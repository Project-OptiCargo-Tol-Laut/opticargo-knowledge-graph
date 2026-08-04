"""Idempotent graph entity builders using an explicit property allowlist."""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Any

from opticargo_knowledge_graph.errors import ProjectionError
from opticargo_knowledge_graph.schema.model import SCHEMA_VERSION
from opticargo_knowledge_graph.serialization import to_jsonable

ProjectionBuilder = Callable[[Any, dict[str, Any], str], None]


def source_checksum(record: dict[str, Any]) -> str:
    canonical = json.dumps(to_jsonable(record), sort_keys=True, separators=(",", ":"))
    return f"sha256:{hashlib.sha256(canonical.encode('utf-8')).hexdigest()}"


def _parameters(record: dict[str, Any]) -> dict[str, Any]:
    return {
        "record": to_jsonable(record),
        "checksum": source_checksum(record),
        "projected_at": datetime.now(UTC),
        "schema_version": SCHEMA_VERSION,
    }


def _run_required(tx, query: str, record: dict[str, Any]) -> None:
    result = tx.run(query, **_parameters(record))
    if result.single() is None:
        raise ProjectionError(f"Projection prerequisites are missing for {record.get('id')}")


def _delete_node(tx, label: str, entity_id: str) -> None:
    tx.run(f"MATCH (n:{label} {{id: $id}}) DETACH DELETE n", id=entity_id).consume()


def project_port(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "Port", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MERGE (n:Port {id: $record.id})
        SET n.name = $record.name, n.city = $record.city,
            n.province = $record.province, n.latitude = $record.latitude,
            n.longitude = $record.longitude,
            n.max_vessel_tonnage = $record.max_vessel_tonnage,
            n._entity_type = 'port', n._schema_version = $schema_version,
            n._source_checksum = $checksum, n._projected_at = $projected_at
        RETURN n.id AS id
        """,
        record,
    )


def project_ship(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "Ship", str(record["id"]))
        return
    _run_required(
        tx,
        """
        OPTIONAL MATCH (operator:User {id: $record.operator_id})
        MERGE (n:Ship {id: $record.id})
        SET n.name = $record.name, n.imo_number = $record.imo_number,
            n.ship_type = $record.ship_type, n.gross_tonnage = $record.gross_tonnage,
            n.deadweight_tonnage = $record.deadweight_tonnage,
            n.cargo_capacity_m3 = $record.cargo_capacity_m3,
            n.flag = $record.flag, n.status = $record.status,
            n._entity_type = 'ship', n._schema_version = $schema_version,
            n._source_checksum = $checksum, n._projected_at = $projected_at
        WITH n, operator
        OPTIONAL MATCH (n)-[old:OPERATED_BY]->()
        DELETE old
        WITH n, operator
        FOREACH (_ IN CASE WHEN operator IS NULL THEN [] ELSE [1] END |
            MERGE (n)-[:OPERATED_BY]->(operator))
        RETURN n.id AS id
        """,
        record,
    )


def project_commodity(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "Commodity", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MERGE (n:Commodity {id: $record.id})
        SET n.name = $record.name, n.category = $record.category,
            n.hs_code = $record.hs_code, n.is_perishable = $record.is_perishable,
            n._entity_type = 'commodity', n._schema_version = $schema_version,
            n._source_checksum = $checksum, n._projected_at = $projected_at
        RETURN n.id AS id
        """,
        record,
    )


def project_route(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted" or not record.get("is_active", True):
        tx.run(
            "MATCH ()-[r:TERHUBUNG_DENGAN|ROUTE_TO {id: $id}]->() DELETE r",
            id=str(record["id"]),
        ).consume()
        _delete_node(tx, "Route", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MATCH (origin:Port {id: $record.origin_port_id})
        MATCH (destination:Port {id: $record.destination_port_id})
        MERGE (route:Route {id: $record.id})
        SET route.distance_nm = $record.distance_nm,
            route.estimated_days = $record.estimated_days,
            route.route_type = $record.route_type,
            route.is_active = $record.is_active,
            route._entity_type = 'route', route._schema_version = $schema_version,
            route._source_checksum = $checksum, route._projected_at = $projected_at
        MERGE (origin)-[r:TERHUBUNG_DENGAN {id: $record.id}]->(destination)
        SET r.distance_nm = $record.distance_nm,
            r.estimated_days = $record.estimated_days,
            r.route_type = $record.route_type,
            r.is_active = $record.is_active,
            r.tarif_dry_container_idr = $record.tarif_dry_container_idr,
            r.tarif_reefer_container_idr = $record.tarif_reefer_container_idr,
            r.tarif_general_cargo_idr = $record.tarif_general_cargo_idr,
            r.koefisien_pm29 = $record.koefisien_pm29,
            r._source_checksum = $checksum, r._projected_at = $projected_at
        WITH origin, destination, route, r
        OPTIONAL MATCH (route)-[old:ORIGIN_PORT|DESTINATION_PORT]->()
        DELETE old
        WITH origin, destination, route, r
        MERGE (route)-[:ORIGIN_PORT]->(origin)
        MERGE (route)-[:DESTINATION_PORT]->(destination)
        MERGE (origin)-[canonical:ROUTE_TO {id: $record.id}]->(destination)
        SET canonical.distance_nm = $record.distance_nm,
            canonical.estimated_days = $record.estimated_days,
            canonical.route_type = $record.route_type,
            canonical.is_active = $record.is_active
        RETURN route.id AS id
        """,
        record,
    )


def project_supplier(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "Supplier", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MATCH (port:Port {id: $record.port_id})
        MERGE (s:Supplier {id: $record.id})
        SET s.business_name = $record.business_name,
            s.avg_monthly_volume_ton = $record.avg_monthly_volume_ton,
            s.rating = $record.rating, s.verified = $record.verified,
            s.address = $record.address,
            s._entity_type = 'supplier', s._schema_version = $schema_version,
            s._source_checksum = $checksum, s._projected_at = $projected_at
        WITH s, port
        OPTIONAL MATCH (owner:User {id: $record.user_id})
        WITH s, port, owner
        OPTIONAL MATCH (s)-[old:BERLOKASI_DI|MENYUPLAI|LOCATED_AT|SUPPLIES|OWNED_BY]->()
        DELETE old
        WITH DISTINCT s, port, owner
        MERGE (s)-[:BERLOKASI_DI]->(port)
        MERGE (s)-[:LOCATED_AT]->(port)
        FOREACH (_ IN CASE WHEN owner IS NULL THEN [] ELSE [1] END |
            MERGE (s)-[:OWNED_BY]->(owner))
        WITH s
        UNWIND $record.commodity_ids AS commodity_id
        MATCH (commodity:Commodity {id: commodity_id})
        MERGE (s)-[:MENYUPLAI]->(commodity)
        MERGE (s)-[:SUPPLIES]->(commodity)
        RETURN DISTINCT s.id AS id
        LIMIT 1
        """,
        record,
    )


def project_voyage(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted" or record.get("status") not in {"scheduled", "in_transit"}:
        _delete_node(tx, "Voyage", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MATCH (ship:Ship {id: $record.ship_id})
        MATCH (origin:Port)-[:TERHUBUNG_DENGAN {id: $record.route_id}]->(destination:Port)
        MATCH (route:Route {id: $record.route_id})
        MERGE (v:Voyage {id: $record.id})
        SET v.ship_id = $record.ship_id, v.route_id = $record.route_id,
            v.status = $record.status,
            v.departure_date = toString($record.departure_date),
            v.arrival_date = toString($record.arrival_date),
            v.total_capacity_ton = $record.total_capacity_ton,
            v.used_capacity_ton = $record.used_capacity_ton,
            v.remaining_capacity_ton = $record.remaining_capacity_ton,
            v.remaining_capacity = $record.remaining_capacity_ton,
            v._entity_type = 'voyage', v._schema_version = $schema_version,
            v._source_checksum = $checksum, v._projected_at = $projected_at
        WITH ship, origin, destination, route, v
        OPTIONAL MATCH ()-[old_ship:BEROPERASI_DI]->(v)
        DELETE old_ship
        WITH ship, origin, destination, route, v
        OPTIONAL MATCH (v)-[old_stop:SINGGAH_DI|USES_SHIP|FOLLOWS_ROUTE|DEPARTS_FROM|ARRIVES_AT]->()
        DELETE old_stop
        WITH ship, origin, destination, route, v
        MERGE (ship)-[:BEROPERASI_DI]->(v)
        MERGE (v)-[origin_stop:SINGGAH_DI {role: 'origin'}]->(origin)
        SET origin_stop.sequence = 1
        MERGE (v)-[destination_stop:SINGGAH_DI {role: 'destination'}]->(destination)
        SET destination_stop.sequence = 2
        MERGE (v)-[:USES_SHIP]->(ship)
        MERGE (v)-[:FOLLOWS_ROUTE]->(route)
        MERGE (v)-[:DEPARTS_FROM]->(origin)
        MERGE (v)-[:ARRIVES_AT]->(destination)
        RETURN v.id AS id
        """,
        record,
    )


def project_user(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "User", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MERGE (n:User {id: $record.id})
        SET n.role = $record.role, n.is_active = $record.is_active,
            n.created_at = toString($record.created_at),
            n._entity_type = 'user', n._schema_version = $schema_version,
            n._source_checksum = $checksum, n._projected_at = $projected_at
        RETURN n.id AS id
        """,
        record,
    )


def project_cargo_capacity(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "CargoCapacity", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MATCH (voyage:Voyage {id: $record.voyage_id})
        MERGE (capacity:CargoCapacity {id: $record.id})
        SET capacity.total_capacity_ton = $record.total_capacity_ton,
            capacity.used_capacity_ton = $record.used_capacity_ton,
            capacity.remaining_capacity_ton = $record.remaining_capacity_ton,
            capacity._entity_type = 'cargo_capacity',
            capacity._schema_version = $schema_version,
            capacity._source_checksum = $checksum,
            capacity._projected_at = $projected_at
        WITH voyage, capacity
        OPTIONAL MATCH (voyage)-[old:HAS_CAPACITY]->(:CargoCapacity)
        DELETE old
        WITH voyage, capacity
        MERGE (voyage)-[:HAS_CAPACITY]->(capacity)
        MERGE (capacity)-[:FOR_VOYAGE]->(voyage)
        RETURN capacity.id AS id
        """,
        record,
    )


def project_cargo_listing(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "CargoListing", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MATCH (supplier:Supplier {id: $record.supplier_id})
        MATCH (commodity:Commodity {id: $record.commodity_id})
        MATCH (origin:Port {id: $record.origin_port_id})
        MATCH (destination:Port {id: $record.destination_port_id})
        MERGE (listing:CargoListing {id: $record.id})
        SET listing.volume_ton = $record.volume_ton,
            listing.available_from = toString($record.available_from),
            listing.available_until = toString($record.available_until),
            listing.asking_price_per_ton = $record.asking_price_per_ton,
            listing.status = $record.status,
            listing._entity_type = 'cargo_listing',
            listing._schema_version = $schema_version,
            listing._source_checksum = $checksum,
            listing._projected_at = $projected_at
        WITH listing, supplier, commodity, origin, destination
        OPTIONAL MATCH (listing)-[old:LISTED_BY|OF_COMMODITY|ORIGINATES_AT|DESTINED_FOR]->()
        DELETE old
        WITH listing, supplier, commodity, origin, destination
        MERGE (listing)-[:LISTED_BY]->(supplier)
        MERGE (listing)-[:OF_COMMODITY]->(commodity)
        MERGE (listing)-[:ORIGINATES_AT]->(origin)
        MERGE (listing)-[:DESTINED_FOR]->(destination)
        RETURN listing.id AS id
        """,
        record,
    )


def project_recommendation(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "Recommendation", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MATCH (voyage:Voyage {id: $record.voyage_id})
        MATCH (requester:User {id: $record.requested_by})
        MERGE (recommendation:Recommendation {id: $record.id})
        SET recommendation.recommendation_type = $record.recommendation_type,
            recommendation.score = $record.score,
            recommendation.status = $record.status,
            recommendation.generated_at = toString($record.generated_at),
            recommendation.model_mode = $record.model_mode,
            recommendation.trace_id = $record.trace_id,
            recommendation._entity_type = 'recommendation',
            recommendation._schema_version = $schema_version,
            recommendation._source_checksum = $checksum,
            recommendation._projected_at = $projected_at
        WITH recommendation, voyage, requester
        OPTIONAL MATCH (recommendation)-[old:FOR_VOYAGE|REQUESTED_BY]->()
        DELETE old
        WITH recommendation, voyage, requester
        MERGE (recommendation)-[:FOR_VOYAGE]->(voyage)
        MERGE (recommendation)-[:REQUESTED_BY]->(requester)
        RETURN recommendation.id AS id
        """,
        record,
    )


def project_booking(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "Booking", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MATCH (voyage:Voyage {id: $record.voyage_id})
        MATCH (listing:CargoListing {id: $record.cargo_listing_id})
        OPTIONAL MATCH (creator:User {id: $record.created_by})
        OPTIONAL MATCH (recommendation:Recommendation {id: $record.recommendation_id})
        MERGE (booking:Booking {id: $record.id})
        SET booking.booked_volume_ton = $record.booked_volume_ton,
            booking.agreed_price_per_ton = $record.agreed_price_per_ton,
            booking.status = $record.status,
            booking.booking_date = toString($record.booking_date),
            booking.confirmation_date = toString($record.confirmation_date),
            booking.booking_ref = $record.booking_ref,
            booking._entity_type = 'booking',
            booking._schema_version = $schema_version,
            booking._source_checksum = $checksum,
            booking._projected_at = $projected_at
        WITH booking, voyage, listing, creator, recommendation
        OPTIONAL MATCH (booking)-[
            old:RESERVES_VOYAGE|BOOKS_LISTING|CREATED_BY|BASED_ON_RECOMMENDATION
        ]->()
        DELETE old
        WITH booking, voyage, listing, creator, recommendation
        MERGE (booking)-[:RESERVES_VOYAGE]->(voyage)
        MERGE (booking)-[:BOOKS_LISTING]->(listing)
        FOREACH (_ IN CASE WHEN creator IS NULL THEN [] ELSE [1] END |
            MERGE (booking)-[:CREATED_BY]->(creator))
        FOREACH (_ IN CASE WHEN recommendation IS NULL THEN [] ELSE [1] END |
            MERGE (booking)-[:BASED_ON_RECOMMENDATION]->(recommendation))
        RETURN booking.id AS id
        """,
        record,
    )


def project_payment(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "Payment", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MATCH (booking:Booking {id: $record.booking_id})
        MERGE (payment:Payment {id: $record.id})
        SET payment.amount = $record.amount, payment.method = $record.method,
            payment.status = $record.status, payment.paid_at = toString($record.paid_at),
            payment._entity_type = 'payment',
            payment._schema_version = $schema_version,
            payment._source_checksum = $checksum,
            payment._projected_at = $projected_at
        MERGE (payment)-[:PAYS_FOR]->(booking)
        RETURN payment.id AS id
        """,
        record,
    )


def project_document(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "Document", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MATCH (uploader:User {id: $record.uploaded_by})
        OPTIONAL MATCH (booking:Booking {id: $record.booking_id})
        OPTIONAL MATCH (superseded:Document {id: $record.supersedes_document_id})
        MERGE (document:Document {id: $record.id})
        SET document.doc_type = $record.doc_type, document.title = $record.title,
            document.issuer = $record.issuer,
            document.document_version = $record.document_version,
            document.effective_date = toString($record.effective_date),
            document.source_reference = $record.source_reference,
            document.is_superseded = $record.is_superseded,
            document.ingestion_status = $record.ingestion_status,
            document._entity_type = 'document',
            document._schema_version = $schema_version,
            document._source_checksum = $checksum,
            document._projected_at = $projected_at
        WITH document, uploader, booking, superseded
        OPTIONAL MATCH (document)-[old:UPLOADED_BY|ATTACHED_TO_BOOKING|SUPERSEDES]->()
        DELETE old
        WITH document, uploader, booking, superseded
        MERGE (document)-[:UPLOADED_BY]->(uploader)
        FOREACH (_ IN CASE WHEN booking IS NULL THEN [] ELSE [1] END |
            MERGE (document)-[:ATTACHED_TO_BOOKING]->(booking))
        FOREACH (_ IN CASE WHEN superseded IS NULL THEN [] ELSE [1] END |
            MERGE (document)-[:SUPERSEDES]->(superseded))
        RETURN document.id AS id
        """,
        record,
    )


def project_review(tx, record: dict[str, Any], operation: str) -> None:
    if operation == "deleted":
        _delete_node(tx, "Review", str(record["id"]))
        return
    _run_required(
        tx,
        """
        MATCH (booking:Booking {id: $record.booking_id})
        MATCH (reviewer:User {id: $record.reviewer_id})
        MATCH (reviewee:User {id: $record.reviewee_id})
        MERGE (review:Review {id: $record.id})
        SET review.rating = $record.rating,
            review.created_at = toString($record.created_at),
            review._entity_type = 'review', review._schema_version = $schema_version,
            review._source_checksum = $checksum, review._projected_at = $projected_at
        WITH review, booking, reviewer, reviewee
        OPTIONAL MATCH (review)-[old:FOR_BOOKING|WRITTEN_BY|REVIEWS_USER]->()
        DELETE old
        WITH review, booking, reviewer, reviewee
        MERGE (review)-[:FOR_BOOKING]->(booking)
        MERGE (review)-[:WRITTEN_BY]->(reviewer)
        MERGE (review)-[:REVIEWS_USER]->(reviewee)
        RETURN review.id AS id
        """,
        record,
    )


DEFAULT_BUILDERS: dict[str, ProjectionBuilder] = {
    "user": project_user,
    "port": project_port,
    "ship": project_ship,
    "commodity": project_commodity,
    "route": project_route,
    "supplier": project_supplier,
    "voyage": project_voyage,
    "cargo_capacity": project_cargo_capacity,
    "cargo_listing": project_cargo_listing,
    "recommendation": project_recommendation,
    "booking": project_booking,
    "payment": project_payment,
    "document": project_document,
    "review": project_review,
}


__all__ = ["DEFAULT_BUILDERS", "ProjectionBuilder", "source_checksum"]
