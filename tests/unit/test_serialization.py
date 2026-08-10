from dataclasses import dataclass
from uuid import uuid4

from opticargo_knowledge_graph.serialization import to_jsonable


@dataclass(frozen=True)
class Sample:
    identifier: object


def test_to_jsonable_serializes_dataclass_uuid() -> None:
    identifier = uuid4()

    assert to_jsonable(Sample(identifier)) == {"identifier": str(identifier)}
