"""Readiness helpers for graph dependencies."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(frozen=True)
class HealthReport:
    status: str
    dependencies: list[dict[str, str]] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def liveness_report() -> dict[str, str]:
    return {"status": "alive"}


def readiness_report(driver=None) -> HealthReport:
    if driver is None:
        return HealthReport(status="ready", dependencies=[])
    try:
        driver.verify_connectivity()
        return HealthReport(status="ready", dependencies=[{"name": "neo4j", "status": "ready"}])
    except Exception as exc:
        return HealthReport(status="degraded", dependencies=[{"name": "neo4j", "status": "degraded", "detail": str(exc)}])


__all__ = ["HealthReport", "liveness_report", "readiness_report"]
