"""Heartbeat health distinguishes ready, stale, missing, and malformed state."""

from datetime import UTC, datetime, timedelta

from opticargo_knowledge_graph.health import WorkerHeartbeat, heartbeat_report, write_heartbeat


def test_heartbeat_state_transitions(tmp_path) -> None:
    path = tmp_path / "heartbeat.json"
    assert heartbeat_report(path).status == "missing"
    path.write_text("not-json", encoding="utf-8")
    assert heartbeat_report(path).status == "malformed"

    now = datetime.now(UTC)
    write_heartbeat(
        path,
        WorkerHeartbeat("ready", now, "0.1.0", {"neo4j": "ready"}),
    )
    assert heartbeat_report(path, now=now).status == "ready"
    stale = heartbeat_report(
        path,
        now=now + timedelta(seconds=100),
        max_age_seconds=90,
    )
    assert stale.status == "stale"
