"""Schema migration loader for Cypher files."""

from __future__ import annotations

from pathlib import Path


def migration_files(base_dir: Path | None = None) -> list[Path]:
    root = base_dir or Path(__file__).parent / "migrations"
    return sorted(root.glob("*.cypher"))


def apply_migrations(session, base_dir: Path | None = None) -> int:
    count = 0
    for path in migration_files(base_dir):
        statement = path.read_text(encoding="utf-8").strip()
        if statement:
            session.run(statement)
            count += 1
    return count


__all__ = ["apply_migrations", "migration_files"]
