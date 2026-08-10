from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

MIGRATION_NAME = re.compile(r"^(?P<version>\d{3})_(?P<name>[a-z0-9_]+)\.cypher$")

class MigrationError(RuntimeError): pass
class MigrationDriftError(MigrationError): pass
class MigrationLockError(MigrationError): pass

@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    statements: tuple[str, ...]
    path: Path | None = None
    checksum: str = ""

def split_cypher_statements(content: str) -> tuple[str, ...]:
    cleaned_lines = [line for line in content.splitlines() if not line.strip().startswith("//")]
    return tuple(item.strip() for item in "\n".join(cleaned_lines).split(";") if item.strip())

def migration_files(base_dir: Path | None = None) -> list[Path]:
    root = base_dir or Path(__file__).parent / "migrations"
    return sorted(root.glob("*.cypher"))

def load_migrations(base_dir: Path | None = None) -> tuple[Migration, ...]:
    migrations: list[Migration] = []
    for path in migration_files(base_dir):
        match = MIGRATION_NAME.fullmatch(path.name)
        if match is None:
            raise MigrationError(f"Invalid migration filename: {path.name}")
        source = path.read_text(encoding="utf-8")
        statements = split_cypher_statements(source)
        if not statements:
            raise MigrationError(f"Migration is empty: {path.name}")
        migrations.append(Migration(version=int(match.group("version")), name=match.group("name"), statements=statements, path=path, checksum=f"sha256:{hashlib.sha256(source.encode('utf-8')).hexdigest()}"))
    versions = [m.version for m in migrations]
    if versions and versions != list(range(1, len(versions) + 1)):
        raise MigrationError(f"Migration versions must be contiguous from 001: {versions}")
    return tuple(migrations)

class GraphMigrator:
    def __init__(self, neo4j: Any, *, schema_name: str, target_version: int) -> None:
        self._neo4j=neo4j; self._schema_name=schema_name; self._target_version=target_version
    def current_version(self) -> int:
        rows=self._neo4j.run("MATCH (migration:GraphMigration {schema_name: $schema_name}) RETURN coalesce(max(migration.version), 0) AS version", {"schema_name": self._schema_name})
        return int(rows[0]["version"]) if rows else 0
    def migrate(self) -> list[int]:
        current=self.current_version(); applied=[]
        for migration in load_migrations():
            if migration.version <= current or migration.version > self._target_version: continue
            self._neo4j.execute_statements(migration.statements)
            self._neo4j.run("MERGE (migration:GraphMigration {schema_name: $schema_name, version: $version}) SET migration.name = $name, migration.checksum = $checksum, migration.applied_at = datetime()", {"schema_name":self._schema_name,"version":migration.version,"name":migration.name,"checksum":migration.checksum}, readonly=False)
            applied.append(migration.version); current=migration.version
        if current < self._target_version: raise RuntimeError(f"graph schema stopped at version {current}; target is {self._target_version}")
        return applied

# Compatibility name; final runtime uses GraphMigrator.
SchemaMigrator = GraphMigrator

def apply_migrations(session: Any, base_dir: Path | None = None) -> int:
    count=0
    for migration in load_migrations(base_dir):
        for statement in migration.statements:
            session.run(statement).consume()
        count += 1
    return count

__all__=["GraphMigrator","SchemaMigrator","Migration","MigrationError","MigrationDriftError","MigrationLockError","load_migrations","migration_files","split_cypher_statements","apply_migrations"]
