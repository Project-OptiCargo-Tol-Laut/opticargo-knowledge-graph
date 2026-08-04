"""Domain/query modules must not depend on CLI, worker, or consumer repositories."""

import ast

from tests.helpers import SOURCE_ROOT


def test_domain_packages_have_inward_dependency_direction() -> None:
    forbidden = (
        "opticargo_knowledge_graph.cli",
        "opticargo_knowledge_graph.worker",
        "opticargo_agents",
        "opticargo_rag_pipeline",
    )
    violations: list[str] = []
    for area in (SOURCE_ROOT / "queries", SOURCE_ROOT / "projections", SOURCE_ROOT / "schema"):
        for path in area.rglob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            imports = [
                node.module or ""
                for node in ast.walk(tree)
                if isinstance(node, ast.ImportFrom)
            ]
            imports.extend(
                alias.name
                for node in ast.walk(tree)
                if isinstance(node, ast.Import)
                for alias in node.names
            )
            if any(name.startswith(forbidden) for name in imports):
                violations.append(str(path.relative_to(SOURCE_ROOT)))
    assert violations == []
