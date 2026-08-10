from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator


class QueryModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class BackhaulCandidate(QueryModel):
    cargo_listing_id: str
    supplier_id: str
    supplier_name: str
    commodity_id: str
    commodity_name: str
    commodity_category: str
    available_volume_ton: Decimal
    origin_port_id: str
    origin_port_name: str
    distance_km: float
    available_from: str | None = None
    available_until: str | None = None


class CargoShipMatch(QueryModel):
    ship_id: str
    ship_name: str
    voyage_id: str
    remaining_capacity_ton: Decimal
    departure_date: str
    arrival_date: str
    route_id: str


class TransitPath(QueryModel):
    port_ids: list[str]
    port_names: list[str]
    route_ids: list[str]
    total_hops: int
    total_distance_nm: Decimal | None = None
    estimated_days: Decimal | None = None


class SupplierDistance(QueryModel):
    supplier_id: str
    supplier_name: str
    supplier_port_id: str
    supplier_port_name: str
    distance_km: float


class GraphOverview(QueryModel):
    labels: dict[str, int] = Field(default_factory=dict)
    relationships: dict[str, int] = Field(default_factory=dict)


class CargoMatchingRequest(QueryModel):
    origin_port_id: str
    destination_port_id: str
    commodity_category: str
    volume_needed: Decimal = Field(gt=0)
    time_window_start: datetime | None = None
    time_window_end: datetime | None = None
    limit: int = Field(default=20, ge=1, le=100)

    @model_validator(mode="after")
    def validate_window(self) -> "CargoMatchingRequest":
        if (
            self.time_window_start is not None
            and self.time_window_end is not None
            and self.time_window_start > self.time_window_end
        ):
            raise ValueError("time_window_start must be before time_window_end")
        return self


Record = dict[str, Any]


# Stable typed compatibility results retained from the develop contract.
from dataclasses import asdict, dataclass, field
from typing import Generic, TypeVar

T = TypeVar("T")

@dataclass(frozen=True)
class QueryResult(Generic[T]):
    name: str
    rows: list[T] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

@dataclass(frozen=True)
class PortResult:
    port_id: str
    port_name: str
    city: str | None = None
    province: str | None = None
    latitude: float | None = None
    longitude: float | None = None
    distance_km: float | None = None

@dataclass(frozen=True)
class SupplierMatch:
    supplier_id: str
    supplier_name: str
    commodity_id: str
    commodity_name: str
    port_id: str | None = None
    port_name: str | None = None
    voyage_id: str | None = None
    available_weight_ton: float | None = None
    remaining_capacity_ton: float | None = None
    rating: float | None = None
    verified: bool | None = None
    capacity_compatible: bool = True
    schedule_compatible: bool = True

@dataclass(frozen=True)
class RouteResult:
    origin_port_id: str
    destination_port_id: str
    port_ids: list[str]
    route_ids: list[str]
    hop_count: int
    distance_nm: float
    estimated_days: int

@dataclass(frozen=True)
class PortSupplierMetric:
    port_id: str
    port_name: str
    supplier_count: int
    verified_supplier_count: int = 0
    commodity_count: int = 0
    active_voyage_count: int = 0
    remaining_capacity_ton: float = 0.0

@dataclass(frozen=True)
class NetworkOverview:
    port_count: int
    route_count: int
    active_voyage_count: int
    supplier_count: int
    commodity_count: int
    remaining_capacity_ton: float

@dataclass(frozen=True)
class CorridorMetric:
    route_id: str
    origin_port_id: str
    destination_port_id: str
    distance_nm: float
    active_voyage_count: int
    remaining_capacity_ton: float

@dataclass(frozen=True)
class BookingLifecycleMetric:
    booking_id: str
    booking_status: str
    payment_count: int
    paid_amount: float
    review_count: int
    average_rating: float | None = None
