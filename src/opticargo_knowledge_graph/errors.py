"""Shared exception types for Knowledge Graph runtime."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class GraphErrorDetail:
    code: str
    message: str
    retryable: bool = False

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class KnowledgeGraphError(Exception):
    code = "knowledge_graph_error"
    retryable = False

    def to_detail(self) -> GraphErrorDetail:
        return GraphErrorDetail(code=self.code, message=str(self), retryable=self.retryable)


class ProjectionError(KnowledgeGraphError):
    code = "projection_error"
    retryable = True


class QueryError(KnowledgeGraphError):
    code = "query_error"
    retryable = False


__all__ = ["GraphErrorDetail", "KnowledgeGraphError", "ProjectionError", "QueryError"]
