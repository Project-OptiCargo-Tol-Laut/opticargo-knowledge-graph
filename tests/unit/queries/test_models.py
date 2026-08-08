from opticargo_knowledge_graph.queries.models import QueryResult, SupplierMatch


def test_typed_query_result_serializes_rows() -> None:
    row = SupplierMatch("s", "Supplier", "c", "Commodity")
    result = QueryResult(name="matching", rows=[row])

    assert result.to_dict()["rows"][0]["supplier_id"] == "s"
