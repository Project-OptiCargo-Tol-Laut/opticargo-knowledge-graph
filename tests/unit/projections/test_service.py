from datetime import UTC, datetime

from opticargo_knowledge_graph.contracts import EntityChangedEvent
from opticargo_knowledge_graph.projections.registry import ProjectionRegistry
from opticargo_knowledge_graph.projections.service import ProjectionService


class Result:
    def __init__(self, single=None):
        self.value = single

    def single(self):
        return self.value

    def consume(self):
        return None


class Transaction:
    def __init__(self, duplicate=False):
        self.duplicate = duplicate
        self.queries = []

    def run(self, query, **parameters):
        self.queries.append((query, parameters))
        if "MATCH (e:_ProjectionEvent" in query:
            return Result({"id": parameters["event_id"]} if self.duplicate else None)
        return Result()


class Session:
    def __init__(self, transaction):
        self.transaction = transaction

    def execute_write(self, callback, *args):
        return callback(self.transaction, *args)

    def run(self, query, **parameters):
        return self.transaction.run(query, **parameters)


class Source:
    def fetch(self, entity_type, entity_id):
        return {"id": entity_id, "name": "Ambon"}


def event() -> EntityChangedEvent:
    return EntityChangedEvent(
        "evt-1", "Port", "port-1", "updated", {"name": "Ambon"}, datetime.now(UTC)
    )


def test_projection_and_event_marker_share_one_transaction() -> None:
    calls = []

    def handler(transaction, record, operation):
        calls.append((transaction, record, operation))

    registry = ProjectionRegistry()
    registry.register("port", handler)
    transaction = Transaction()

    result = ProjectionService(registry, Source()).project(Session(transaction), event())

    assert result.status == "projected"
    assert calls[0][1]["id"] == "port-1"
    assert any("CREATE (e:_ProjectionEvent" in query for query, _ in transaction.queries)


def test_duplicate_event_does_not_execute_builder() -> None:
    calls = []

    def handler(transaction, record, operation):
        calls.append(record)

    registry = ProjectionRegistry()
    registry.register("port", handler)

    result = ProjectionService(registry, Source()).project(
        Session(Transaction(duplicate=True)), event()
    )

    assert result.status == "duplicate"
    assert calls == []


def test_unknown_entity_is_skipped_without_session_access() -> None:
    unknown = EntityChangedEvent("evt", "unknown", "id", "updated")
    assert ProjectionService(ProjectionRegistry()).project(None, unknown).status == "skipped"
