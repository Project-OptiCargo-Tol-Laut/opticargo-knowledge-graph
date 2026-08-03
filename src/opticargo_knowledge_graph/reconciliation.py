"""Reconciliation helpers for rebuilding graph projections."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ReconciliationReport:
    scanned: int = 0
    projected: int = 0
    failed: int = 0

    @property
    def ok(self) -> bool:
        return self.failed == 0


def reconcile_once(*, scanned: int = 0, projected: int = 0, failed: int = 0) -> ReconciliationReport:
    return ReconciliationReport(scanned=scanned, projected=projected, failed=failed)


__all__ = ["ReconciliationReport", "reconcile_once"]
