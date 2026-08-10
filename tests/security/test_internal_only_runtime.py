"""Runtime artifact is internal-only and has no public HTTP application."""

from tests.helpers import REPOSITORY_ROOT, SOURCE_ROOT


def test_runtime_has_worker_job_commands_without_public_ingress() -> None:
    source = "\n".join(path.read_text(encoding="utf-8") for path in SOURCE_ROOT.rglob("*.py"))
    compose = (REPOSITORY_ROOT / "compose.graph.yml").read_text(encoding="utf-8")
    assert "FastAPI(" not in source
    assert "@app." not in source
    assert "opticargo_knowledge_graph.worker" in compose
    assert "ports:" not in compose
