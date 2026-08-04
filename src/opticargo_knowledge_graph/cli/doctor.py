"""Doctor command for Knowledge Graph local diagnostics."""

from __future__ import annotations

import json

from opticargo_knowledge_graph.cli.factory import build_driver_from_env
from opticargo_knowledge_graph.health import liveness_report, readiness_report


def main() -> int:
    driver = build_driver_from_env()
    try:
        readiness = readiness_report(driver)
    finally:
        driver.close()
    payload = {
        "service": "opticargo-knowledge-graph",
        "liveness": liveness_report(),
        "readiness": readiness.to_dict(),
    }
    print(json.dumps(payload, default=str))
    return 0 if readiness.status == "ready" else 1


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main"]
