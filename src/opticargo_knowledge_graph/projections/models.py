from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ..serialization import stable_hash


@dataclass(frozen=True)
class NodeRef:
    label: str
    entity_id: str


@dataclass(frozen=True)
class RelationshipPlan:
    source: NodeRef
    relationship_type: str
    target: NodeRef
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class ProjectionPlan:
    entity_type: str
    entity_id: str
    label: str
    properties: dict[str, Any]
    relationships: tuple[RelationshipPlan, ...] = ()

    @property
    def source_hash(self) -> str:
        relationships = [
            {
                "source": {"label": item.source.label, "id": item.source.entity_id},
                "type": item.relationship_type,
                "target": {"label": item.target.label, "id": item.target.entity_id},
                "properties": item.properties,
            }
            for item in self.relationships
        ]
        return stable_hash(
            {
                "entity_type": self.entity_type,
                "entity_id": self.entity_id,
                "label": self.label,
                "properties": self.properties,
                "relationships": relationships,
            }
        )

from dataclasses import asdict as _asdict, dataclass as _dataclass, field as _field
@_dataclass(frozen=True)
class ProjectionInput:
    entity_type: str
    entity_id: str
    payload: dict[str, Any] = _field(default_factory=dict)
    def to_dict(self) -> dict[str, Any]:
        return _asdict(self)
