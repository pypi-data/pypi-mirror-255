"""Custom contracts for importlinter."""
import importlib
import itertools
import pathlib
import pkgutil
import sys
import types
from collections.abc import Iterable, Sequence
from dataclasses import dataclass
from importlib.util import find_spec
from typing import cast

import more_itertools
from grimp import DetailedImport, ImportGraph, Layer
from importlinter import Contract, ContractCheck, fields, output
from importlinter.domain.imports import Module
from typing_extensions import LiteralString

from corvic_check.importcontract._common import (
    DetailedChain,
    build_detailed_chain_from_route,
    render_chain_data,
)

# Module names ending in _NAMESPACE_SUFFIX are namespace packages and the
# module name should be interpreted as all sub-modules of the namespace.
_NAMESPACE_SUFFIX: LiteralString = ".*"


def _find_project_root(*, sentinel_file: str = "pyproject.toml") -> pathlib.Path:
    """Return root of a python project.

    Assume the current directory is a descendant of source tree.
    """
    cur = pathlib.Path.cwd()
    fs_root = pathlib.Path(cur.anchor)
    while True:
        sentinel = cur / sentinel_file
        if sentinel.exists():
            return cur
        cur = cur.parent
        if cur == fs_root:
            break
    raise ValueError(f"{sentinel_file} not found inside project root")


def _get_descendants(graph: ImportGraph, modules: list[str]) -> set[str]:
    """Get the modules and descendants of those modules.

    Unlike graph.find_descendants(module), include module in the return value.
    """
    descendants = set(
        more_itertools.flatten([graph.find_descendants(mod) for mod in modules])
    )
    myself = set(modules)
    return descendants.union(myself)


def _iter_namespace(ns_pkg: types.ModuleType):
    # Specifying the second argument (prefix) to iter_modules makes the
    # returned name an absolute name instead of a relative one. This allows
    # import_module to work without having to do additional modification to
    # the name.
    return pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + ".")


def _local_module_names(ns_mod: Module, local_path: pathlib.Path) -> list[str]:
    """Return the sub-modules of a namespace module rooted under the path."""
    ns_pkg = importlib.import_module(ns_mod.name)
    if ns_pkg.__file__:
        raise ValueError(f"{ns_mod} is not a namespace package")

    keep: list[str] = []
    for _finder, name, is_pkg in _iter_namespace(ns_pkg):
        assert (
            is_pkg
        ), "importlinter.root_packages only handles sub-packages of a namespace package"
        spec = find_spec(name)
        if not spec:
            raise ValueError(f"could not find {name}")

        if not (spec.has_location and spec.origin):
            raise NotImplementedError(f"unexpected module format for {name}")
        location = pathlib.Path(spec.origin)
        if location.is_relative_to(local_path):
            keep.append(name)

    return keep


def _local_namespace_path(local_namespace_path: fields.StringField) -> pathlib.Path:
    # Ideally path should be relative to `lint-imports --config=path` but
    # there doesn't seem to be a good way to find this. Instead use the
    # project root.
    project_root = _find_project_root()
    return project_root / str(local_namespace_path)


@dataclass
class _NamespaceModule:
    namespace: Module
    submodules: list[Module]


def _resolve_module(mod: Module, local_path: pathlib.Path) -> Module | _NamespaceModule:
    mod_name = mod.name
    if not mod_name.endswith(_NAMESPACE_SUFFIX):
        return mod
    ns_mod = Module(mod_name[: -len(_NAMESPACE_SUFFIX)])
    return _NamespaceModule(
        namespace=ns_mod,
        submodules=[Module(name) for name in _local_module_names(ns_mod, local_path)],
    )


def _expand_module_as_list(
    module_or_namespace: Module | _NamespaceModule,
) -> list[Module]:
    match module_or_namespace:
        case _NamespaceModule(submodules=submodules):
            return submodules
        case Module() as mod:
            return [mod]


def _expand_possible_namespace_module(
    mod: Module, local_path: pathlib.Path
) -> list[Module]:
    """Expand namespace_module.* into the sub-modules defined in the current project.

    The notation namespace_module.* is nonstandard but allows for natural
    extension of contracts to namespace packages.
    """
    return _expand_module_as_list(_resolve_module(mod, local_path))


def _raise_error_if_not_defined(modules: Iterable[Module], defined_names: set[str]):
    module_names = {mod.name for mod in modules}
    undefined = module_names.difference(defined_names)
    if any(undefined):
        raise ValueError(f"undefined modules: {', '.join(undefined)}")


@dataclass
class _LayerChainData:
    importer: str
    imported: str
    routes: list[DetailedChain]


class NamespaceLayersContract(Contract):
    """Extension of Independence/LayersContract to support namespace packages.

    Both those contracts use graph.find_illegal_dependencies_for_layers under
    the hood.
    """

    independent_modules = fields.ListField(
        subfield=fields.ModuleField(), required=False
    )
    layers = fields.ListField(subfield=fields.ModuleField(), required=False)
    local_namespace_path = fields.StringField(required=False)

    def _check_layers(
        self, graph: ImportGraph, layers: list[list[Module]]
    ) -> list[_LayerChainData]:
        dependencies = graph.find_illegal_dependencies_for_layers(
            layers=[
                Layer(*[mod.name for mod in mods], independent=False) for mods in layers
            ]
        )

        return [
            _LayerChainData(
                imported=dep.imported,
                importer=dep.importer,
                routes=[build_detailed_chain_from_route(r, graph) for r in dep.routes],
            )
            for dep in dependencies
        ]

    def _check_independence(
        self, graph: ImportGraph, independent: Sequence[Module | _NamespaceModule]
    ) -> list[_LayerChainData]:
        # Iff a group of modules A is independent from a module (or group of
        # modules) B, then neither A < B nor B < A, where < is transitively
        # imports.

        def is_namespace(module: Module | _NamespaceModule) -> bool:
            match module:
                case Module():
                    return False
                case _NamespaceModule():
                    return True

        simple_modules, namespace_modules = more_itertools.partition(
            is_namespace, independent
        )

        simple_modules = cast(list[Module], simple_modules)
        namespace_modules = cast(list[_NamespaceModule], namespace_modules)

        group_layers = [
            Layer(
                *[mod.name for mod in ns_mod.submodules],
                ns_mod.namespace.name,
                independent=False,
            )
            for ns_mod in namespace_modules
        ]

        simple_layers = [Layer(mod.name, independent=False) for mod in simple_modules]

        layers = [*group_layers, *simple_layers]

        dependencies_forward = graph.find_illegal_dependencies_for_layers(layers=layers)
        dependencies_reversed = graph.find_illegal_dependencies_for_layers(
            layers=[*reversed(layers)]
        )

        dependencies = [*itertools.chain(dependencies_forward, dependencies_reversed)]

        return [
            _LayerChainData(
                imported=dep.imported,
                importer=dep.importer,
                routes=[build_detailed_chain_from_route(r, graph) for r in dep.routes],
            )
            for dep in dependencies
        ]

    def check(self, graph: ImportGraph, verbose: bool):
        """Check contract."""
        independent_modules = cast(list[Module], self.independent_modules or [])
        layers = cast(list[Module], self.layers or [])

        if not (self.independent_modules or self.layers):
            raise ValueError("independent_modules or layers is required")

        if self.local_namespace_path:
            local_namespace_path = _local_namespace_path(self.local_namespace_path)
            expanded_layer_modules = [
                _expand_possible_namespace_module(mod, local_namespace_path)
                for mod in layers
            ]
            resolved_independent_modules = [
                _resolve_module(mod, local_namespace_path)
                for mod in independent_modules
            ]
            expanded_independent_modules = [
                _expand_module_as_list(mod) for mod in resolved_independent_modules
            ]
        else:
            expanded_layer_modules = [[mod] for mod in layers]
            resolved_independent_modules = independent_modules
            expanded_independent_modules = [[mod] for mod in independent_modules]

        _raise_error_if_not_defined(
            more_itertools.flatten(expanded_layer_modules), graph.modules
        )
        _raise_error_if_not_defined(
            more_itertools.flatten(expanded_independent_modules), graph.modules
        )

        layer_violation_chains = self._check_layers(graph, expanded_layer_modules)
        independence_violation_chains = self._check_independence(
            graph, resolved_independent_modules
        )

        violation_chains = [*layer_violation_chains, *independence_violation_chains]
        return ContractCheck(
            kept=not any(violation_chains),
            metadata={
                "violation_chains": violation_chains,
            },
        )

    def render_broken_contract(self, check: ContractCheck):
        """Print contract violations."""
        for chains_data in cast(
            list[_LayerChainData], check.metadata["violation_chains"]
        ):
            higher_layer, lower_layer = (chains_data.imported, chains_data.importer)
            output.print(f"{lower_layer} is not allowed to import {higher_layer}:")
            output.new_line()

            for chain_data in chains_data.routes:
                render_chain_data(chain_data)
                output.new_line()

            output.new_line()


class CompletePortionContract(Contract):
    """Check that packages in a local namespace directory are in the import graph.

    importlinter expects portions of a namespace package (i.e., sub-modules of
    a namespace package) to be individually listed in
    [tool.importlinter.root_packages] for them to be considered in import graph
    analysis. This contract verifies that this root_packages is complete with
    respect to the sub-modules rooted in the current project.
    """

    namespace_package = fields.ModuleField(required=True)
    local_namespace_path = fields.StringField(required=True)

    def check(self, graph: ImportGraph, verbose: bool):
        """Check contract."""
        local_namespace_path = _local_namespace_path(self.local_namespace_path)
        namespace_package = cast(Module, self.namespace_package)
        all_modules = [Module(name) for name in graph.modules]
        all_children = [
            mod.name for mod in all_modules if mod.is_in_package(namespace_package)
        ]

        local_module_names = set(
            _local_module_names(namespace_package, local_namespace_path)
        )

        orphans = local_module_names.difference(all_children)
        broken = any(orphans)
        return ContractCheck(
            kept=not broken, metadata={"module_violations": list(orphans)}
        )

    def render_broken_contract(self, check: ContractCheck):
        """Print contract violations."""
        for mod in check.metadata["module_violations"]:
            output.print_error(
                f"{mod} in {self.local_namespace_path} "
                + "but not found in [tool.importlinter.root_packages]",
                bold=True,
            )


class SafeNameContract(Contract):
    """Check that module names do not shadow stdlib module names.

    Python adds the current directory to the module search path by default and
    the search path applies to all imports. This means that a module sharing
    the name of a common module, e.g., typing.py, in the working directory
    overrides the well-known module in all import statements. This can lead to
    cryptic error messages.

    While this applies to any dependency not just the Python standard library,
    the likelihood of collisions is much higher with stdlib names, so it is
    best to avoid using them at all.
    """

    modules = fields.ListField(subfield=fields.ModuleField(), required=True)
    exclude_modules = fields.ListField(subfield=fields.ModuleField(), required=False)
    local_namespace_path = fields.StringField(required=False)

    def check(self, graph: ImportGraph, verbose: bool):
        """Check contract."""
        modules = cast(list[Module], self.modules or [])
        exclude_modules = cast(list[Module], self.exclude_modules or [])

        _raise_error_if_not_defined(exclude_modules, graph.modules)

        if self.local_namespace_path:
            local_namespace_path = _local_namespace_path(self.local_namespace_path)
            modules = list(
                more_itertools.flatten(
                    _expand_possible_namespace_module(mod, local_namespace_path)
                    for mod in modules
                )
            )

        universe = _get_descendants(graph, [mod.name for mod in modules])

        exclude_module_names = {mod.name for mod in exclude_modules}
        if exclude_modules:
            output.verbose_print(
                verbose, f'excluding modules: {" ".join(exclude_module_names)}'
            )

        module_violations: list[str] = []
        for mod in universe:
            if mod in exclude_module_names:
                continue
            parts = mod.split(".")
            if parts[-1] not in sys.stdlib_module_names:
                continue
            module_violations.append(mod)

        return ContractCheck(
            kept=not module_violations,
            metadata={
                "module_violations": module_violations,
            },
        )

    def render_broken_contract(self, check: ContractCheck):
        """Print contract violations."""
        for mod in check.metadata["module_violations"]:
            output.print_error(
                f"{mod} shadows a standard library module of the same name",
                bold=True,
            )


class TShapedContract(Contract):
    """T-shaped imports contract.

    Ensure that imports are T-shaped among the first level of child modules of
    a root module.

    That is, the direct children (root.a, root.b, ...) of the root module may
    import each other, but none of them should import each others descendants,
    e.g., root.a should not import root.b.c.

    For root.a to be T-shaped means satisfying two constraints: (1) all
    importers of root.a only import root.a and no descendants of root.a, and
    (2) root.a does not import any descendants of other modules.

    Accordingly, there are two ways a module can be partially T-shaped: (1) it
    allows other modules to import its descendants, or (2) its descendants
    import others descendants.

    If a module is only partially T-shaped, use the configuration option
    exclude_imports_of to indicate that other modules may import descendants of
    the module (constraint 1 is not satisfied) and use the configuration option
    exclude_imports_from to indicate that descendants of the module import
    descendants of others (constraint 2 is not satisfied).
    """

    root = fields.ModuleField()
    exclude_imports_of = fields.ListField(subfield=fields.ModuleField(), required=False)
    exclude_imports_from = fields.ListField(
        subfield=fields.ModuleField(), required=False
    )
    local_namespace_path = fields.StringField(required=False)

    def check(self, graph: ImportGraph, verbose: bool):
        """Check contract."""
        root = cast(Module, self.root)
        exclude_imports_of = cast(list[Module], self.exclude_imports_of or [])
        exclude_imports_from = cast(list[Module], self.exclude_imports_from or [])
        exclude_imports_from = cast(list[Module], self.exclude_imports_from or [])

        _raise_error_if_not_defined(exclude_imports_of, graph.modules)
        _raise_error_if_not_defined(exclude_imports_from, graph.modules)

        if self.local_namespace_path:
            local_namespace_path = _local_namespace_path(self.local_namespace_path)
            roots = _expand_possible_namespace_module(root, local_namespace_path)
            siblings = {mod.name for mod in roots}
            universe = _get_descendants(graph, list(siblings))
        else:
            root_name = root.name
            siblings = graph.find_children(root_name)
            universe = _get_descendants(graph, [root_name])

        module_tree: dict[str, set[str]] = {
            sib: graph.find_descendants(sib) for sib in siblings
        }

        exclude_imports_of = _get_descendants(
            graph, [mod.name for mod in exclude_imports_of]
        )
        exclude_imports_from = _get_descendants(
            graph, [mod.name for mod in exclude_imports_from]
        )

        import_violations: list[DetailedImport] = []
        for descendants in module_tree.values():
            for desc in descendants:
                for dep in graph.find_modules_directly_imported_by(desc):
                    if dep not in universe:
                        continue
                    if dep in descendants:
                        continue
                    if dep in module_tree:
                        continue
                    if dep in exclude_imports_of:
                        continue
                    if desc in exclude_imports_from:
                        continue
                    details = graph.get_import_details(importer=desc, imported=dep)
                    if not details:
                        # Create empty metadata when import exists but no
                        # details are known
                        details = [
                            DetailedImport(
                                importer=desc,
                                imported=dep,
                                line_contents="<unknown>",
                                line_number=0,
                            )
                        ]
                    import_violations.extend(details)

        return ContractCheck(
            kept=not import_violations,
            metadata={
                "import_violations": import_violations,
            },
        )

    def render_broken_contract(self, check: ContractCheck):
        """Print contract violations."""
        for detail in check.metadata["import_violations"]:
            importer = detail["importer"]
            imported = detail["imported"]
            line_number = detail["line_number"]
            line_contents = detail["line_contents"]

            output.print_error(
                f"{importer} is not allowed to import {imported}:",
                bold=True,
            )
            output.indent_cursor()
            output.print_error(f"{importer}:{line_number}: {line_contents}")
