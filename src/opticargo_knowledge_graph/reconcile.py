from __future__ import annotations

import argparse
import json
import logging

from .clients import Neo4jClient, PostgresClient, RedisStreamClient
from .clients.neo4j import create_neo4j_driver
from .clients.postgres import PostgresProjectionSource
from .config import GraphSettings
from .reconciliation import Reconciler
from .config import get_settings
from .logging import configure_logging, log_event
from .reconciliation import ReconciliationService


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Reconcile PostgreSQL source data into Neo4j")
    parser.add_argument("--check", action="store_true", help="Report differences without mutation")
    parser.add_argument(
        "--keep-stale",
        action="store_true",
        help="Do not delete graph entities absent from PostgreSQL",
    )
    return parser


def run() -> None:
    args = build_parser().parse_args()
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_format)
    logger = logging.getLogger(__name__)
    postgres = PostgresClient(settings.database_url.get_secret_value())
    neo4j = Neo4jClient(
        settings.neo4j_uri,
        settings.neo4j_user,
        settings.neo4j_password.get_secret_value(),
        database=settings.neo4j_database,
        query_timeout_seconds=settings.graph_query_timeout_seconds,
    )
    redis = RedisStreamClient(settings.redis_url.get_secret_value())
    try:
        report = ReconciliationService(settings, postgres, neo4j, redis).run(
            check_only=args.check,
            delete_stale=not args.keep_stale,
        )
        log_event(
            logger,
            logging.INFO,
            "graph reconciliation completed",
            **report.as_dict(),
        )
        print(json.dumps(report.as_dict(), indent=2, default=str))
    finally:
        postgres.close()
        neo4j.close()
        redis.close()


if __name__ == "__main__":
    run()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repair", action="store_true")
    parser.add_argument("--cleanup-stale", action="store_true")
    args = parser.parse_args(argv)
    if args.cleanup_stale and not args.repair:
        parser.error("--cleanup-stale requires --repair")
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            report = Reconciler(session, PostgresProjectionSource()).run(
                repair=args.repair, cleanup_stale=args.cleanup_stale
            )
        print(json.dumps(report.to_dict(), default=str, sort_keys=True))
        return 0 if report.ok else 2
    finally:
        driver.close()
