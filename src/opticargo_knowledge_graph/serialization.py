from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, is_dataclass
from enum import Enum
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


def to_graph_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return json.dumps(normalize_for_hash(value), sort_keys=True, separators=(",", ":"), default=str)
    if isinstance(value, (list, tuple, set)):
        converted = [to_graph_value(item) for item in value]
        if all(item is None or isinstance(item, (str, bool, int, float)) for item in converted):
            return converted
        return json.dumps(converted, sort_keys=True, separators=(",", ":"), default=str)
    return str(value)


def graph_properties(values: dict[str, Any]) -> dict[str, Any]:
    return {key: to_graph_value(value) for key, value in values.items() if value is not None}


def normalize_for_hash(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): normalize_for_hash(value[key]) for key in sorted(value)}
    if isinstance(value, (list, tuple)):
        return [normalize_for_hash(item) for item in value]
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, UUID):
        return str(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return value


def stable_hash(value: Any) -> str:
    raw = json.dumps(normalize_for_hash(value), sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def to_jsonable(value: Any) -> Any:
    """Compatibility serializer used by develop projection builders/tests."""
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in sorted(value.items(), key=lambda pair: str(pair[0])) if item is not None}
    if isinstance(value, set):
        return [to_jsonable(item) for item in sorted(value, key=repr)]
    if isinstance(value, (list, tuple)):
        return [to_jsonable(item) for item in value]
    if isinstance(value, Enum):
        return to_jsonable(value.value)
    if isinstance(value, (UUID, datetime, date, Decimal)):
        return str(value)
    return value
