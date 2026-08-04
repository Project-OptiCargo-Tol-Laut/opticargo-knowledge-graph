"""Typed query results preserve units, ordering fields, and immutable rows."""

from dataclasses import FrozenInstanceError

import pytest

from opticargo_knowledge_graph.queries.models import QueryResult, RouteResult, SupplierMatch


def test_query_result_models_are_typed_and_immutable() -> None:
    route = RouteResult("p1", "p2", ["p1", "p2"], ["r1"], 1, 120.5, 2)
    supplier = SupplierMatch("s1", "Supplier", "c1", "Coffee", available_weight_ton=10.0)
    result = QueryResult(name="route_paths", rows=[route])

    assert result.rows[0].distance_nm == 120.5
    assert supplier.available_weight_ton == 10.0
    with pytest.raises(FrozenInstanceError):
        route.hop_count = 2
