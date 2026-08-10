from __future__ import annotations

import os
import sys
from pathlib import Path

from .config import get_settings
from .health import heartbeat_report, is_fresh, read_health


def main() -> int | None:
    legacy_path = os.getenv("GRAPH_HEARTBEAT_PATH")
    # GRAPH_HEARTBEAT_PATH is retained for backward compatibility. The merged
    # final worker writes this compatibility heartbeat in addition to its
    # canonical WORKER_HEALTH_FILE when the variable is configured.
    if legacy_path:
        report = heartbeat_report(
            Path(legacy_path),
            max_age_seconds=int(os.getenv("GRAPH_HEARTBEAT_MAX_AGE_SECONDS", "90")),
        )
        if report.status != "ready":
            raise SystemExit(1)
        return None
    settings = get_settings()
    try:
        payload = read_health(settings.worker_health_file)
    except (OSError, ValueError):
        return 1
    if payload.get("state") not in {"starting", "idle", "processing", "retrying"}:
        return 1
    if not is_fresh(payload, settings.worker_heartbeat_stale_seconds):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
