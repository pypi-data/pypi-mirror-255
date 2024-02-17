"""Build tool CLI."""
import os
import pathlib
import subprocess
import sys
import webbrowser

import click


class CommandError(Exception):
    """A check command failed."""

    def __init__(self):
        """Create a command error.

        The sub-command writes error details to the console. So this class
        doesn't need to capture them too.
        """


class CheckError(Exception):
    """A general check error."""

    def __init__(self, message: str):
        """Create a general check error."""
        super().__init__(message)


class Profile:
    """Rust build profiles."""

    OPT_DEV = "opt-dev"
    DEBUG_RELEASE = "debug-release"

    # Work around absence of enum.StrEnum in Python < 3.11. Post 3.11 make
    # Profile a StrEnum and replace uses of values with list(Profile).
    @classmethod
    def values(cls) -> list[str]:
        """Return valid profile values."""
        return [cls.OPT_DEV, cls.DEBUG_RELEASE]


def _project_root(*, outside_project_root: bool = False) -> pathlib.Path:
    """Return the path to the project root."""
    if outside_project_root:
        raise CheckError("must be run within corvic-engine")
    cur = pathlib.Path.cwd()
    fs_root = pathlib.Path(cur.anchor)
    while True:
        # Pick an sentinel file that should be present even in "chroot"
        # scenarios like a docker container (c.f. .git/ which is often excluded
        # from container file systems).
        sentinel = cur / "poetry.lock"
        if sentinel.exists():
            return cur
        cur = cur.parent
        if cur == fs_root:
            break
    raise CheckError("poetry.lock not found inside project root")


def _parse_env_bool(value: str) -> bool:
    value = value.lower().strip()

    if len(value) == 0:
        return False

    match value:
        case "true" | "1":
            return True
        case "false" | "0":
            return False
        case _:
            return True


@click.group()
def cli():
    """Build tool."""


@cli.command()
@click.option(
    "--profile", type=click.Choice(Profile.values()), default=Profile.DEBUG_RELEASE
)
@click.option(
    "--default-features/--no-default-features", default=True, show_default=True
)
@click.option("--release/--no-release", default=False, show_default=True)
def build(profile: str, default_features: bool, release: bool):
    """Make build artifacts suitable for separate installation."""
    extra: list[str] = []
    if not default_features:
        extra.append("--no-default-features")
    if release:
        extra.append("--release")
    subprocess.check_call(["maturin", "build", "--profile", profile, *extra])


@cli.command()
@click.option("--profile", type=click.Choice(Profile.values()), default=Profile.OPT_DEV)
@click.option(
    "--default-features/--no-default-features", default=True, show_default=True
)
def dev(profile: str, default_features: bool):
    """Make build artifacts and install them into the local environment."""
    # We use [tools.poetry.scripts] to install developer tooling and maturin
    # reads [project.scripts] which is empty. Thus, the default behavior of
    # `maturin develop` to install the package will wipe the poetry installed
    # scripts.
    extra = ["--skip-install"]
    if not default_features:
        extra.append("--no-default-features")
    # Change directory to project root otherwise wrong Cargo.toml could be used
    subprocess.check_call(
        ["maturin", "develop", "--profile", profile, *extra],
        cwd=_project_root(),
    )


@cli.command()
@click.argument(
    "path",
    type=click.Path(path_type=pathlib.Path, exists=True),
    default=None,
    required=False,
)
def format(path: pathlib.Path | None):
    """Format code and files."""
    cwd = path if path else _project_root()

    codes: list[int] = []
    codes.append(subprocess.call(["ruff", "format", "--silent"], cwd=cwd))
    codes.append(subprocess.call(["cargo", "fmt", "--all"], cwd=cwd))
    codes.append(subprocess.call(["dprint", "fmt", "--allow-no-files"], cwd=cwd))
    codes.append(
        subprocess.call(["ruff", "check", "--fix", "--exit-zero", "--silent"], cwd=cwd)
    )

    if any(codes):
        raise CommandError()


@cli.command()
@click.argument(
    "path",
    type=click.Path(path_type=pathlib.Path, exists=True),
    default=None,
    required=False,
)
@click.option(
    "--ci/--no-ci",
    default=_parse_env_bool(os.getenv("CI", "0")),
    show_default=True,
    help="If true, avoid non-determinisic checks. Default: os.environ['CI']",
)
def lint(path: pathlib.Path | None, ci: bool):
    """Lint code and files."""
    cwd = path if path else _project_root()

    codes: list[int] = []
    codes.append(subprocess.call(["ruff", "format", "--check"], cwd=cwd))
    codes.append(subprocess.call(["cargo", "fmt", "--check", "--all"], cwd=cwd))
    codes.append(subprocess.call(["dprint", "check"], cwd=cwd))
    codes.append(
        subprocess.call(
            ["lint-imports", "--config", _project_root() / "pyproject.toml"]
        )
    )
    codes.append(subprocess.call(["ruff", "check", "."], cwd=cwd))

    cargo_deny_check_args = ["bans", "licenses", "sources"]
    if not ci:
        cargo_deny_check_args += ["advisories"]

    # Change directory to project root otherwise wrong Cargo.toml could be used
    codes.append(
        subprocess.call(
            ["cargo", "deny", "check", *cargo_deny_check_args],
            cwd=_project_root(),
        )
    )

    codes.append(subprocess.call(["codespell", "."], cwd=cwd))
    codes.append(
        subprocess.call(
            [
                "cargo",
                "clippy",
                "--workspace",
                "--all-targets",
                "--all-features",
                "--locked",
                "--",
                "-D",
                "warnings",
            ],
            cwd=cwd,
        )
    )
    codes.append(subprocess.check_call(["pyright"], cwd=cwd))
    if any(codes):
        raise CommandError()


@cli.command()
@click.option(
    "--open/--no-open",
    help="Open generated docs in browser",
    default=True,
    show_default=True,
)
@click.argument("other_sphinx_arguments", nargs=-1, type=click.UNPROCESSED)
def docs(open: bool, other_sphinx_arguments: list[str]):
    """Generate docs."""
    docs_dir = _project_root() / "docs"
    subprocess.check_call(
        [
            "sphinx-build",
            "-M",
            "html",
            "source",
            "build",
            "-W",
            *other_sphinx_arguments,
        ],
        cwd=docs_dir,
    )
    if open:
        doc_index = docs_dir / "build" / "html" / "index.html"
        url = f"file://{doc_index!s}"
        webbrowser.open(url)


@cli.command()
def test():
    """Run tests."""
    subprocess.check_call(["pytest"])
    subprocess.check_call(["cargo", "test"])


def main():
    """Build tool CLI."""
    try:
        cli.main(prog_name="check")
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
    except CommandError:
        sys.exit(1)
    except CheckError as exc:
        sys.stderr.write(str(exc))
        sys.stderr.write("\n")
        sys.exit(1)
