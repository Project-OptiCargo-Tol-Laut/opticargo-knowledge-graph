"""Internal immutable contracts normalize projection outcomes and timestamps."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from opticargo_knowledge_graph.contracts import EntityChangedEvent, ProjectionResult


def test_entity_event_and_projection_result_are_immutable_and_serializable() -> None:
    occurred_at = datetime.now(UTC)
    event = EntityChangedEvent("evt", "port", "port-1", "updated", occurred_at=occurred_at)
    result = ProjectionResult("port", "port-1", "projected")

    assert event.to_dict()["occurred_at"].tzinfo is UTC
    assert result.to_dict() == {
        "entity_type": "port",
        "entity_id": "port-1",
        "status": "projected",
        "detail": None,
    }
    with pytest.raises(FrozenInstanceError):
        result.status = "failed"
