"""A live reconciliation owner prevents concurrent repair."""

import pytest

from opticargo_knowledge_graph.reconciliation import Reconciler, ReconciliationLockError
from tests.unit.test_reconciliation import Result, Source


class LockedSession:
    def run(self, query, **parameters):
        if "RETURN lock.owner" in query:
            return Result(single=None)
        return Result()


def test_reconciliation_lock_contention_fails_before_scanning() -> None:
    with pytest.raises(ReconciliationLockError):
        Reconciler(LockedSession(), Source(), owner="worker-b").run(repair=True)
