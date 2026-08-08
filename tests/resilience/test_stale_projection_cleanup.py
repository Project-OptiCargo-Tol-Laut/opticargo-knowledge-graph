"""Cleanup removes graph entities absent from canonical source only in repair mode."""

from opticargo_knowledge_graph.reconciliation import Reconciler
from tests.unit.test_reconciliation import Result


class Source:
    def fetch_all(self, entity_type):
        return []


class Session:
    def run(self, query, **parameters):
        if "RETURN lock.owner" in query:
            return Result(single={"owner": parameters["owner"]})
        if "MATCH (n:Port)" in query:
            return Result(rows=[{"id": "stale-port", "checksum": "old"}])
        return Result()


def test_stale_projection_cleanup_calls_delete_once() -> None:
    reconciler = Reconciler(Session(), Source(), owner="cleanup", entity_order=("port",))
    deleted = []

    class Service:
        def project_record(self, *args, **kwargs):
            deleted.append((kwargs["entity_id"], kwargs["operation"]))
            return type("Projection", (), {"status": "deleted"})()

    reconciler._service = Service()
    report = reconciler.run(repair=True, cleanup_stale=True)
    assert report.entities[0].stale == report.entities[0].deleted == 1
    assert deleted == [("stale-port", "deleted")]
