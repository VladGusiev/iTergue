"""The import graph is the architecture. These tests are what enforce it."""

import ast
from pathlib import Path

import pytest

PACKAGE = Path(__file__).parent.parent / "src" / "itergue"
# The vocabulary the rest of the game is written in. `combat` used to be here and
# left deliberately in Lesson 22: a Combatant stands somewhere, so it needs Point.
# The rule is the direction of the import, not the count of modules with none.
LEAVES = {"geometry", "messages", "tiles"}


def imports() -> dict[str, set[str]]:
    """Every module in the package, mapped to the package modules it imports."""
    graph = {}
    for path in PACKAGE.glob("*.py"):
        found = {
            node.module.split(".")[-1]
            for node in ast.walk(ast.parse(path.read_text()))
            if isinstance(node, ast.ImportFrom)
            and node.module
            and node.module.startswith("itergue")
        }
        graph[path.stem] = found - {path.stem}
    return graph


def test_the_package_has_no_import_cycles():
    # A cycle is the failure that has no good fix once it exists: every module in
    # the loop has to be untangled at once. Catch it on the commit that adds it.
    graph = imports()
    seen: set[str] = set()

    def walk(module: str, path: tuple[str, ...]) -> None:
        if module in path:
            pytest.fail(f"import cycle: {' -> '.join([*path, module])}")
        if module in seen:
            return
        seen.add(module)
        for dependency in sorted(graph.get(module, ())):
            walk(dependency, (*path, module))

    for module in sorted(graph):
        walk(module, ())


def test_the_leaves_stay_leaves():
    # These define the vocabulary everything else is written in. The day one
    # of them imports upward, the layering is gone and nothing else here can tell.
    graph = imports()
    for leaf in LEAVES:
        assert graph[leaf] == set(), f"{leaf} should depend on nothing in the package"


def test_only_the_entry_point_depends_on_main():
    # main wires the program together, so importing it from anywhere else means
    # the wiring has leaked into the parts being wired.
    importers = {name for name, deps in imports().items() if "main" in deps}
    assert importers == {"__main__"}
