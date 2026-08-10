"""Canonical Knowledge Graph schema and migration surface."""

from .migrator import GraphMigrator, SchemaMigrator, Migration, MigrationError, load_migrations, migration_files, split_cypher_statements, apply_migrations
from .model import (
    CANONICAL_LABELS, CANONICAL_RELATIONSHIPS, PROJECTION_METADATA_PROPERTIES,
    SCHEMA_VERSION, SENSITIVE_PROPERTIES,
)

__all__ = [
    "CANONICAL_LABELS", "CANONICAL_RELATIONSHIPS", "PROJECTION_METADATA_PROPERTIES",
    "SCHEMA_VERSION", "SENSITIVE_PROPERTIES", "GraphMigrator", "SchemaMigrator", "Migration", "MigrationError", "apply_migrations",
    "load_migrations", "migration_files", "split_cypher_statements",
]
