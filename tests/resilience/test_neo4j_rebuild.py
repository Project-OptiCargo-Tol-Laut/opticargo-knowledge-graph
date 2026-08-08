"""An empty derived graph can be rebuilt entirely from canonical records."""

from opticargo_knowledge_graph.reconciliation import Reconciler
from tests.unit.test_reconciliation import Session, Source


def test_empty_graph_rebuild_projects_every_source_record() -> None:
    reconciler = Reconciler(Session(), Source(), owner="rebuild")
    projected = []

    class Service:
        def project_record(self, *args, **kwargs):
            projected.append(kwargs["entity_id"])
            return type("Projection", (), {"status": "projected"})()

    reconciler._service = Service()
    report = reconciler.run(repair=True, cleanup_stale=True)
    assert report.scanned == report.projected == 1
    assert projected == ["port-1"]
