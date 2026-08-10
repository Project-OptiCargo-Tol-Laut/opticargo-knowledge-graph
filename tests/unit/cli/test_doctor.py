"""Doctor reports readiness, closes dependencies, and never prints credentials."""

import json

from opticargo_knowledge_graph.cli import doctor


class Driver:
    def __init__(self, *, failure: bool = False) -> None:
        self.failure = failure
        self.closed = False

    def verify_connectivity(self) -> None:
        if self.failure:
            raise RuntimeError("bolt://neo4j:secret@graph")

    def close(self) -> None:
        self.closed = True


def test_doctor_ready_and_degraded_are_machine_readable(monkeypatch, capsys) -> None:
    ready_driver = Driver()
    monkeypatch.setattr(doctor, "build_driver_from_env", lambda: ready_driver)
    assert doctor.main() == 0
    ready = json.loads(capsys.readouterr().out)
    assert ready["readiness"]["status"] == "ready"
    assert ready_driver.closed

    failed_driver = Driver(failure=True)
    monkeypatch.setattr(doctor, "build_driver_from_env", lambda: failed_driver)
    assert doctor.main() == 1
    output = capsys.readouterr().out
    assert "secret" not in output
    assert json.loads(output)["readiness"]["status"] == "degraded"
