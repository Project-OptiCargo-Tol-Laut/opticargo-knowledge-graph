"""Validate production-critical repository structure and migration ordering."""

from __future__ import annotations

import json
import re
from pathlib import Path

MIGRATION_NAME = re.compile(r"^(?P<version>\d{3})_[a-z0-9_]+\.cypher$")


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    required = [
        "Dockerfile",
        "pyproject.toml",
        ".github/workflows/ci.yml",
        ".github/workflows/integration.yml",
        "src/opticargo_knowledge_graph/worker.py",
        "src/opticargo_knowledge_graph/reconciliation.py",
        "src/opticargo_knowledge_graph/projections/entity_builders.py",
        "src/opticargo_knowledge_graph/queries/graph_context.py",
    ]
    missing = [item for item in required if not (root / item).is_file()]
    empty_python = [
        str(path.relative_to(root))
        for area in (root / "src", root / "scripts", root / "tests")
        for path in area.rglob("*.py")
        if path.stat().st_size == 0
    ]
    migration_dir = root / "src/opticargo_knowledge_graph/schema/migrations"
    migration_paths = sorted(migration_dir.glob("*.cypher"))
    parsed = [MIGRATION_NAME.fullmatch(path.name) for path in migration_paths]
    invalid_migrations = [
        path.name
        for path, match in zip(migration_paths, parsed, strict=True)
        if match is None
    ]
    versions = sorted(int(match.group("version")) for match in parsed if match is not None)
    contiguous = versions == list(range(1, len(versions) + 1))
    errors = {
        "missing": missing,
        "empty_python": empty_python,
        "invalid_migrations": invalid_migrations,
        "migration_versions_contiguous": contiguous,
    }
    ok = not missing and not empty_python and not invalid_migrations and contiguous
    print(json.dumps({"status": "ok" if ok else "failed", **errors}, sort_keys=True))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
