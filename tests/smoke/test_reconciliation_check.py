"""Check-only reconciliation reports drift without calling projection repair."""

from opticargo_knowledge_graph.reconciliation import Reconciler
from tests.unit.test_reconciliation import Session, Source


def test_reconciliation_check_only_is_machine_readable_and_non_mutating() -> None:
    reconciler = Reconciler(Session(), Source(), owner="smoke")

    class Service:
        def project_record(self, *args, **kwargs):
            raise AssertionError("check-only must not project")

    reconciler._service = Service()
    report = reconciler.run(repair=False)
    assert report.to_dict()["repair"] is False
    assert report.drift == 1
