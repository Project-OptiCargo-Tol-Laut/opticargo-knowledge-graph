"""Duplicate event IDs cannot execute a projection handler twice."""

from datetime import UTC, datetime

from opticargo_knowledge_graph.contracts import EntityChangedEvent
from opticargo_knowledge_graph.projections import ProjectionRegistry, ProjectionService


class Result:
    def __init__(self, value=None):
        self.value = value

    def single(self):
        return self.value

    def consume(self):
        return self


class Session:
    def __init__(self):
        self.events = set()

    def run(self, query, **parameters):
        if "MATCH (e:_ProjectionEvent" in str(query):
            value = (
                {"id": parameters["event_id"]}
                if parameters["event_id"] in self.events
                else None
            )
            return Result(value)
        return Result()

    def execute_write(self, callback):
        session = self

        class Transaction:
            def run(self, query, **parameters):
                if "MATCH (e:_ProjectionEvent" in str(query):
                    value = (
                        {"id": parameters["event_id"]}
                        if parameters["event_id"] in session.events
                        else None
                    )
                    return Result(value)
                if "CREATE (e:_ProjectionEvent" in str(query):
                    session.events.add(parameters["event_id"])
                return Result()

        return callback(Transaction())


def test_duplicate_event_has_one_side_effect_and_one_marker() -> None:
    calls = []
    registry = ProjectionRegistry()
    registry.register("port", lambda tx, record, operation: calls.append(record["id"]))

    class Source:
        def fetch(self, entity_type, entity_id):
            return {"id": entity_id, "name": "Port"}

    service = ProjectionService(registry, Source())
    session = Session()
    event = EntityChangedEvent(
        "event-1",
        "port",
        "port-1",
        "updated",
        occurred_at=datetime.now(UTC),
    )

    assert service.project(session, event).status == "projected"
    assert service.project(session, event).status == "duplicate"
    assert calls == ["port-1"]
    assert session.events == {"event-1"}
