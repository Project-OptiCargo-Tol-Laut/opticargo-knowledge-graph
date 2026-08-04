from opticargo_knowledge_graph.clients.postgres import SOURCE_QUERIES
from opticargo_knowledge_graph.projections import entity_builders


def test_projection_source_and_cypher_exclude_identity_secrets() -> None:
    source = "\n".join(SOURCE_QUERIES.values()).casefold()
    builder_source = open(entity_builders.__file__, encoding="utf-8").read().casefold()

    for sensitive in (
        "password_hash",
        "authorization",
        "api_key",
        "external_reference",
        "provider_event_id",
    ):
        assert sensitive not in source
        assert sensitive not in builder_source
