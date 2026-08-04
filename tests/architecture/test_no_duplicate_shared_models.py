"""Cross-repository graph contracts must come from opticargo-shared."""

import ast

from tests.helpers import SOURCE_ROOT

SHARED_MODEL_NAMES = {
    "GraphContext",
    "GraphBackhaulCandidate",
    "PortContext",
    "VoyageLegContext",
    "ShipCapacityContext",
    "SupplierContext",
}


def test_knowledge_graph_does_not_redefine_shared_models() -> None:
    definitions: set[str] = set()
    for path in SOURCE_ROOT.rglob("*.py"):
        tree = ast.parse(path.read_text(encoding="utf-8"))
        definitions.update(node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
    assert definitions.isdisjoint(SHARED_MODEL_NAMES)
