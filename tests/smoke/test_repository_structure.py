"""Clean-checkout structure contains implemented tests, workflows, and no vendored wheel."""

from tests.helpers import REPOSITORY_ROOT


def test_repository_structure_has_no_python_placeholders_or_wheels() -> None:
    areas = (
        REPOSITORY_ROOT / "src",
        REPOSITORY_ROOT / "scripts",
        REPOSITORY_ROOT / "tests",
    )
    empty_python = [
        path for area in areas for path in area.rglob("*.py") if path.stat().st_size == 0
    ]
    assert empty_python == []
    assert (REPOSITORY_ROOT / ".github/workflows/ci.yml").is_file()
    assert (REPOSITORY_ROOT / ".github/workflows/integration.yml").is_file()
    assert list(REPOSITORY_ROOT.rglob("*.whl")) == []


def test_every_test_layer_has_documented_responsibility() -> None:
    layers = (
        "architecture",
        "contract",
        "unit",
        "smoke",
        "integration",
        "e2e",
        "resilience",
        "evaluation",
        "performance",
        "security",
    )
    assert all((REPOSITORY_ROOT / "tests" / layer / "README.md").is_file() for layer in layers)
