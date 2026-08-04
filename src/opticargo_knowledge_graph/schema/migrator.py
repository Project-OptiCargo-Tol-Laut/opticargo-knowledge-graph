"""Versioned, checksummed Neo4j schema migrations with a database lock."""

from __future__ import annotations

import hashlib
import re
import socket
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

MIGRATION_NAME = re.compile(r"^(?P<version>\d{3})_(?P<name>[a-z0-9_]+)\.cypher$")
LEDGER_LABEL = "_OptiCargoSchemaMigration"
LOCK_NAME = "opticargo-schema"


class MigrationError(RuntimeError):
    """Base error for migration loading and execution."""


class MigrationDriftError(MigrationError):
    """Raised when an applied migration file has changed."""


class MigrationLockError(MigrationError):
    """Raised when another migrator owns the database lock."""


@dataclass(frozen=True)
class Migration:
    version: int
    name: str
    path: Path
    checksum: str
    statements: tuple[str, ...]


@dataclass(frozen=True)
class MigrationReport:
    discovered: int
    applied: int
    skipped: int
    current_version: int


def migration_files(base_dir: Path | None = None) -> list[Path]:
    root = base_dir or Path(__file__).parent / "migrations"
    return sorted(root.glob("*.cypher"))


def _split_statements(source: str) -> tuple[str, ...]:
    lines = [line for line in source.splitlines() if not line.lstrip().startswith("//")]
    return tuple(
        statement.strip() for statement in "\n".join(lines).split(";") if statement.strip()
    )


def load_migrations(base_dir: Path | None = None) -> list[Migration]:
    migrations: list[Migration] = []
    for path in migration_files(base_dir):
        match = MIGRATION_NAME.fullmatch(path.name)
        if match is None:
            raise MigrationError(f"Invalid migration filename: {path.name}")
        source = path.read_text(encoding="utf-8")
        statements = _split_statements(source)
        if not statements:
            raise MigrationError(f"Migration is empty: {path.name}")
        migrations.append(
            Migration(
                version=int(match.group("version")),
                name=match.group("name"),
                path=path,
                checksum=f"sha256:{hashlib.sha256(source.encode('utf-8')).hexdigest()}",
                statements=statements,
            )
        )
    versions = [migration.version for migration in migrations]
    if versions and versions != list(range(1, len(versions) + 1)):
        raise MigrationError(f"Migration versions must be contiguous from 001: {versions}")
    return migrations


class SchemaMigrator:
    def __init__(self, session, *, owner: str | None = None, lock_ttl_seconds: int = 300) -> None:
        self._session = session
        self._owner = owner or f"{socket.gethostname()}-{uuid4()}"
        self._lock_ttl_seconds = max(30, lock_ttl_seconds)

    def _bootstrap(self) -> None:
        self._session.run(
            f"CREATE CONSTRAINT opticargo_schema_migration_version IF NOT EXISTS "
            f"FOR (m:{LEDGER_LABEL}) REQUIRE m.version IS UNIQUE"
        ).consume()
        self._session.run(
            "CREATE CONSTRAINT opticargo_schema_lock_name IF NOT EXISTS "
            "FOR (l:_OptiCargoSchemaLock) REQUIRE l.name IS UNIQUE"
        ).consume()

    def _acquire_lock(self) -> None:
        expires_at = datetime.now(UTC) + timedelta(seconds=self._lock_ttl_seconds)
        record = self._session.run(
            """
            MERGE (lock:_OptiCargoSchemaLock {name: $name})
            ON CREATE SET lock.owner = $owner, lock.expires_at = $expires_at
            WITH lock
            WHERE lock.owner = $owner OR lock.expires_at < datetime()
            SET lock.owner = $owner,
                lock.expires_at = $expires_at,
                lock.acquired_at = datetime()
            RETURN lock.owner AS owner
            """,
            name=LOCK_NAME,
            owner=self._owner,
            expires_at=expires_at,
        ).single()
        if record is None or record["owner"] != self._owner:
            raise MigrationLockError("Neo4j schema migration lock is held by another process")

    def _release_lock(self) -> None:
        self._session.run(
            """
            MATCH (lock:_OptiCargoSchemaLock {name: $name, owner: $owner})
            SET lock.expires_at = datetime(), lock.owner = null
            """,
            name=LOCK_NAME,
            owner=self._owner,
        ).consume()

    def _ledger(self) -> dict[int, dict[str, str]]:
        result = self._session.run(
            f"MATCH (m:{LEDGER_LABEL}) "
            "RETURN m.version AS version, m.checksum AS checksum, m.status AS status"
        )
        return {
            int(record["version"]): {
                "checksum": str(record["checksum"]),
                "status": str(record["status"]),
            }
            for record in result
        }

    def _mark(self, migration: Migration, status: str, error_type: str | None = None) -> None:
        self._session.run(
            f"""
            MERGE (m:{LEDGER_LABEL} {{version: $version}})
            SET m.name = $name,
                m.checksum = $checksum,
                m.status = $status,
                m.error_type = $error_type,
                m.updated_at = datetime(),
                m.applied_at = CASE WHEN $status = 'applied' THEN datetime() ELSE m.applied_at END
            """,
            version=migration.version,
            name=migration.name,
            checksum=migration.checksum,
            status=status,
            error_type=error_type,
        ).consume()

    def apply(self, base_dir: Path | None = None) -> MigrationReport:
        migrations = load_migrations(base_dir)
        self._bootstrap()
        self._acquire_lock()
        applied = 0
        skipped = 0
        try:
            ledger = self._ledger()
            for migration in migrations:
                previous = ledger.get(migration.version)
                if (
                    previous
                    and previous["status"] == "applied"
                    and previous["checksum"] != migration.checksum
                ):
                    raise MigrationDriftError(
                        f"Applied migration checksum changed: {migration.path.name}"
                    )
                if previous and previous["status"] == "applied":
                    skipped += 1
                    continue
                self._mark(migration, "applying")
                try:
                    for statement in migration.statements:
                        self._session.run(statement).consume()
                except Exception as error:
                    self._mark(migration, "failed", error.__class__.__name__)
                    raise MigrationError(
                        f"Migration failed: {migration.path.name} ({error.__class__.__name__})"
                    ) from error
                self._mark(migration, "applied")
                applied += 1
            current = max((migration.version for migration in migrations), default=0)
            return MigrationReport(len(migrations), applied, skipped, current)
        finally:
            self._release_lock()


def apply_migrations(session, base_dir: Path | None = None) -> int:
    """Compatibility wrapper returning the number applied in this invocation."""
    return SchemaMigrator(session).apply(base_dir).applied


__all__ = [
    "Migration",
    "MigrationDriftError",
    "MigrationError",
    "MigrationLockError",
    "MigrationReport",
    "SchemaMigrator",
    "apply_migrations",
    "load_migrations",
    "migration_files",
]
