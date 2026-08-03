"""JSON logging helpers with secret redaction."""

from __future__ import annotations

import json
import logging
from typing import Any

SENSITIVE_KEYS = {"password", "token", "secret", "authorization", "api_key"}


def redact(payload: Any) -> Any:
    if isinstance(payload, dict):
        return {
            key: "***REDACTED***" if key.casefold() in SENSITIVE_KEYS else redact(value)
            for key, value in payload.items()
        }
    if isinstance(payload, list):
        return [redact(value) for value in payload]
    return payload


def get_logger(name: str = "opticargo.knowledge_graph") -> logging.Logger:
    return logging.getLogger(name)


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    logger.info(json.dumps({"event": event, **redact(fields)}, default=str))


__all__ = ["SENSITIVE_KEYS", "get_logger", "log_event", "redact"]
