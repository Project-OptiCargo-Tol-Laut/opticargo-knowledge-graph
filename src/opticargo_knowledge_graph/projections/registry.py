"""Projection handler registry."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

ProjectionFn = Callable[[Any, dict[str, Any]], object]


class ProjectionRegistry:
    def __init__(self) -> None:
        self._handlers: dict[str, ProjectionFn] = {}

    def register(self, entity_type: str, handler: ProjectionFn) -> None:
        self._handlers[entity_type.casefold()] = handler

    def get(self, entity_type: str) -> ProjectionFn | None:
        return self._handlers.get(entity_type.casefold())


__all__ = ["ProjectionFn", "ProjectionRegistry"]
