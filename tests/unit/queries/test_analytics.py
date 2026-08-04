from opticargo_knowledge_graph.queries.analytics import port_supplier_counts
from opticargo_knowledge_graph.queries.models import PortSupplierMetric


class Session:
    def run(self, query, **parameters):
        return [
            {
                "port_id": "p",
                "port_name": "Ambon",
                "supplier_count": 2,
                "verified_supplier_count": 1,
                "commodity_count": 3,
                "active_voyage_count": 1,
                "remaining_capacity_ton": 50.0,
            }
        ]


def test_port_analytics_returns_typed_capacity_summary() -> None:
    result = port_supplier_counts(Session())
    assert result.rows == [PortSupplierMetric("p", "Ambon", 2, 1, 3, 1, 50.0)]
