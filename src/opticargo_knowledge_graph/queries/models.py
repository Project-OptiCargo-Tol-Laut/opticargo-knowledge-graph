"""Typed query result models exposed to graph consumers."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Generic, TypeVar

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


__all__ = [
    "BookingLifecycleMetric",
    "CorridorMetric",
    "NetworkOverview",
    "PortResult",
    "PortSupplierMetric",
    "QueryResult",
    "RouteResult",
    "SupplierMatch",
]
