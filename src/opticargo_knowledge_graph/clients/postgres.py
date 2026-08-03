"""Postgres connection factory for source-of-truth reads."""

from __future__ import annotations

import os


def create_postgres_connection(dsn: str | None = None):
    import psycopg2

    return psycopg2.connect(dsn or os.environ["DATABASE_URL"])


__all__ = ["create_postgres_connection"]
