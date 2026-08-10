"""Validate the installed shared distribution and required graph contracts."""

from __future__ import annotations

import json
from importlib.metadata import version

from opticargo_shared.agent_state import GraphBackhaulCandidate, GraphContext


def main() -> int:
    shared_version = version("opticargo-shared")
    print(
        json.dumps(
            {
                "distribution": "opticargo-shared",
                "version": shared_version,
                "contracts": [GraphContext.__name__, GraphBackhaulCandidate.__name__],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
