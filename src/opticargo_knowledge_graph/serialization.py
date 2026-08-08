"""Serialization helpers for graph payloads."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from typing import Any
from uuid import UUID


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {
            str(key): to_jsonable(item)
            for key, item in sorted(value.items(), key=lambda pair: str(pair[0]))
            if item is not None
        }
    if isinstance(value, set):
        return [to_jsonable(item) for item in sorted(value, key=repr)]
    if isinstance(value, list | tuple):
        return [to_jsonable(item) for item in value]
    if isinstance(value, Enum):
        return to_jsonable(value.value)
    if isinstance(value, UUID | datetime | date | Decimal):
        return str(value)
    return value


__all__ = ["to_jsonable"]
