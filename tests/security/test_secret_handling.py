"""Diagnostics expose error classes and endpoint roles, never credential values."""

import json

from opticargo_knowledge_graph.cli import doctor


class FailingDriver:
    def verify_connectivity(self):
        raise RuntimeError("bolt://neo4j:super-secret@graph:7687")

    def close(self):
        return None


def test_doctor_sanitizes_dependency_failure(monkeypatch, capsys) -> None:
    monkeypatch.setattr(doctor, "build_driver_from_env", FailingDriver)
    assert doctor.main() == 1
    output = capsys.readouterr().out
    assert "super-secret" not in output
    assert json.loads(output)["readiness"]["detail"] == "RuntimeError"
