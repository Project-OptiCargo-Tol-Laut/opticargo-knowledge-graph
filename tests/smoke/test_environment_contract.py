"""Runtime endpoints use supported internal schemes and distinct dependency ports."""

from urllib.parse import urlparse

from opticargo_knowledge_graph.config import GraphSettings


def test_default_environment_contract_has_valid_internal_endpoints() -> None:
    settings = GraphSettings()
    neo4j = urlparse(settings.neo4j_uri)
    redis = urlparse(settings.redis_url)
    assert neo4j.scheme in {"bolt", "neo4j"}
    assert redis.scheme in {"redis", "rediss"}
    assert neo4j.port == 7687
    assert redis.port == 6379
    assert neo4j.hostname != "localhost"
