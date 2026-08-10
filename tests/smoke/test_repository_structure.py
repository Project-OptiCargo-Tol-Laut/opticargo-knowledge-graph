"""Clean-checkout structure contains implemented tests, workflows, and release inputs."""

from tests.helpers import REPOSITORY_ROOT


def test_repository_structure_has_no_python_placeholders_and_expected_wheel_locations() -> None:
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

    # vendor/ contains intentional internal release inputs for repo-local Docker
    # builds. dist/ is a legitimate local build output and must not make the test
    # order-dependent. Wheels anywhere else are unexpected.
    wheels = list(REPOSITORY_ROOT.rglob("*.whl"))
    unexpected = [
        path for path in wheels
        if path.relative_to(REPOSITORY_ROOT).parts[0] not in {"vendor", "dist"}
    ]
    assert unexpected == []
    assert (
        REPOSITORY_ROOT / "vendor" / "opticargo_shared-1.0.0-py3-none-any.whl"
    ).is_file()


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
