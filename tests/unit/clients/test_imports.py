"""Client package exposes only adapter factories without opening connections."""

import opticargo_knowledge_graph.clients as clients


def test_client_exports_are_stable() -> None:
    assert callable(clients.create_neo4j_driver)
    assert callable(clients.create_postgres_connection)
    assert callable(clients.create_redis_client)
