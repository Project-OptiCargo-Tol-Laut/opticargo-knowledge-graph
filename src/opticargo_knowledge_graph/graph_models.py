"""Typed graph-context contracts owned by the Knowledge Graph domain.

The platform Shared package intentionally remains on its stable main contract.
Graph-specific query results therefore live with the service that produces
them.  RAG and Agents consume these models through the KG package boundary.
"""

from datetime import date
from decimal import Decimal
from typing import Annotated
from uuid import UUID

from opticargo_shared.base import ContractModel, DecimalScore, NonNegativeDecimal
from pydantic import AwareDatetime, Field


class PortContext(ContractModel):
    port_id: UUID
    code: Annotated[str, Field(min_length=1)]
    name: Annotated[str, Field(min_length=1)]
    country: str | None = None
    city: str | None = None
    province: str | None = None
    latitude: Annotated[Decimal, Field(ge=Decimal("-90"), le=Decimal("90"))] | None = None
    longitude: Annotated[Decimal, Field(ge=Decimal("-180"), le=Decimal("180"))] | None = None
    max_vessel_tonnage: NonNegativeDecimal | None = None


class VoyageLegContext(ContractModel):
    route_id: UUID | None = None
    route_type: str | None = None
    origin_port: PortContext
    destination_port: PortContext
    departure_date: date | None = None
    arrival_date: date | None = None
    distance_nm: NonNegativeDecimal | None = None
    estimated_days: int | None = Field(default=None, ge=0)


class ShipCapacityContext(ContractModel):
    ship_id: UUID
    ship_name: Annotated[str, Field(min_length=1)]
    total_weight_ton: NonNegativeDecimal | None = None
    used_weight_ton: NonNegativeDecimal | None = None
    remaining_weight_ton: NonNegativeDecimal
    remaining_volume_m3: NonNegativeDecimal | None = None
    deadweight_tonnage: NonNegativeDecimal | None = None
    cargo_capacity_m3: NonNegativeDecimal | None = None


class SupplierContext(ContractModel):
    supplier_id: UUID
    supplier_name: Annotated[str, Field(min_length=1)]
    rating: DecimalScore | None = None
    verified: bool | None = None
    avg_monthly_volume_ton: NonNegativeDecimal | None = None
    nearest_port_id: UUID | None = None
    distance_to_port_nm: NonNegativeDecimal | None = None
    supplied_commodity_ids: list[UUID] = Field(default_factory=list)


class GraphBackhaulCandidate(ContractModel):
    cargo_listing_id: UUID
    voyage_id: UUID | None = None
    supplier: SupplierContext
    commodity_id: UUID
    commodity_name: Annotated[str, Field(min_length=1)]
    origin_port: PortContext
    destination_port: PortContext | None = None
    available_weight_ton: NonNegativeDecimal
    available_volume_m3: NonNegativeDecimal | None = None
    schedule_compatible: bool
    capacity_compatible: bool
    certification_compatible: bool
    graph_score: DecimalScore | None = None
    relationship_path: list[str] = Field(default_factory=list)


class GraphContext(ContractModel):
    correlation_id: UUID
    voyage_id: UUID | None = None
    active_leg: VoyageLegContext | None = None
    ship_capacity: ShipCapacityContext | None = None
    candidates: list[GraphBackhaulCandidate] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    generated_at: AwareDatetime | None = None


__all__ = [
    "GraphBackhaulCandidate",
    "GraphContext",
    "PortContext",
    "ShipCapacityContext",
    "SupplierContext",
    "VoyageLegContext",
]
