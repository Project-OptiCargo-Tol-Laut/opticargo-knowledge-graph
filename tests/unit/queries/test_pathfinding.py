import pytest

from opticargo_knowledge_graph.queries.models import RouteResult
from opticargo_knowledge_graph.queries.pathfinding import route_paths


class Session:
    def __init__(self):
        self.query = None

    def run(self, query, **parameters):
        self.query = query.text
        return [
            {
                "origin_port_id": parameters["origin_port_id"],
                "destination_port_id": parameters["destination_port_id"],
                "port_ids": ["a", "b"],
                "route_ids": ["r"],
                "hop_count": 1,
                "distance_nm": 100.0,
                "estimated_days": 1,
            }
        ]


def test_pathfinding_is_bounded_and_typed() -> None:
    session = Session()
    result = route_paths(session, origin_port_id="a", destination_port_id="b", max_hops=99)

    assert "*1..6" in session.query
    assert isinstance(result.rows[0], RouteResult)


def test_pathfinding_rejects_same_origin_and_destination() -> None:
    with pytest.raises(ValueError, match="different"):
        route_paths(Session(), origin_port_id="a", destination_port_id="a")
