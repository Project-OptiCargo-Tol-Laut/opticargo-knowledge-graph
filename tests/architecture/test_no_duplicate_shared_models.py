"""Stable Shared models are not redefined by the Knowledge Graph package."""

import ast

from tests.helpers import SOURCE_ROOT

SHARED_MODEL_NAMES = {"Citation", "RetrievedChunk", "CargoScoringRequest"}


def test_knowledge_graph_does_not_redefine_shared_models() -> None:
    definitions: set[str] = set()
    for path in SOURCE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        definitions.update(node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    assert definitions.isdisjoint(SHARED_MODEL_NAMES)


def test_graph_context_models_have_one_knowledge_graph_owner() -> None:
    graph_models = SOURCE_ROOT / "graph_models.py"
    assert graph_models.is_file()
    for path in SOURCE_ROOT.rglob("*.py"):
        if path == graph_models:
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"))
        definitions = {
            node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)
        }
        assert "GraphContext" not in definitions
