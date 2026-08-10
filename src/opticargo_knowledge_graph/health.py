from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock
from typing import Any
from uuid import uuid4


# Health is published from multiple threads in one worker process.
# Serialize the final replace step for Windows compatibility while keeping
# unique temp files and atomic replacement semantics on every platform.
_HEALTH_WRITE_LOCK = Lock()


@dataclass
class WorkerHealth:
    state: str
    heartbeat_at: str
    pid: int
    dependencies: dict[str, bool] = field(default_factory=dict)
    pending_entries: int = 0
    last_event_id: str | None = None
    last_error: str | None = None
    release: str = "dev"
    git_sha: str = "local"

    @classmethod
    def now(
        cls,
        *,
        state: str,
        dependencies: dict[str, bool] | None = None,
        pending_entries: int = 0,
        last_event_id: str | None = None,
        last_error: str | None = None,
        release: str = "dev",
        git_sha: str = "local",
    ) -> "WorkerHealth":
        return cls(
            state=state,
            heartbeat_at=datetime.now(UTC).isoformat(),
            pid=os.getpid(),
            dependencies=dependencies or {},
            pending_entries=pending_entries,
            last_event_id=last_event_id,
            last_error=last_error,
            release=release,
            git_sha=git_sha,
        )


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    # A fixed ``path.tmp`` races when the monitor thread and event worker
    # threads publish health concurrently. A unique file in the same directory
    # preserves atomic os.replace semantics without cross-thread collisions.
    temporary = path.with_name(f".{path.name}.{os.getpid()}.{uuid4().hex}.tmp")
    try:
        temporary.write_text(text, encoding="utf-8")
        # os.replace is atomic, but concurrent replacements of the same target
        # can raise WinError 5 on Windows. The graph worker publishes health
        # from several threads in a single process, so serialize only the
        # publication step.
        with _HEALTH_WRITE_LOCK:
            os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def write_health(path: Path, health: WorkerHealth) -> None:
    _atomic_write_text(
        path,
        json.dumps(asdict(health), separators=(",", ":")),
    )


def read_health(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def is_fresh(payload: dict[str, Any], stale_seconds: float) -> bool:
    raw = payload.get("heartbeat_at")
    if not isinstance(raw, str):
        return False
    heartbeat = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    return (datetime.now(UTC) - heartbeat).total_seconds() <= stale_seconds


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

from dataclasses import asdict as _asdict, dataclass as _dataclass, field as _field
@_dataclass(frozen=True)
class HealthReport:
    status: str
    dependencies: list[dict[str, str]] = _field(default_factory=list)
    detail: str | None = None
    def to_dict(self) -> dict[str, Any]: return _asdict(self)

def liveness_report() -> dict[str, str]:
    return {"status": "alive"}

def readiness_report(driver=None) -> HealthReport:
    if driver is None:
        return HealthReport(status="ready")
    try:
        if hasattr(driver, "verify_connectivity"):
            driver.verify_connectivity()
            return HealthReport(status="ready", dependencies=[{"name": "neo4j", "status": "ready"}])
        with driver.session() as session:
            value = session.run("RETURN 1 AS ok").single()
        ready = value is not None
        return HealthReport(
            status="ready" if ready else "degraded",
            dependencies=[{"name": "neo4j", "status": "ready" if ready else "degraded"}],
        )
    except Exception as exc:
        return HealthReport(
            status="degraded",
            dependencies=[{"name": "neo4j", "status": "degraded"}],
            detail=exc.__class__.__name__,
        )


def write_heartbeat(path: Path, heartbeat: WorkerHeartbeat) -> None:
    _atomic_write_text(
        path,
        json.dumps(heartbeat.to_dict(), sort_keys=True),
    )


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
