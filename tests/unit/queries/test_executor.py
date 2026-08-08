from opticargo_knowledge_graph.queries.executor import execute_read_query


class FakeSession:
    def run(self, query, **parameters):
        return [{"ok": parameters["value"]}]


def test_execute_read_query_blocks_mutations() -> None:
    try:
        execute_read_query(FakeSession(), "bad", "MATCH (n) SET n.x = 1")
    except ValueError as exc:
        assert "read-only" in str(exc)
    else:
        raise AssertionError("mutation query should fail")


def test_execute_read_query_returns_rows() -> None:
    result = execute_read_query(FakeSession(), "ok", "MATCH (n) RETURN n", value=1)

    assert result.rows == [{"ok": 1}]
