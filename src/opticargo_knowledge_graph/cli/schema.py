from __future__ import annotations

import json

from ..projections.registry import ENTITY_ORDER, get_projection_spec
from ..schema import load_migrations
from ..schema.migrator import migration_files


def run() -> None:
    payload = {
        "entities": [
            {
                "entity_type": entity_type,
                "label": get_projection_spec(entity_type).label,
                "table": get_projection_spec(entity_type).table_name,
            }
            for entity_type in ENTITY_ORDER
        ],
        "migrations": [
            {
                "version": migration.version,
                "name": migration.name,
                "statement_count": len(migration.statements),
            }
            for migration in load_migrations()
        ],
    }
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    run()


def main() -> int:
    for path in migration_files():
        print(path.name)
    return 0
