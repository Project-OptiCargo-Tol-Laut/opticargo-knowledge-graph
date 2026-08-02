"""Typed, read-only context queries used by RAG and recommendation flows."""

from datetime import datetime, timezone
from decimal import Decimal
from uuid import NAMESPACE_URL, UUID, uuid5

from neo4j import Session

from opticargo_shared.agent_state import (
    GraphBackhaulCandidate,
    GraphContext,
    PortContext,
    ShipCapacityContext,
    SupplierContext,
    VoyageLegContext,
)


def _uuid(value: str) -> UUID:
    return UUID(str(value))


def _candidate_uuid(*parts: str) -> UUID:
    return uuid5(NAMESPACE_URL, "opticargo:graph-candidate:" + ":".join(parts))


def _normalized_rating(value: float | int | str | None) -> Decimal | None:
    if value is None:
        return None
    rating = Decimal(str(value))
    if rating > 1:
        rating = rating / Decimal("5")
    return min(max(rating, Decimal("0")), Decimal("1"))


def _port_from_record(record: dict, prefix: str) -> PortContext | None:
    identifier = record.get(f"{prefix}_port_id")
    name = record.get(f"{prefix}_port_name")
    if not identifier or not name:
        return None
    return PortContext(
        port_id=_uuid(identifier),
        code=record.get(f"{prefix}_port_code") or name,
        name=name,
        country=record.get(f"{prefix}_port_province"),
    )


def _voyage_snapshot(session: Session, voyage_id: str) -> dict | None:
    """Read the operating leg and capacity once, before looking for suppliers."""
    result = session.run(
        """
        MATCH (v:Voyage {id: $voyage_id})
        OPTIONAL MATCH (ship:Ship)-[:BEROPERASI_DI]->(v)
        OPTIONAL MATCH (v)-[:SINGGAH_DI {role: 'origin'}]->(origin:Port)
        OPTIONAL MATCH (v)-[:SINGGAH_DI {role: 'destination'}]->(destination:Port)
        RETURN v.id AS voyage_id,
               v.remaining_capacity_ton AS remaining_weight_ton,
               ship.id AS ship_id,
               ship.name AS ship_name,
               origin.id AS origin_port_id,
               origin.name AS origin_port_name,
               origin.province AS origin_port_province,
               destination.id AS destination_port_id,
               destination.name AS destination_port_name,
               destination.province AS destination_port_province
        """,
        voyage_id=voyage_id,
    )
    record = result.single()
    return dict(record) if record else None


def _supplier_candidates(
    session: Session,
    port_id: str | None,
    commodity: str | None,
    remaining_capacity: float | int | None,
    limit: int,
):
    """Get only suppliers that are usable for the requested operating context."""
    return session.run(
        """
        MATCH (s:Supplier)-[:BERLOKASI_DI]->(p:Port)
        MATCH (s)-[:MENYUPLAI]->(c:Commodity)
        WHERE ($port_id IS NULL OR p.id = $port_id)
          AND ($commodity IS NULL OR toLower(c.name) CONTAINS toLower($commodity))
          AND ($remaining_capacity IS NULL
               OR coalesce(s.avg_monthly_volume_ton, 0) <= $remaining_capacity)
        RETURN s.id AS supplier_id,
               s.business_name AS supplier_name,
               s.rating AS supplier_rating,
               s.verified AS supplier_verified,
               c.id AS commodity_id,
               c.name AS commodity_name,
               s.avg_monthly_volume_ton AS available_weight_ton,
               p.id AS origin_port_id,
               p.name AS origin_port_name,
               p.province AS origin_port_province
        ORDER BY coalesce(s.verified, false) DESC,
                 coalesce(s.rating, 0) DESC,
                 coalesce(s.avg_monthly_volume_ton, 0) DESC
        LIMIT $limit
        """,
        port_id=port_id,
        commodity=commodity.strip() if commodity and commodity.strip() else None,
        remaining_capacity=remaining_capacity,
        limit=limit,
    )


def find_backhaul_graph_context(
    session: Session,
    correlation_id: str | UUID,
    voyage_id: str | UUID | None = None,
    origin_port: str | None = None,
    commodity: str | None = None,
    limit: int = 20,
) -> GraphContext:
    """Build a shared ``GraphContext`` from the current Neo4j projection.

    For a voyage, suppliers at its destination are preferred because they are
    potential backhaul cargo.  For an explicit port lookup, only suppliers at
    the resolved port are returned.  The query is read-only and is safe for
    RAG enrichment as well as the recommendation flow.
    """
    normalized_limit = max(1, min(int(limit), 50))
    warnings: list[str] = []
    snapshot: dict | None = None
    selected_port_id: str | None = None

    if voyage_id:
        snapshot = _voyage_snapshot(session, str(voyage_id))
        if snapshot is None:
            warnings.append(f"Voyage {voyage_id} was not found in the knowledge graph")
        else:
            # A backhaul starts at the current voyage destination.  If older
            # seeded data has no destination role, fall back to its origin.
            selected_port_id = snapshot.get("destination_port_id") or snapshot.get("origin_port_id")
    elif origin_port and origin_port.strip():
        port_record = session.run(
            """
            MATCH (p:Port)
            WHERE toLower(p.name) CONTAINS toLower($origin_port)
            RETURN p.id AS port_id, p.name AS port_name
            ORDER BY size(p.name) ASC
            LIMIT 1
            """,
            origin_port=origin_port.strip(),
        ).single()
        if port_record:
            selected_port_id = port_record["port_id"]
        else:
            warnings.append(f"Port '{origin_port}' was not found in the knowledge graph")

    capacity = snapshot.get("remaining_weight_ton") if snapshot else None
    candidate_result = _supplier_candidates(
        session,
        port_id=selected_port_id,
        commodity=commodity,
        remaining_capacity=capacity,
        limit=normalized_limit,
    )

    candidates: list[GraphBackhaulCandidate] = []
    for raw_record in candidate_result:
        record = dict(raw_record)
        try:
            supplier_port = _port_from_record(record, "origin")
            if supplier_port is None:
                raise ValueError("supplier port is incomplete")
            supplier = SupplierContext(
                supplier_id=_uuid(record["supplier_id"]),
                supplier_name=record["supplier_name"],
                rating=_normalized_rating(record.get("supplier_rating")),
                nearest_port_id=supplier_port.port_id,
            )
            candidates.append(
                GraphBackhaulCandidate(
                    cargo_listing_id=_candidate_uuid(
                        str(record["supplier_id"]),
                        str(record["commodity_id"]),
                        str(supplier_port.port_id),
                    ),
                    supplier=supplier,
                    commodity_id=_uuid(record["commodity_id"]),
                    commodity_name=record["commodity_name"],
                    origin_port=supplier_port,
                    available_weight_ton=str(record.get("available_weight_ton") or 0),
                    schedule_compatible=True,
                    capacity_compatible=capacity is None
                    or Decimal(str(record.get("available_weight_ton") or 0)) <= Decimal(str(capacity)),
                    certification_compatible=bool(record.get("supplier_verified")),
                    graph_score=_normalized_rating(record.get("supplier_rating")),
                    relationship_path=["Supplier", "BERLOKASI_DI", "Port", "MENYUPLAI", "Commodity"],
                )
            )
        except (KeyError, TypeError, ValueError, ArithmeticError) as exc:
            warnings.append(f"Skipped malformed graph record: {exc}")

    active_leg = None
    ship_capacity = None
    if snapshot:
        origin = _port_from_record(snapshot, "origin")
        destination = _port_from_record(snapshot, "destination")
        if origin and destination:
            active_leg = VoyageLegContext(origin_port=origin, destination_port=destination)
        elif not origin or not destination:
            warnings.append("Voyage operating leg is incomplete in the knowledge graph")
        if snapshot.get("ship_id") and snapshot.get("ship_name") and capacity is not None:
            ship_capacity = ShipCapacityContext(
                ship_id=_uuid(snapshot["ship_id"]),
                ship_name=snapshot["ship_name"],
                remaining_weight_ton=str(capacity),
            )

    return GraphContext(
        correlation_id=_uuid(str(correlation_id)),
        voyage_id=_uuid(str(voyage_id)) if voyage_id else None,
        active_leg=active_leg,
        ship_capacity=ship_capacity,
        candidates=candidates,
        warnings=warnings,
        generated_at=datetime.now(timezone.utc),
    )
