from opticargo_knowledge_graph.queries.cargo_matching import voyage_cargo_matches
from opticargo_knowledge_graph.queries.models import SupplierMatch


class Session:
    def run(self, query, **parameters):
        assert parameters["voyage_id"] == "voyage-1"
        return [
            {
                "supplier_id": "s",
                "supplier_name": "Supplier",
                "commodity_id": "c",
                "commodity_name": "Kopra",
                "port_id": "p",
                "port_name": "Ambon",
                "voyage_id": "voyage-1",
                "available_weight_ton": 25.0,
                "remaining_capacity_ton": 25.0,
                "rating": 4.5,
                "verified": True,
                "capacity_compatible": True,
                "schedule_compatible": True,
            }
        ]


def test_voyage_matching_returns_typed_capacity_compatible_rows() -> None:
    result = voyage_cargo_matches(Session(), voyage_id="voyage-1", commodity="kopra")

    assert isinstance(result.rows[0], SupplierMatch)
    assert result.rows[0].capacity_compatible is True
    assert result.rows[0].available_weight_ton == 25.0
