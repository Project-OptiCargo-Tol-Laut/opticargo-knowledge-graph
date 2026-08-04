import pytest

from opticargo_knowledge_graph.queries.models import PortResult
from opticargo_knowledge_graph.queries.spatial_queries import nearby_ports


class Session:
    def run(self, query, **parameters):
        return [
            {
                "port_id": "p",
                "port_name": "Ambon",
                "city": "Ambon",
                "province": "Maluku",
                "latitude": -3.7,
                "longitude": 128.1,
                "distance_km": 10.0,
            }
        ]


def test_nearby_ports_returns_typed_distance() -> None:
    result = nearby_ports(Session(), latitude=-3.6, longitude=128.0)
    assert isinstance(result.rows[0], PortResult)
    assert result.rows[0].distance_km == 10.0


def test_nearby_ports_rejects_invalid_coordinates() -> None:
    with pytest.raises(ValueError, match="latitude"):
        nearby_ports(Session(), latitude=91, longitude=0)
