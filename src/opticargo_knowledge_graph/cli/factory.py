"""Factory helpers for CLI commands."""

from opticargo_knowledge_graph.clients.neo4j import create_neo4j_driver
from opticargo_knowledge_graph.config import GraphSettings


def build_driver_from_env():
    return create_neo4j_driver(GraphSettings.from_environment())


__all__ = ["build_driver_from_env"]
