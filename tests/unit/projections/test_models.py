from opticargo_knowledge_graph.projections.models import ProjectionInput


def test_projection_input_serializes_without_mutating_payload() -> None:
    payload = {"name": "Ambon"}
    value = ProjectionInput("port", "id-1", payload)

    assert value.to_dict() == {
        "entity_type": "port",
        "entity_id": "id-1",
        "payload": {"name": "Ambon"},
    }
    assert payload == {"name": "Ambon"}
