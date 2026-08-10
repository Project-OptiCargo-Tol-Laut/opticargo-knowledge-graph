"""Deterministic shared fixtures for Knowledge Graph tests."""

from __future__ import annotations

import pytest

from tests.helpers import RecordingSession


@pytest.fixture
def recording_session() -> RecordingSession:
    return RecordingSession()
