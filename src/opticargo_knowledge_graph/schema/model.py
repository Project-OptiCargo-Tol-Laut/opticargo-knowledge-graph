"""Versioned canonical graph schema contract."""

from __future__ import annotations

SCHEMA_VERSION = "1.0"

CANONICAL_LABELS = (
    "User",
    "Port",
    "Ship",
    "Route",
    "Voyage",
    "CargoCapacity",
    "Commodity",
    "Supplier",
    "CargoListing",
    "Recommendation",
    "Booking",
    "Payment",
    "Document",
    "Review",
)

CANONICAL_RELATIONSHIPS = (
    "OPERATED_BY",
    "ORIGIN_PORT",
    "DESTINATION_PORT",
    "ROUTE_TO",
    "USES_SHIP",
    "FOLLOWS_ROUTE",
    "DEPARTS_FROM",
    "ARRIVES_AT",
    "HAS_CAPACITY",
    "FOR_VOYAGE",
    "OWNED_BY",
    "LOCATED_AT",
    "SUPPLIES",
    "LISTED_BY",
    "OF_COMMODITY",
    "ORIGINATES_AT",
    "DESTINED_FOR",
    "REQUESTED_BY",
    "RESERVES_VOYAGE",
    "BOOKS_LISTING",
    "CREATED_BY",
    "BASED_ON_RECOMMENDATION",
    "PAYS_FOR",
    "UPLOADED_BY",
    "ATTACHED_TO_BOOKING",
    "SUPERSEDES",
    "FOR_BOOKING",
    "WRITTEN_BY",
    "REVIEWS_USER",
)

PROJECTION_METADATA_PROPERTIES = (
    "_entity_type",
    "_schema_version",
    "_source_checksum",
    "_projected_at",
)

SENSITIVE_PROPERTIES = frozenset(
    {
        "password_hash",
        "email",
        "refresh_token",
        "external_reference",
        "provider_event_id",
        "object_key",
        "document_content",
        "ingestion_error",
    }
)

__all__ = [
    "CANONICAL_LABELS",
    "CANONICAL_RELATIONSHIPS",
    "PROJECTION_METADATA_PROPERTIES",
    "SCHEMA_VERSION",
    "SENSITIVE_PROPERTIES",
]
