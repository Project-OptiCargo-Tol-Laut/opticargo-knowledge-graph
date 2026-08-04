"""JSON logging helpers with secret redaction."""

from __future__ import annotations

import json
import logging
import os
import sys
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


def configure_logging(level: str | None = None) -> None:
    """Configure one process-wide stdout handler for container log collection."""
    logger = get_logger()
    normalized_level = (level or os.getenv("LOG_LEVEL", "INFO")).upper()
    numeric_level = getattr(logging, normalized_level, logging.INFO)
    logger.setLevel(numeric_level)
    logger.propagate = False
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(handler)


def log_event(logger: logging.Logger, event: str, **fields: Any) -> None:
    logger.info(json.dumps({"event": event, **redact(fields)}, default=str))


__all__ = ["SENSITIVE_KEYS", "configure_logging", "get_logger", "log_event", "redact"]
