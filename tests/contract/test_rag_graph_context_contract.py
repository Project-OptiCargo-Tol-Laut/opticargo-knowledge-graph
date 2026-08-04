from uuid import uuid4

from opticargo_knowledge_graph.queries.graph_context import find_backhaul_graph_context


class _FakeResult:
    def __init__(self, rows):
        self._rows = rows

    def single(self):
        return self._rows[0] if self._rows else None

    def __iter__(self):
        return iter(self._rows)


class _FakeSession:
    def __init__(self, snapshot, candidates):
        self._responses = [_FakeResult([snapshot]), _FakeResult(candidates)]
        self.queries = []

    def run(self, query, **parameters):
        self.queries.append((query, parameters))
        return self._responses.pop(0)


def test_missing_voyage_does_not_fall_back_to_global_supplier_search() -> None:
    session = _FakeSession(None, [])

    context = find_backhaul_graph_context(
        session=session,
        correlation_id=uuid4(),
        voyage_id=uuid4(),
    )

    assert context.candidates == []
    assert any("was not found" in warning for warning in context.warnings)
    assert len(session.queries) == 1


def test_supplier_query_caps_partial_load_at_remaining_voyage_capacity() -> None:
    correlation_id = uuid4()
    voyage_id = uuid4()
    origin_port_id = uuid4()
    destination_port_id = uuid4()
    supplier_id = uuid4()
    commodity_id = uuid4()
    snapshot = {
        "voyage_id": str(voyage_id),
        "remaining_weight_ton": 25.0,
        "origin_port_id": str(origin_port_id),
        "origin_port_name": "Makassar",
        "destination_port_id": str(destination_port_id),
        "destination_port_name": "Sorong",
    }
    candidates = [
        {
            "supplier_id": str(supplier_id),
            "supplier_name": "PT Muatan Parsial",
            "supplier_rating": 4.0,
            "supplier_verified": True,
            "supplier_avg_monthly_volume_ton": 80.0,
            "supplied_commodity_ids": [str(commodity_id)],
            "commodity_id": str(commodity_id),
            "commodity_name": "Kopra",
            # This is the value projected by the Cypher CASE expression.
            "available_weight_ton": 25.0,
            "origin_port_id": str(destination_port_id),
            "origin_port_name": "Sorong",
        }
    ]
    session = _FakeSession(snapshot, candidates)

    context = find_backhaul_graph_context(
        session=session,
        correlation_id=correlation_id,
        voyage_id=voyage_id,
        commodity="kopra",
    )

    assert context.candidates[0].available_weight_ton == 25
    assert context.candidates[0].capacity_compatible is True
    supplier_query = session.queries[1][0]
    assert "s.avg_monthly_volume_ton > $remaining_capacity" in supplier_query


def test_backhaul_graph_context_contains_final_integration_fields() -> None:
    correlation_id = uuid4()
    voyage_id = uuid4()
    route_id = uuid4()
    ship_id = uuid4()
    origin_port_id = uuid4()
    destination_port_id = uuid4()
    supplier_id = uuid4()
    commodity_id = uuid4()

    snapshot = {
        "voyage_id": str(voyage_id),
        "route_id": str(route_id),
        "remaining_weight_ton": 250.0,
        "ship_id": str(ship_id),
        "ship_name": "KM Nusantara",
        "ship_deadweight_tonnage": 1200.0,
        "ship_cargo_capacity_m3": 4000.0,
        "origin_port_id": str(origin_port_id),
        "origin_port_name": "Makassar",
        "origin_port_city": "Makassar",
        "origin_port_province": "Sulawesi Selatan",
        "origin_port_latitude": -5.1477,
        "origin_port_longitude": 119.4327,
        "origin_port_max_vessel_tonnage": 20000,
        "destination_port_id": str(destination_port_id),
        "destination_port_name": "Sorong",
        "destination_port_city": "Sorong",
        "destination_port_province": "Papua Barat Daya",
        "destination_port_latitude": -0.8762,
        "destination_port_longitude": 131.2558,
        "destination_port_max_vessel_tonnage": 12000,
        "route_distance_nm": 750.0,
        "route_estimated_days": 4,
        "route_type": "tol_laut",
    }
    candidates = [
        {
            "supplier_id": str(supplier_id),
            "supplier_name": "PT Komoditas Timur",
            "supplier_rating": 4.5,
            "supplier_verified": True,
            "supplier_avg_monthly_volume_ton": 120.0,
            "supplied_commodity_ids": [str(commodity_id)],
            "commodity_id": str(commodity_id),
            "commodity_name": "Kopra",
            "available_weight_ton": 80.0,
            "origin_port_id": str(destination_port_id),
            "origin_port_name": "Sorong",
            "origin_port_city": "Sorong",
            "origin_port_province": "Papua Barat Daya",
            "origin_port_latitude": -0.8762,
            "origin_port_longitude": 131.2558,
            "origin_port_max_vessel_tonnage": 12000,
        }
    ]
    session = _FakeSession(snapshot, candidates)

    context = find_backhaul_graph_context(
        session=session,
        correlation_id=correlation_id,
        voyage_id=voyage_id,
        commodity="kopra",
    )

    assert context.correlation_id == correlation_id
    assert context.voyage_id == voyage_id
    assert context.active_leg is not None
    assert context.active_leg.route_id == route_id
    assert context.active_leg.route_type == "tol_laut"
    assert context.active_leg.distance_nm == 750
    assert context.active_leg.estimated_days == 4
    assert context.active_leg.destination_port.city == "Sorong"
    assert context.ship_capacity is not None
    assert context.ship_capacity.deadweight_tonnage == 1200
    assert context.ship_capacity.cargo_capacity_m3 == 4000
    assert context.candidates[0].voyage_id == voyage_id
    assert context.candidates[0].supplier.verified is True
    assert context.candidates[0].supplier.avg_monthly_volume_ton == 120
    assert context.candidates[0].supplier.supplied_commodity_ids == [commodity_id]
    assert context.candidates[0].destination_port is not None
    assert context.candidates[0].destination_port.port_id == origin_port_id
    assert session.queries[1][1]["remaining_capacity"] == 250.0
