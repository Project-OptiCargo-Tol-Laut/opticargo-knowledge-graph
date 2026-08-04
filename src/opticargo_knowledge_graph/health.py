"""Worker heartbeat persistence and dependency readiness helpers."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path


@dataclass(frozen=True)
class HealthReport:
    status: str
    dependencies: list[dict[str, str]] = field(default_factory=list)
    detail: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class WorkerHeartbeat:
    state: str
    timestamp: datetime
    release: str
    dependencies: dict[str, str]
    pending_count: int = 0
    last_event_ref: str | None = None
    last_error: str | None = None

    def to_dict(self) -> dict[str, object]:
        payload = asdict(self)
        payload["timestamp"] = self.timestamp.isoformat()
        return payload


def write_heartbeat(path: Path, heartbeat: WorkerHeartbeat) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f"{path.suffix}.tmp")
    temporary.write_text(json.dumps(heartbeat.to_dict(), sort_keys=True), encoding="utf-8")
    temporary.replace(path)


def read_heartbeat(path: Path) -> WorkerHeartbeat:
    payload = json.loads(path.read_text(encoding="utf-8"))
    timestamp = datetime.fromisoformat(payload["timestamp"])
    if timestamp.tzinfo is None:
        raise ValueError("heartbeat timestamp must be timezone-aware")
    return WorkerHeartbeat(
        state=str(payload["state"]),
        timestamp=timestamp,
        release=str(payload["release"]),
        dependencies=dict(payload["dependencies"]),
        pending_count=max(0, int(payload.get("pending_count", 0))),
        last_event_ref=payload.get("last_event_ref"),
        last_error=payload.get("last_error"),
    )


def heartbeat_report(
    path: Path,
    *,
    max_age_seconds: int = 90,
    now: datetime | None = None,
) -> HealthReport:
    if not path.is_file():
        return HealthReport(status="missing", detail="worker heartbeat is missing")
    try:
        heartbeat = read_heartbeat(path)
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return HealthReport(status="malformed", detail="worker heartbeat is malformed")
    current = now or datetime.now(UTC)
    if (current - heartbeat.timestamp).total_seconds() > max(1, max_age_seconds):
        return HealthReport(status="stale", detail="worker heartbeat is stale")
    dependencies = [
        {"name": name, "status": status}
        for name, status in sorted(heartbeat.dependencies.items())
    ]
    if heartbeat.state != "ready" or any(
        status != "ready" for status in heartbeat.dependencies.values()
    ):
        return HealthReport(status="degraded", dependencies=dependencies)
    return HealthReport(status="ready", dependencies=dependencies)


def liveness_report() -> dict[str, str]:
    return {"status": "alive"}


def readiness_report(driver=None) -> HealthReport:
    if driver is None:
        return HealthReport(status="ready", dependencies=[])
    try:
        driver.verify_connectivity()
        return HealthReport(status="ready", dependencies=[{"name": "neo4j", "status": "ready"}])
    except Exception as exc:  # noqa: BLE001 - health boundary normalizes driver failures
        return HealthReport(
            status="degraded",
            dependencies=[{"name": "neo4j", "status": "degraded"}],
            detail=exc.__class__.__name__,
        )


__all__ = [
    "HealthReport",
    "WorkerHeartbeat",
    "heartbeat_report",
    "liveness_report",
    "read_heartbeat",
    "readiness_report",
    "write_heartbeat",
]
