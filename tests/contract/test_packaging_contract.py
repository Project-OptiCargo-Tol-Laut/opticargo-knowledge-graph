"""Wheel configuration includes typed marker and versioned Cypher resources."""

from importlib.resources import files

from tests.helpers import REPOSITORY_ROOT


def test_package_data_and_resources_are_declared() -> None:
    pyproject = (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    package = files("opticargo_knowledge_graph")
    assert '"py.typed"' in pyproject
    assert '"schema/**/*.cypher"' in pyproject
    assert package.joinpath("py.typed").is_file()
    migration_names = [item.name for item in package.joinpath("schema/migrations").iterdir()]
    assert "006_canonical_labels.cypher" in migration_names
