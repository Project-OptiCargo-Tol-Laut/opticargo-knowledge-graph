"""Read-only PostgreSQL source used by projection and reconciliation."""

from __future__ import annotations

import os
import re
from collections.abc import Callable, Iterator
from contextlib import contextmanager
from typing import Any

SQLALCHEMY_DRIVER = re.compile(r"^(postgres(?:ql)?)(?:\+[a-zA-Z0-9_]+)://")

SOURCE_QUERIES = {
    "user": """
        SELECT id::text, role, is_active, created_at
        FROM users
    """,
    "port": """
        SELECT id::text, name, city, province,
               latitude::float, longitude::float, max_vessel_tonnage::float
        FROM ports
    """,
    "ship": """
        SELECT id::text, name, imo_number, ship_type, gross_tonnage::float,
               deadweight_tonnage::float, cargo_capacity_m3::float,
               operator_id::text, flag, status
        FROM ships
    """,
    "commodity": """
        SELECT id::text, name, category, hs_code, is_perishable
        FROM commodities
    """,
    "route": """
        SELECT id::text, origin_port_id::text, destination_port_id::text,
               distance_nm::float, estimated_days, route_type, is_active,
               tarif_dry_container_idr::float, tarif_reefer_container_idr::float,
               tarif_general_cargo_idr::float, koefisien_pm29::float
        FROM routes
    """,
    "voyage": """
        SELECT id::text, ship_id::text, route_id::text, status,
               departure_date, arrival_date, total_capacity_ton::float,
               used_capacity_ton::float, remaining_capacity_ton::float
        FROM voyages
    """,
    "supplier": """
        SELECT id::text, business_name, user_id::text, port_id::text,
               commodity_ids::text[],
               avg_monthly_volume_ton::float, rating::float, verified, address
        FROM suppliers
    """,
    "cargo_capacity": """
        SELECT id::text, id::text AS voyage_id, total_capacity_ton::float,
               used_capacity_ton::float, remaining_capacity_ton::float
        FROM voyages
        WHERE status IN ('scheduled', 'in_transit')
    """,
    # Transaction projection views are owned by Gateway/PostgreSQL. They expose
    # only graph-safe fields and intentionally exclude payment/document secrets.
    "cargo_listing": """
        SELECT id::text, supplier_id::text, commodity_id::text,
               volume_ton::float, available_from, available_until,
               origin_port_id::text, destination_port_id::text,
               asking_price_per_ton::float, status
        FROM kg_cargo_listings_projection
    """,
    "recommendation": """
        SELECT id::text, voyage_id::text, requested_by::text,
               recommendation_type, score::float, status, generated_at,
               model_mode, trace_id::text
        FROM kg_recommendations_projection
    """,
    "booking": """
        SELECT id::text, voyage_id::text, cargo_listing_id::text,
               recommendation_id::text, created_by::text,
               booked_volume_ton::float, agreed_price_per_ton::float,
               status, booking_date, confirmation_date, booking_ref
        FROM kg_bookings_projection
    """,
    "payment": """
        SELECT id::text, booking_id::text, amount::float, method, status, paid_at
        FROM kg_payments_projection
    """,
    "document": """
        SELECT id::text, booking_id::text, uploaded_by::text,
               supersedes_document_id::text, doc_type, title, issuer,
               document_version, effective_date, source_reference,
               is_superseded, ingestion_status
        FROM kg_documents_projection
    """,
    "review": """
        SELECT id::text, booking_id::text, reviewer_id::text,
               reviewee_id::text, rating, created_at
        FROM kg_reviews_projection
    """,
}


def normalize_postgres_dsn(dsn: str) -> str:
    return SQLALCHEMY_DRIVER.sub(r"\1://", dsn)


def create_postgres_connection(dsn: str | None = None):
    import psycopg2

    active_dsn = dsn or os.environ["DATABASE_URL"]
    return psycopg2.connect(normalize_postgres_dsn(active_dsn))


class PostgresProjectionSource:
    """Whitelisted source-of-truth reads; event payloads never become graph truth."""

    def __init__(self, connection_factory: Callable[[], Any] = create_postgres_connection) -> None:
        self._connection_factory = connection_factory

    @contextmanager
    def _cursor(self) -> Iterator[Any]:
        from psycopg2.extras import RealDictCursor

        connection = self._connection_factory()
        cursor = None
        try:
            connection.set_session(readonly=True, autocommit=True)
            cursor = connection.cursor(cursor_factory=RealDictCursor)
            yield cursor
        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def fetch(self, entity_type: str, entity_id: str) -> dict[str, Any] | None:
        query = SOURCE_QUERIES.get(entity_type.casefold())
        if query is None:
            return None
        with self._cursor() as cursor:
            cursor.execute(
                f"SELECT * FROM ({query}) AS canonical_source WHERE id = %s::text",
                (entity_id,),
            )
            row = cursor.fetchone()
        return dict(row) if row else None

    def fetch_all(self, entity_type: str) -> list[dict[str, Any]]:
        query = SOURCE_QUERIES.get(entity_type.casefold())
        if query is None:
            raise ValueError(f"Unsupported projection entity: {entity_type}")
        with self._cursor() as cursor:
            cursor.execute(f"SELECT * FROM ({query}) AS canonical_source ORDER BY id")
            return [dict(row) for row in cursor.fetchall()]


__all__ = [
    "SOURCE_QUERIES",
    "PostgresProjectionSource",
    "create_postgres_connection",
    "normalize_postgres_dsn",
]
