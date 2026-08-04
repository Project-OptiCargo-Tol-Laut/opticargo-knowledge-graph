"""Transaction lifecycle events map to their canonical graph projection."""

from opticargo_shared.events import EventType

from opticargo_knowledge_graph.worker import PROJECTABLE_EVENT_TYPES


def test_transaction_event_mapping_is_explicit_and_non_mutating() -> None:
    expected = {
        EventType.booking_created: ("booking", "created"),
        EventType.booking_status_changed: ("booking", "updated"),
        EventType.payment_created: ("payment", "created"),
        EventType.payment_status_changed: ("payment", "updated"),
        EventType.document_uploaded: ("document", "created"),
        EventType.review_created: ("review", "created"),
        EventType.recommendation_created: ("recommendation", "created"),
    }
    assert all(PROJECTABLE_EVENT_TYPES[event] == mapping for event, mapping in expected.items())
    assert EventType.report_requested not in PROJECTABLE_EVENT_TYPES
