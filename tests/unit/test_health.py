from opticargo_knowledge_graph.health import liveness_report, readiness_report


def test_health_reports_are_ready_without_required_driver() -> None:
    assert liveness_report()["status"] == "alive"
    assert readiness_report().status == "ready"
