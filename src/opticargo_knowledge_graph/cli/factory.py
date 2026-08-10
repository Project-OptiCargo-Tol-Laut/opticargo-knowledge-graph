from __future__ import annotations

from typing import Any

from ..clients import Neo4jClient, PostgresClient, RedisStreamClient
from ..clients.neo4j import create_neo4j_driver
from ..config import GraphSettings
from ..config import Settings


def clients(settings: Settings) -> tuple[PostgresClient, Neo4jClient, RedisStreamClient]:
    postgres = PostgresClient(settings.database_url.get_secret_value())
    neo4j = Neo4jClient(
        settings.neo4j_uri,
        settings.neo4j_user,
        settings.neo4j_password.get_secret_value(),
        database=settings.neo4j_database,
        query_timeout_seconds=settings.graph_query_timeout_seconds,
    )
    redis = RedisStreamClient(settings.redis_url.get_secret_value())
    return postgres, neo4j, redis


def close_all(*items: Any) -> None:
    for item in items:
        item.close()


def build_driver_from_env():
    return create_neo4j_driver(GraphSettings.from_environment())
