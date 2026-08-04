"""Booking, payment, and review form a safe queryable lifecycle graph."""

import os
from datetime import UTC, datetime
from uuid import uuid4

import pytest

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings
from opticargo_knowledge_graph.projections import ProjectionService, default_projection_registry
from opticargo_knowledge_graph.queries.analytics import booking_lifecycle
from tests.e2e.helpers import DictSource, cleanup_entities, project

pytestmark = pytest.mark.skipif(
    os.getenv("OPTICARGO_E2E") != "1",
    reason="requires seeded disposable Neo4j E2E runtime",
)


def test_booking_payment_review_lifecycle_has_no_sensitive_payment_reference() -> None:
    source = DictSource()
    ids = {
        name: str(uuid4())
        for name in (
            "reviewer",
            "reviewee",
            "listing",
            "recommendation",
            "booking",
            "payment",
            "review",
        )
    }
    settings = GraphSettings.from_environment()
    driver = create_neo4j_driver(settings)
    service = ProjectionService(default_projection_registry(), source)
    try:
        with driver.session(database=settings.neo4j_database) as session:
            anchor = session.run(
                "MATCH (v:Voyage)-[:SINGGAH_DI {role: 'origin'}]->(origin:Port) "
                "MATCH (v)-[:SINGGAH_DI {role: 'destination'}]->(destination:Port) "
                "MATCH (supplier:Supplier)-[:MENYUPLAI]->(commodity:Commodity) "
                "RETURN v.id AS voyage, origin.id AS origin, destination.id AS destination, "
                "supplier.id AS supplier, commodity.id AS commodity LIMIT 1"
            ).single(strict=True)
            for role in ("reviewer", "reviewee"):
                source.put(
                    "user",
                    {
                        "id": ids[role],
                        "role": role,
                        "is_active": True,
                        "created_at": datetime.now(UTC),
                    },
                )
                project(session, service, "user", ids[role])
            source.put(
                "cargo_listing",
                {
                    "id": ids["listing"],
                    "supplier_id": anchor["supplier"],
                    "commodity_id": anchor["commodity"],
                    "volume_ton": 5.0,
                    "available_from": "2026-01-01",
                    "available_until": "2026-12-31",
                    "origin_port_id": anchor["origin"],
                    "destination_port_id": anchor["destination"],
                    "asking_price_per_ton": 100.0,
                    "status": "open",
                },
            )
            project(session, service, "cargo_listing", ids["listing"])
            source.put(
                "recommendation",
                {
                    "id": ids["recommendation"],
                    "voyage_id": anchor["voyage"],
                    "requested_by": ids["reviewer"],
                    "recommendation_type": "backhaul",
                    "score": 0.91,
                    "status": "proposed",
                    "generated_at": datetime.now(UTC),
                    "model_mode": "fallback",
                    "trace_id": str(uuid4()),
                },
            )
            project(session, service, "recommendation", ids["recommendation"])
            source.put(
                "booking",
                {
                    "id": ids["booking"],
                    "voyage_id": anchor["voyage"],
                    "cargo_listing_id": ids["listing"],
                    "recommendation_id": ids["recommendation"],
                    "created_by": ids["reviewer"],
                    "booked_volume_ton": 5.0,
                    "agreed_price_per_ton": 90.0,
                    "status": "confirmed",
                    "booking_date": datetime.now(UTC),
                    "confirmation_date": datetime.now(UTC),
                    "booking_ref": "E2E-BOOKING",
                },
            )
            project(session, service, "booking", ids["booking"])
            source.put(
                "payment",
                {
                    "id": ids["payment"],
                    "booking_id": ids["booking"],
                    "amount": 450.0,
                    "method": "bank_transfer",
                    "status": "paid",
                    "paid_at": datetime.now(UTC),
                },
            )
            project(session, service, "payment", ids["payment"])
            source.put(
                "review",
                {
                    "id": ids["review"],
                    "booking_id": ids["booking"],
                    "reviewer_id": ids["reviewer"],
                    "reviewee_id": ids["reviewee"],
                    "rating": 5,
                    "created_at": datetime.now(UTC),
                },
            )
            project(session, service, "review", ids["review"])
            row = next(
                item
                for item in booking_lifecycle(session, limit=200).rows
                if item.booking_id == ids["booking"]
            )
            assert row.payment_count == 1 and row.paid_amount == 450.0
            assert row.review_count == 1 and row.average_rating == 5.0
            recommendation_link = session.run(
                """
                MATCH (:Booking {id: $booking_id})-[:BASED_ON_RECOMMENDATION]->
                      (:Recommendation {id: $recommendation_id})
                RETURN count(*) AS count
                """,
                booking_id=ids["booking"],
                recommendation_id=ids["recommendation"],
            ).single(strict=True)["count"]
            assert recommendation_link == 1
            payment = session.run(
                "MATCH (p:Payment {id: $id}) RETURN properties(p) AS properties", id=ids["payment"]
            ).single(strict=True)["properties"]
            assert "external_reference" not in payment and "provider_event_id" not in payment
            cleanup_entities(session, list(ids.values()))
    finally:
        driver.close()
