"""Knowledge Graph read-query package.

Submodules are imported explicitly to avoid loading optional shared/pydantic
contracts for lightweight diagnostics.
"""

__all__ = ["find_backhaul_graph_context"]


def __getattr__(name: str):
    if name == "find_backhaul_graph_context":
        from opticargo_knowledge_graph.queries.graph_context import find_backhaul_graph_context

        return find_backhaul_graph_context
    raise AttributeError(name)
