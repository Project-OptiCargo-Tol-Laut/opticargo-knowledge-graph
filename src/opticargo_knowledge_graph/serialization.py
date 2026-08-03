"""Serialization helpers for graph payloads."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Any
from uuid import UUID


def to_jsonable(value: Any) -> Any:
    if is_dataclass(value):
        return to_jsonable(asdict(value))
    if hasattr(value, "model_dump"):
        return value.model_dump(mode="json")
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, list | tuple | set):
        return [to_jsonable(item) for item in value]
    if isinstance(value, UUID | datetime | date | Decimal):
        return str(value)
    return value


__all__ = ["to_jsonable"]
