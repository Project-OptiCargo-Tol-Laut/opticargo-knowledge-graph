"""KG is an internal package/worker/job and must not expose public ingress."""

from tests.helpers import REPOSITORY_ROOT, SOURCE_ROOT


def test_source_and_dependencies_have_no_public_web_framework() -> None:
    forbidden = {"fastapi", "flask", "django", "uvicorn", "gunicorn"}
    source = "\n".join(path.read_text(encoding="utf-8") for path in SOURCE_ROOT.rglob("*.py"))
    pyproject = (REPOSITORY_ROOT / "pyproject.toml").read_text(encoding="utf-8").casefold()

    assert not any(f"import {name}" in source.casefold() for name in forbidden)
    assert not any(name in pyproject for name in forbidden)


def test_docker_artifact_starts_worker_not_http_api() -> None:
    dockerfile = (REPOSITORY_ROOT / "Dockerfile").read_text(encoding="utf-8")
    assert "opticargo_knowledge_graph.worker" in dockerfile
    assert "EXPOSE 80" not in dockerfile
