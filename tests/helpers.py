"""Reusable deterministic fakes and repository paths for tests."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SOURCE_ROOT = REPOSITORY_ROOT / "src" / "opticargo_knowledge_graph"
WORKSPACE_ROOT = REPOSITORY_ROOT.parent


class FakeResult:
    def __init__(self, rows: list[dict[str, Any]] | None = None) -> None:
        self.rows = rows or []

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.rows)

    def single(self, strict: bool = False):
        if strict and len(self.rows) != 1:
            raise ValueError("expected exactly one row")
        return self.rows[0] if self.rows else None

    def consume(self) -> FakeResult:
        return self


class RecordingSession:
    def __init__(self, results: list[FakeResult] | None = None) -> None:
        self.queries: list[tuple[str, dict[str, Any]]] = []
        self.results = list(results or [])

    def run(self, query: Any, **parameters: Any) -> FakeResult:
        text = getattr(query, "text", str(query))
        self.queries.append((text, parameters))
        return self.results.pop(0) if self.results else FakeResult()
