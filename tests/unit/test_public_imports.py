"""Package import is side-effect free and versioned."""

import opticargo_knowledge_graph


def test_root_package_has_a_minimal_stable_public_surface() -> None:
    assert opticargo_knowledge_graph.__all__ == ["__version__"]
    assert opticargo_knowledge_graph.__version__ == "1.0.0"
