"""Shared remains stable while KG exposes its domain-specific graph contracts."""

from importlib.metadata import files, version

from opticargo_knowledge_graph.graph_models import GraphBackhaulCandidate, GraphContext


def test_shared_distribution_version_and_kg_contract_imports() -> None:
    assert version("opticargo-shared") == "1.0.0"
    assert GraphContext.__name__ == "GraphContext"
    assert GraphBackhaulCandidate.__name__ == "GraphBackhaulCandidate"
    installed_files = files("opticargo-shared")
    assert installed_files is not None and any(path.name == "METADATA" for path in installed_files)
