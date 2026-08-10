from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Any

from ..serialization import graph_properties
from .models import NodeRef, ProjectionPlan, RelationshipPlan


@dataclass(frozen=True)
class ProjectionSpec:
    entity_type: str
    label: str
    table_name: str
    alias: str
    select_sql: str
    builder: Callable[[dict[str, Any]], ProjectionPlan]


def _node(label: str, entity_id: Any) -> NodeRef:
    return NodeRef(label=label, entity_id=str(entity_id))


def _rel(
    source_label: str,
    source_id: Any,
    relationship_type: str,
    target_label: str,
    target_id: Any,
    **properties: Any,
) -> RelationshipPlan:
    return RelationshipPlan(
        source=_node(source_label, source_id),
        relationship_type=relationship_type,
        target=_node(target_label, target_id),
        properties=graph_properties(properties),
    )


def _plan(
    entity_type: str,
    label: str,
    row: dict[str, Any],
    properties: dict[str, Any],
    relationships: list[RelationshipPlan] | None = None,
) -> ProjectionPlan:
    entity_id = str(row["id"])
    props = graph_properties({"id": entity_id, **properties})
    return ProjectionPlan(
        entity_type=entity_type,
        entity_id=entity_id,
        label=label,
        properties=props,
        relationships=tuple(relationships or []),
    )


def build_user(row: dict[str, Any]) -> ProjectionPlan:
    return _plan(
        "user",
        "User",
        row,
        {
            "username": row.get("username"),
            "role": row.get("role"),
            "company_name": row.get("company_name"),
            "account_status": row.get("account_status"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
    )


def build_port(row: dict[str, Any]) -> ProjectionPlan:
    return _plan(
        "port",
        "Port",
        row,
        {
            "name": row.get("name"),
            "city": row.get("city"),
            "province": row.get("province"),
            "latitude": row.get("latitude"),
            "longitude": row.get("longitude"),
            "facilities_json": row.get("facilities"),
            "max_vessel_tonnage": row.get("max_vessel_tonnage"),
            "operating_hours_json": row.get("operating_hours"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
    )


def build_ship(row: dict[str, Any]) -> ProjectionPlan:
    certifications = row.get("certifications") or {}
    if isinstance(certifications, dict):
        certification_names = sorted(str(key) for key, value in certifications.items() if value)
    else:
        certification_names = [str(value) for value in certifications]
    relationships = [_rel("Ship", row["id"], "OPERATED_BY", "User", row["operator_id"])]
    return _plan(
        "ship",
        "Ship",
        row,
        {
            "name": row.get("name"),
            "imo_number": row.get("imo_number"),
            "ship_type": row.get("ship_type"),
            "gross_tonnage": row.get("gross_tonnage"),
            "deadweight_tonnage": row.get("deadweight_tonnage"),
            "cargo_capacity_m3": row.get("cargo_capacity_m3"),
            "flag": row.get("flag"),
            "certifications": certification_names,
            "status": row.get("status"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
        relationships,
    )


def build_route(row: dict[str, Any]) -> ProjectionPlan:
    relationships = [
        _rel("Route", row["id"], "ORIGIN_PORT", "Port", row["origin_port_id"]),
        _rel("Route", row["id"], "DESTINATION_PORT", "Port", row["destination_port_id"]),
        _rel(
            "Port",
            row["origin_port_id"],
            "ROUTE_TO",
            "Port",
            row["destination_port_id"],
            route_id=str(row["id"]),
            distance_nm=row.get("distance_nm"),
            estimated_days=row.get("estimated_days"),
            route_type=row.get("route_type"),
            is_active=row.get("is_active"),
        ),
    ]
    return _plan(
        "route",
        "Route",
        row,
        {
            "distance_nm": row.get("distance_nm"),
            "estimated_days": row.get("estimated_days"),
            "route_type": row.get("route_type"),
            "is_active": row.get("is_active"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
        relationships,
    )


def build_voyage(row: dict[str, Any]) -> ProjectionPlan:
    relationships = [
        _rel("Voyage", row["id"], "USES_SHIP", "Ship", row["ship_id"]),
        _rel("Voyage", row["id"], "FOLLOWS_ROUTE", "Route", row["route_id"]),
        _rel("Voyage", row["id"], "DEPARTS_FROM", "Port", row["origin_port_id"]),
        _rel("Voyage", row["id"], "ARRIVES_AT", "Port", row["destination_port_id"]),
    ]
    return _plan(
        "voyage",
        "Voyage",
        row,
        {
            "ship_id": row.get("ship_id"),
            "route_id": row.get("route_id"),
            "origin_port_id": row.get("origin_port_id"),
            "destination_port_id": row.get("destination_port_id"),
            "departure_date": row.get("departure_date"),
            "arrival_date": row.get("arrival_date"),
            "total_capacity_ton": row.get("total_capacity_ton"),
            "used_capacity_ton": row.get("used_capacity_ton"),
            "remaining_capacity_ton": row.get("remaining_capacity_ton"),
            "status": row.get("status"),
            "waypoints_json": row.get("waypoints"),
            "version": row.get("version"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
        relationships,
    )


def build_cargo_capacity(row: dict[str, Any]) -> ProjectionPlan:
    relationships = [
        _rel("Voyage", row["voyage_id"], "HAS_CAPACITY", "CargoCapacity", row["id"]),
        _rel("CargoCapacity", row["id"], "FOR_VOYAGE", "Voyage", row["voyage_id"]),
    ]
    return _plan(
        "cargo_capacity",
        "CargoCapacity",
        row,
        {
            "available_weight_ton": row.get("available_weight_ton"),
            "available_volume_m3": row.get("available_volume_m3"),
            "cargo_type_allowed": row.get("cargo_type_allowed") or [],
            "temperature_range_json": row.get("temperature_range"),
            "version": row.get("version"),
            "updated_at": row.get("updated_at"),
        },
        relationships,
    )


def build_commodity(row: dict[str, Any]) -> ProjectionPlan:
    return _plan(
        "commodity",
        "Commodity",
        row,
        {
            "name": row.get("name"),
            "category": row.get("category"),
            "hs_code": row.get("hs_code"),
            "special_requirements_json": row.get("special_requirements"),
            "is_perishable": row.get("is_perishable"),
            "max_stack_height": row.get("max_stack_height"),
            "certifications_required": row.get("certifications_required") or [],
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
    )


def build_supplier(row: dict[str, Any]) -> ProjectionPlan:
    relationships = [
        _rel("Supplier", row["id"], "OWNED_BY", "User", row["user_id"]),
        _rel("Supplier", row["id"], "LOCATED_AT", "Port", row["port_id"]),
    ]
    for commodity_id in row.get("commodity_ids") or []:
        relationships.append(_rel("Supplier", row["id"], "SUPPLIES", "Commodity", commodity_id))
    return _plan(
        "supplier",
        "Supplier",
        row,
        {
            "business_name": row.get("business_name"),
            "avg_monthly_volume_ton": row.get("avg_monthly_volume_ton"),
            "rating": row.get("rating"),
            "verified": row.get("verified"),
            "address": row.get("address"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
        relationships,
    )


def build_cargo_listing(row: dict[str, Any]) -> ProjectionPlan:
    relationships = [
        _rel("CargoListing", row["id"], "LISTED_BY", "Supplier", row["supplier_id"]),
        _rel("CargoListing", row["id"], "OF_COMMODITY", "Commodity", row["commodity_id"]),
        _rel("CargoListing", row["id"], "ORIGINATES_AT", "Port", row["origin_port_id"]),
        _rel("CargoListing", row["id"], "DESTINED_FOR", "Port", row["destination_port_id"]),
    ]
    return _plan(
        "cargo_listing",
        "CargoListing",
        row,
        {
            "volume_ton": row.get("volume_ton"),
            "volume_m3": row.get("volume_m3"),
            "available_from": row.get("available_from"),
            "available_until": row.get("available_until"),
            "asking_price_per_ton": row.get("asking_price_per_ton"),
            "status": row.get("status"),
            "certifications": row.get("certifications") or [],
            "cargo_type": row.get("cargo_type"),
            "version": row.get("version"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
        relationships,
    )


def build_recommendation(row: dict[str, Any]) -> ProjectionPlan:
    relationships = [
        _rel("Recommendation", row["id"], "FOR_VOYAGE", "Voyage", row["voyage_id"])
    ]
    if row.get("requested_by"):
        relationships.append(
            _rel("Recommendation", row["id"], "REQUESTED_BY", "User", row["requested_by"])
        )
    return _plan(
        "recommendation",
        "Recommendation",
        row,
        {
            "recommendation_type": row.get("recommendation_type"),
            "score": row.get("score"),
            "status": row.get("status"),
            "generated_at": row.get("generated_at"),
            "responded_at": row.get("responded_at"),
            "model_mode": row.get("model_mode"),
            "trace_id": row.get("trace_id"),
        },
        relationships,
    )


def build_booking(row: dict[str, Any]) -> ProjectionPlan:
    relationships = [
        _rel("Booking", row["id"], "RESERVES_VOYAGE", "Voyage", row["voyage_id"]),
        _rel("Booking", row["id"], "BOOKS_LISTING", "CargoListing", row["cargo_listing_id"]),
    ]
    if row.get("created_by"):
        relationships.append(
            _rel("Booking", row["id"], "CREATED_BY", "User", row["created_by"])
        )
    if row.get("recommendation_id"):
        relationships.append(
            _rel(
                "Booking",
                row["id"],
                "BASED_ON_RECOMMENDATION",
                "Recommendation",
                row["recommendation_id"],
            )
        )
    return _plan(
        "booking",
        "Booking",
        row,
        {
            "booked_volume_ton": row.get("booked_volume_ton"),
            "booked_volume_m3": row.get("booked_volume_m3"),
            "agreed_price_per_ton": row.get("agreed_price_per_ton"),
            "status": row.get("status"),
            "booking_date": row.get("booking_date"),
            "confirmation_date": row.get("confirmation_date"),
            "booking_ref": row.get("booking_ref"),
            "version": row.get("version"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
        relationships,
    )


def build_payment(row: dict[str, Any]) -> ProjectionPlan:
    relationships = [_rel("Payment", row["id"], "PAYS_FOR", "Booking", row["booking_id"])]
    return _plan(
        "payment",
        "Payment",
        row,
        {
            "amount": row.get("amount"),
            "method": row.get("method"),
            "status": row.get("status"),
            "provider": row.get("provider"),
            "paid_at": row.get("paid_at"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
        relationships,
    )


def build_document(row: dict[str, Any]) -> ProjectionPlan:
    relationships: list[RelationshipPlan] = [
        _rel("Document", row["id"], "UPLOADED_BY", "User", row["uploaded_by"])
    ]
    if row.get("booking_id"):
        relationships.append(
            _rel("Document", row["id"], "ATTACHED_TO_BOOKING", "Booking", row["booking_id"])
        )
    if row.get("supersedes_document_id"):
        relationships.append(
            _rel(
                "Document",
                row["id"],
                "SUPERSEDES",
                "Document",
                row["supersedes_document_id"],
            )
        )
    return _plan(
        "document",
        "Document",
        row,
        {
            "doc_type": row.get("doc_type"),
            "title": row.get("title"),
            "mime_type": row.get("mime_type"),
            "issuer": row.get("issuer"),
            "document_version": row.get("document_version"),
            "effective_date": row.get("effective_date"),
            "source_reference": row.get("source_reference"),
            "is_superseded": row.get("is_superseded"),
            "ingestion_status": row.get("ingestion_status"),
            "created_at": row.get("created_at"),
            "updated_at": row.get("updated_at"),
        },
        relationships,
    )


def build_review(row: dict[str, Any]) -> ProjectionPlan:
    relationships = [
        _rel("Review", row["id"], "FOR_BOOKING", "Booking", row["booking_id"]),
        _rel("Review", row["id"], "WRITTEN_BY", "User", row["reviewer_id"]),
        _rel("Review", row["id"], "REVIEWS_USER", "User", row["reviewee_id"]),
    ]
    return _plan(
        "review",
        "Review",
        row,
        {"rating": row.get("rating"), "created_at": row.get("created_at")},
        relationships,
    )


_SPECS = {
    "user": ProjectionSpec(
        "user",
        "User",
        "users",
        "u",
        """SELECT u.id, u.username, u.role, u.company_name, u.account_status,
                  u.created_at, u.updated_at FROM users u""",
        build_user,
    ),
    "port": ProjectionSpec(
        "port",
        "Port",
        "ports",
        "p",
        """SELECT p.id, p.name, p.city, p.province, p.latitude, p.longitude,
                  p.facilities, p.max_vessel_tonnage, p.operating_hours,
                  p.created_at, p.updated_at FROM ports p""",
        build_port,
    ),
    "ship": ProjectionSpec(
        "ship",
        "Ship",
        "ships",
        "s",
        """SELECT s.id, s.name, s.imo_number, s.ship_type, s.gross_tonnage,
                  s.deadweight_tonnage, s.cargo_capacity_m3, s.operator_id, s.flag,
                  s.certifications, s.status, s.created_at, s.updated_at FROM ships s""",
        build_ship,
    ),
    "route": ProjectionSpec(
        "route",
        "Route",
        "routes",
        "r",
        """SELECT r.id, r.origin_port_id, r.destination_port_id, r.distance_nm,
                  r.estimated_days, r.route_type, r.is_active, r.created_at, r.updated_at
           FROM routes r""",
        build_route,
    ),
    "voyage": ProjectionSpec(
        "voyage",
        "Voyage",
        "voyages",
        "v",
        """SELECT v.id, v.ship_id, v.route_id, r.origin_port_id, r.destination_port_id,
                  v.departure_date, v.arrival_date, v.total_capacity_ton,
                  v.used_capacity_ton, v.remaining_capacity_ton, v.status, v.waypoints,
                  v.version, v.created_at, v.updated_at
           FROM voyages v JOIN routes r ON r.id = v.route_id""",
        build_voyage,
    ),
    "cargo_capacity": ProjectionSpec(
        "cargo_capacity",
        "CargoCapacity",
        "cargo_capacities",
        "cc",
        """SELECT cc.id, cc.voyage_id, cc.available_weight_ton, cc.available_volume_m3,
                  cc.cargo_type_allowed, cc.temperature_range, cc.updated_at, cc.version
           FROM cargo_capacities cc""",
        build_cargo_capacity,
    ),
    "commodity": ProjectionSpec(
        "commodity",
        "Commodity",
        "commodities",
        "c",
        """SELECT c.id, c.name, c.category, c.hs_code, c.special_requirements,
                  c.is_perishable, c.max_stack_height, c.certifications_required,
                  c.created_at, c.updated_at FROM commodities c""",
        build_commodity,
    ),
    "supplier": ProjectionSpec(
        "supplier",
        "Supplier",
        "suppliers",
        "s",
        """SELECT s.id, s.user_id, s.business_name, s.port_id, s.commodity_ids,
                  s.avg_monthly_volume_ton, s.rating, s.verified, s.address,
                  s.created_at, s.updated_at FROM suppliers s""",
        build_supplier,
    ),
    "cargo_listing": ProjectionSpec(
        "cargo_listing",
        "CargoListing",
        "cargo_listings",
        "cl",
        """SELECT cl.id, cl.supplier_id, cl.commodity_id, cl.volume_ton, cl.volume_m3,
                  cl.available_from, cl.available_until, cl.origin_port_id,
                  cl.destination_port_id, cl.asking_price_per_ton, cl.status,
                  cl.certifications, cl.cargo_type, cl.version, cl.created_at, cl.updated_at
           FROM cargo_listings cl""",
        build_cargo_listing,
    ),
    "recommendation": ProjectionSpec(
        "recommendation",
        "Recommendation",
        "recommendations",
        "r",
        """SELECT r.id, r.voyage_id, r.recommendation_type, r.score, r.status,
                  r.generated_at, r.responded_at, r.model_mode, r.trace_id, r.requested_by
           FROM recommendations r""",
        build_recommendation,
    ),
    "booking": ProjectionSpec(
        "booking",
        "Booking",
        "bookings",
        "b",
        """SELECT b.id, b.voyage_id, b.cargo_listing_id, b.recommendation_id,
                  b.booked_volume_ton, b.booked_volume_m3, b.agreed_price_per_ton,
                  b.status, b.booking_date, b.confirmation_date, b.booking_ref,
                  b.created_by, b.version, b.created_at, b.updated_at FROM bookings b""",
        build_booking,
    ),
    "payment": ProjectionSpec(
        "payment",
        "Payment",
        "payments",
        "p",
        """SELECT p.id, p.booking_id, p.amount, p.method, p.status, p.provider,
                  p.paid_at, p.created_at, p.updated_at FROM payments p""",
        build_payment,
    ),
    "document": ProjectionSpec(
        "document",
        "Document",
        "documents",
        "d",
        """SELECT d.id, d.booking_id, d.doc_type, d.title, d.mime_type, d.uploaded_by,
                  d.issuer, d.document_version, d.effective_date, d.source_reference,
                  d.is_superseded, d.supersedes_document_id, d.ingestion_status,
                  d.created_at, d.updated_at FROM documents d""",
        build_document,
    ),
    "review": ProjectionSpec(
        "review",
        "Review",
        "reviews",
        "r",
        """SELECT r.id, r.booking_id, r.reviewer_id, r.reviewee_id, r.rating,
                  r.created_at FROM reviews r""",
        build_review,
    ),
}

ENTITY_ORDER = (
    "user",
    "port",
    "ship",
    "route",
    "voyage",
    "cargo_capacity",
    "commodity",
    "supplier",
    "cargo_listing",
    "recommendation",
    "booking",
    "payment",
    "document",
    "review",
)

_ALIASES = {
    "users": "user",
    "ports": "port",
    "ships": "ship",
    "routes": "route",
    "voyages": "voyage",
    "cargo_capacities": "cargo_capacity",
    "cargocapacity": "cargo_capacity",
    "commodities": "commodity",
    "suppliers": "supplier",
    "cargo_listings": "cargo_listing",
    "cargolisting": "cargo_listing",
    "recommendations": "recommendation",
    "bookings": "booking",
    "payments": "payment",
    "documents": "document",
    "reviews": "review",
}


def normalize_entity_type(entity_type: str) -> str:
    normalized = entity_type.strip().lower().replace("-", "_").replace(" ", "_")
    return _ALIASES.get(normalized, normalized)


def get_projection_spec(entity_type: str) -> ProjectionSpec:
    normalized = normalize_entity_type(entity_type)
    try:
        return _SPECS[normalized]
    except KeyError as exc:
        raise KeyError(f"unsupported graph entity type: {entity_type}") from exc


def supported_entity_types() -> tuple[str, ...]:
    return ENTITY_ORDER


# Develop compatibility: expose the ordered projection contract without duplicating SQL.
PROJECTION_SPECS = tuple(_SPECS[name] for name in ENTITY_ORDER)

__all__ = [
    "ENTITY_ORDER", "PROJECTION_SPECS", "ProjectionSpec", "get_projection_spec",
    "normalize_entity_type", "supported_entity_types",
]

class ProjectionRegistry:
    """Develop handler registry retained independently from final ProjectionSpec registry."""
    def __init__(self, *, include_defaults: bool = False) -> None:
        self._handlers: dict[str, Any] = {}
        if include_defaults:
            try:
                from opticargo_knowledge_graph.projections.entity_builders import DEFAULT_BUILDERS
                for entity_type, handler in DEFAULT_BUILDERS.items():
                    self.register(entity_type, handler)
            except ImportError:
                pass
    def register(self, entity_type: str, handler: Any) -> None:
        normalized = normalize_entity_type(entity_type)
        if not normalized:
            raise ValueError("entity_type cannot be empty")
        self._handlers[normalized] = handler
    def get(self, entity_type: str) -> Any | None:
        return self._handlers.get(normalize_entity_type(entity_type))
    @property
    def entity_types(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))

def default_projection_registry() -> ProjectionRegistry:
    return ProjectionRegistry(include_defaults=True)
