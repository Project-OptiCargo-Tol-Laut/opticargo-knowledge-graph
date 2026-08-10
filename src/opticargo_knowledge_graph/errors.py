from dataclasses import asdict, dataclass

@dataclass(frozen=True)
class GraphErrorDetail:
    code: str
    message: str
    retryable: bool = False
    def to_dict(self) -> dict[str, object]:
        return asdict(self)

class KnowledgeGraphError(Exception):
    """Base error for graph package/runtime failures."""
    code = "knowledge_graph_error"
    retryable = False
    def to_detail(self) -> GraphErrorDetail:
        return GraphErrorDetail(code=self.code, message=str(self), retryable=self.retryable)


class ContractError(KnowledgeGraphError):
    """Event or shared contract validation failed."""


class UnsupportedEventError(KnowledgeGraphError):
    """Event is valid but not relevant to the graph projection."""


class DependencyUnavailableError(KnowledgeGraphError):
    """Required runtime dependency cannot be reached."""


class LockUnavailableError(KnowledgeGraphError):
    """A distributed job lock is already held."""


class QueryValidationError(KnowledgeGraphError):
    """Typed query input is not safe or valid."""


class ProjectionError(KnowledgeGraphError):
    """Canonical source/projector failure; retryable at worker boundary."""
    code = "projection_error"
    retryable = True

class QueryError(KnowledgeGraphError):
    """Read-only graph query execution failure."""
    code = "query_error"
    retryable = True

__all__ = [
    "GraphErrorDetail",
    "KnowledgeGraphError", "ContractError", "UnsupportedEventError",
    "DependencyUnavailableError", "LockUnavailableError", "QueryValidationError",
    "ProjectionError", "QueryError",
]
