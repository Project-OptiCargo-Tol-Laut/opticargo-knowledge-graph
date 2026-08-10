"""A missed projection is detected and repaired from canonical source."""

from opticargo_knowledge_graph.reconciliation import Reconciler
from tests.unit.test_reconciliation import Session, Source


def test_missed_event_is_repaired_once_without_duplicate() -> None:
    reconciler = Reconciler(Session(), Source(), owner="recovery")
    projected = []

    class Service:
        def project_record(self, *args, **kwargs):
            projected.append((kwargs["entity_type"], kwargs["entity_id"]))
            return type("Projection", (), {"status": "projected"})()

    reconciler._service = Service()
    report = reconciler.run(repair=True)
    assert report.projected == 1
    assert projected == [("port", "port-1")]
