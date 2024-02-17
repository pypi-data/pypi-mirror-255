#!/usr/bin/env python
"""Minimal dependency license checker.

This is explicitly not part of corvic_check because dev dependencies are not
part of the product directly and have fewer restrictions on licensing (e.g.,
may contain more copyleft licensed software).
"""
import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from typing import Any

# List of well-known safe licenses
ALLOW_LIST = [
    "3-Clause BSD License",
    "Apache 2.0",
    "Apache License v2.0",
    "Apache License, Version 2.0",
    "Apache Software License",
    "Apache Software License; BSD License",
    "Apache Software License; MIT License",
    "Apache-2.0",
    "BSD License",
    "BSD",
    "FreeBSD",
    "GNU Lesser General Public License v2 (LGPLv2)",
    "MIT License",
    "MIT License; Mozilla Public License 2.0 (MPL 2.0)",
    "MIT No Attribution License (MIT-0)",
    "MIT licensed, as found in the LICENSE file",
    "MIT",
    "Mozilla Public License 2.0 (MPL 2.0)",
    "Python Software Foundation License",
    "The Unlicense (Unlicense)",
]


class Version:
    """A version."""

    major: int
    minor: int
    patch: int
    unparsed: str | None

    def __init__(
        self,
        major: int,
        minor: int,
        patch: int,
        unparsed: str | None = None,
    ) -> None:
        """Create a version."""
        self.major = major
        self.minor = minor
        self.patch = patch
        self.unparsed = unparsed

    def less_than(self, other: "Version") -> bool:
        """Returns true if this version is less than another version."""
        return (self.major, self.minor, self.patch) < (
            other.major,
            other.minor,
            other.patch,
        )


def parse_version(semver: str) -> Version:
    """Parse a version string into a Version."""
    major, minor, patchish = semver.split(".", maxsplit=2)
    m = re.match(r"(\d+)(.*)?", patchish)
    patch = 0
    if m and m.group(1):
        patch = int(m.group(1))
    unparsed = None
    if m and m.group(2):
        unparsed = m.group(2)
    return Version(int(major), int(minor), int(patch), unparsed)


@dataclass
class Exemption:
    """A manual exemption to the general license allow list."""

    expected_license: str
    less_than: Version | None


MANUAL_EXCLUSIONS = {
    # 🐦
    "corvic-engine": Exemption("UNKNOWN", None),
    # Per https://github.com/python-pillow/Pillow/issues/5975, this is a
    # trivial variant of MIT but there is no plan to update for clarity.
    "pillow": Exemption("Historical Permission Notice and Disclaimer (HPND)", None),
    "chardet": Exemption(
        "GNU Lesser General Public License v2 or later (LGPLv2+)",
        parse_version("6.0.0"),
    ),
    "pypdfium2": Exemption(
        "(Apache-2.0 OR BSD-3-Clause) AND LicenseRef-PdfiumThirdParty",
        parse_version("5.0.0"),
    ),
    # This is a short identifier for the 'GNU Lesser General Public License
    # v2.1' only license used by gensim library. It is okay to use as it is not
    # statically linked to anything.
    "gensim": Exemption(
        "LGPL-2.1-only",
        parse_version("5.0.0"),
    ),
}


class LicenseError(Exception):
    """An error raised when checking licenses."""

    message: str

    def __init__(self, message: str) -> None:
        """Create a LicenseError."""
        self.message = message


@dataclass(init=False)
class Dep:
    """A package dependency."""

    name: str
    description: str
    license: str
    license_text: str
    notice_text: str
    version: str
    url: str

    def __init__(self, data_dict: dict[str, Any]) -> None:
        """Create a package dependency."""
        self.name = data_dict["Name"]
        self.description = data_dict["Description"]
        self.license = data_dict["License"]
        self.license_text = data_dict["LicenseText"]
        self.notice_text = data_dict["NoticeText"]
        self.version = data_dict["Version"]
        self.url = data_dict["URL"]


def sync_environment():
    """Update environment to match default installed dependencies."""
    subprocess.check_call(
        [
            "poetry",
            "install",
            "--without=dev",
            "--without=docs",
            "--with=check-license",
            "--sync",
        ],
    )


def run_report(_args: argparse.Namespace):
    """Print raw output of pip-license."""
    subprocess.check_call(["pip-licenses", "--with-urls", "--format=csv"])


def _license_okay(dep: Dep) -> bool:
    if dep.license in ALLOW_LIST:
        return True
    exclusion = MANUAL_EXCLUSIONS.get(dep.name, None)
    if not exclusion:
        return False
    if dep.license != exclusion.expected_license:
        return False
    if not exclusion.less_than:
        return True

    dep_ver = parse_version(dep.version)
    return dep_ver.less_than(exclusion.less_than)


def run_check(args: argparse.Namespace):
    """Check if any licenses in the environment are non-compliant."""
    dep_objs = json.loads(
        subprocess.check_output(
            [
                "pip-licenses",
                "--with-urls",
                "--with-description",
                "--with-license-file",
                "--with-notice-file",
                "--format=json",
            ],
        ),
    )
    deps = [Dep(obj) for obj in dep_objs]
    not_okay_deps = [dep for dep in deps if not _license_okay(dep)]

    if not not_okay_deps:
        print("licenses of dependencies are okay")
        return

    for dep in not_okay_deps:
        if args.verbose:
            print("---")
            print(f"name: {dep.name}")
            print(f"license: {dep.license}")
            print(f"description: {dep.description}")
            print(f"notice_text:\n\n{dep.notice_text}\n")
            print(f"license_text:\n\n{dep.license_text}\n")
        else:
            print(f"{dep.name}\t{dep.version}\t{dep.license}")

    raise LicenseError(
        "some dependencies have unknown licenses; see output for details"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Check licenses.")
    parser.add_argument(
        "--sync",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Synchronize current (virtual) environment with poetry lockfile",
    )
    subparsers = parser.add_subparsers(required=True)

    parser_report = subparsers.add_parser("report")
    parser_report.set_defaults(func=run_report)

    parser_check = subparsers.add_parser("check")
    parser_check.add_argument("--verbose", action="store_true")
    parser_check.set_defaults(func=run_check)

    parser_args = parser.parse_args()

    try:
        if parser_args.sync:
            sync_environment()
        parser_args.func(parser_args)
    except LicenseError as exc:
        sys.stderr.write(exc.message)
        sys.stderr.write("\n")
        sys.exit(1)
