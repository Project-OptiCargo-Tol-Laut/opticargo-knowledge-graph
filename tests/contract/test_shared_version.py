"""KG consumes the exact agreed opticargo-shared contract version."""

from importlib.metadata import version

from tests.helpers import REPOSITORY_ROOT


def test_installed_and_declared_shared_versions_are_compatible() -> None:
    assert version("opticargo-shared") == "1.0.0"
    pyproject = (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert '"opticargo-shared==1.0.0"' in pyproject
