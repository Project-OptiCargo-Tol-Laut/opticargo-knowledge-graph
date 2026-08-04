"""Structured logging recursively redacts sensitive keys."""

import json
import logging

from opticargo_knowledge_graph.logging import log_event, redact


def test_nested_secret_values_are_redacted(caplog) -> None:
    payload = {
        "password": "secret",
        "nested": {"authorization": "Bearer token", "safe": "value"},
        "items": [{"api_key": "key"}],
    }
    assert redact(payload) == {
        "password": "***REDACTED***",
        "nested": {"authorization": "***REDACTED***", "safe": "value"},
        "items": [{"api_key": "***REDACTED***"}],
    }

    logger = logging.getLogger("opticargo.security.test")
    with caplog.at_level(logging.INFO, logger=logger.name):
        log_event(logger, "security", **payload)
    decoded = json.loads(caplog.records[-1].message)
    assert "secret" not in caplog.records[-1].message
    assert decoded["nested"]["safe"] == "value"
