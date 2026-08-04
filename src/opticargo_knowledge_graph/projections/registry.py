"""Projection handler registry."""

from __future__ import annotations

from dataclasses import dataclass

from opticargo_knowledge_graph.projections.entity_builders import (
    DEFAULT_BUILDERS,
    ProjectionBuilder,
)


@dataclass(frozen=True)
class ProjectionSpec:
    entity_type: str
    label: str
    dependencies: tuple[str, ...] = ()


PROJECTION_SPECS = (
    ProjectionSpec("user", "User"),
    ProjectionSpec("port", "Port"),
    ProjectionSpec("ship", "Ship", ("user",)),
    ProjectionSpec("route", "Route", ("port",)),
    ProjectionSpec("voyage", "Voyage", ("ship", "route")),
    ProjectionSpec("cargo_capacity", "CargoCapacity", ("voyage",)),
    ProjectionSpec("commodity", "Commodity"),
    ProjectionSpec("supplier", "Supplier", ("user", "port", "commodity")),
    ProjectionSpec(
        "cargo_listing", "CargoListing", ("supplier", "commodity", "port")
    ),
    ProjectionSpec("recommendation", "Recommendation", ("voyage", "user")),
    ProjectionSpec(
        "booking", "Booking", ("voyage", "cargo_listing", "recommendation", "user")
    ),
    ProjectionSpec("payment", "Payment", ("booking",)),
    ProjectionSpec("document", "Document", ("booking", "user")),
    ProjectionSpec("review", "Review", ("booking", "user")),
)

ENTITY_ALIASES = {
    "users": "user",
    "ports": "port",
    "ships": "ship",
    "routes": "route",
    "voyages": "voyage",
    "capacities": "cargo_capacity",
    "cargo-capacity": "cargo_capacity",
    "commodities": "commodity",
    "suppliers": "supplier",
    "listings": "cargo_listing",
    "cargo-listing": "cargo_listing",
    "recommendations": "recommendation",
    "bookings": "booking",
    "payments": "payment",
    "documents": "document",
    "reviews": "review",
}


def normalize_entity_type(entity_type: str) -> str:
    normalized = entity_type.strip().casefold().replace(" ", "_")
    return ENTITY_ALIASES.get(normalized, normalized)


class ProjectionRegistry:
    def __init__(self, *, include_defaults: bool = False) -> None:
        self._handlers: dict[str, ProjectionBuilder] = {}
        if include_defaults:
            for entity_type, handler in DEFAULT_BUILDERS.items():
                self.register(entity_type, handler)

    def register(self, entity_type: str, handler: ProjectionBuilder) -> None:
        normalized = normalize_entity_type(entity_type)
        if not normalized:
            raise ValueError("entity_type cannot be empty")
        self._handlers[normalized] = handler

    def get(self, entity_type: str) -> ProjectionBuilder | None:
        return self._handlers.get(normalize_entity_type(entity_type))

    @property
    def entity_types(self) -> tuple[str, ...]:
        return tuple(sorted(self._handlers))


def default_projection_registry() -> ProjectionRegistry:
    return ProjectionRegistry(include_defaults=True)


__all__ = [
    "ENTITY_ALIASES",
    "PROJECTION_SPECS",
    "ProjectionBuilder",
    "ProjectionRegistry",
    "ProjectionSpec",
    "default_projection_registry",
    "normalize_entity_type",
]
