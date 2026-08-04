from opticargo_knowledge_graph.worker import reclaim_pending


class Redis:
    def xautoclaim(self, stream, group, consumer, idle, start, count):
        assert idle == 60_000
        return ("0-0", [("1-0", {"event": "{}"})], [])


def test_pending_entries_are_reclaimed_from_failed_consumers() -> None:
    entries = reclaim_pending(
        Redis(),
        stream="events",
        group="graph",
        consumer="worker-2",
        min_idle_ms=60_000,
        count=10,
    )
    assert entries == [("1-0", {"event": "{}"})]
