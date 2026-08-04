import pytest

from opticargo_knowledge_graph.queries.executor import execute_read_query
from opticargo_knowledge_graph.queries.spatial_queries import ports_by_name


class Session:
    def __init__(self):
        self.parameters = None

    def run(self, query, **parameters):
        self.parameters = parameters
        return []


def test_user_input_is_bound_as_parameter_not_interpolated() -> None:
    session = Session()
    attack = "Ambon') DETACH DELETE n //"
    ports_by_name(session, attack)

    assert session.parameters["name"] == attack
    assert attack not in session.parameters.keys()


@pytest.mark.parametrize("keyword", ["CREATE", "MERGE", "DETACH DELETE", "CALL dbms.listConfig"])
def test_executor_rejects_write_or_procedure_queries(keyword: str) -> None:
    with pytest.raises(ValueError, match="read-only"):
        execute_read_query(Session(), "unsafe", f"MATCH (n) {keyword} RETURN n")
