"""Neo4j driver factory."""

from __future__ import annotations

from opticargo_knowledge_graph.config import GraphSettings


def create_neo4j_driver(settings: GraphSettings | None = None):
    from neo4j import GraphDatabase

    active = settings or GraphSettings.from_environment()
    return GraphDatabase.driver(active.neo4j_uri, auth=(active.neo4j_user, active.neo4j_password))


__all__ = ["create_neo4j_driver"]
