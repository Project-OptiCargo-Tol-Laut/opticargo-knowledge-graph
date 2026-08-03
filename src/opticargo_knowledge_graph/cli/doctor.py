"""Doctor command for Knowledge Graph local diagnostics."""

from __future__ import annotations

import json

from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.health import liveness_report, readiness_report


def main() -> int:
    settings = GraphSettings.from_environment()
    payload = {
        "service": "opticargo-knowledge-graph",
        "neo4j_uri": settings.neo4j_uri,
        "liveness": liveness_report(),
        "readiness": readiness_report().to_dict(),
    }
    print(json.dumps(payload, default=str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())


__all__ = ["main"]
