"""Projection allowlists must exclude secrets, raw payment data, and document content."""

from opticargo_knowledge_graph.clients.postgres import SOURCE_QUERIES
from tests.helpers import SOURCE_ROOT

FORBIDDEN_PROPERTIES = {
    "password_hash",
    "refresh_token",
    "provider_secret",
    "card_number",
    "payment_reference",
    "object_key",
    "document_content",
}


def test_canonical_queries_and_builders_exclude_sensitive_properties() -> None:
    queries = "\n".join(SOURCE_QUERIES.values()).casefold()
    builders = (SOURCE_ROOT / "projections" / "entity_builders.py").read_text(
        encoding="utf-8"
    ).casefold()
    violations = sorted(
        name for name in FORBIDDEN_PROPERTIES if name in queries or name in builders
    )
    assert violations == []
