"""Error hierarchy exposes safe typed retry policy."""

from opticargo_knowledge_graph.errors import KnowledgeGraphError, ProjectionError, QueryError


def test_error_details_distinguish_retryable_failures() -> None:
    base = KnowledgeGraphError("invalid contract").to_detail()
    projection = ProjectionError("database unavailable").to_detail()
    query = QueryError("timeout").to_detail()

    assert base.code == "knowledge_graph_error"
    assert base.retryable is False
    assert projection.code == "projection_error" and projection.retryable
    assert query.code == "query_error" and query.retryable
