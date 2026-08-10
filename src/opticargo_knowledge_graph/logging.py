from __future__ import annotations

import json
import logging
import sys
from datetime import UTC, datetime
from typing import Any


_REDACT_KEYS = {
    "password",
    "neo4j_password",
    "database_url",
    "redis_url",
    "token",
    "secret",
    "authorization",
    "api_key",
}


def _redact(value: Any, key: str | None = None) -> Any:
    if key and any(marker in key.lower() for marker in _REDACT_KEYS):
        return "***REDACTED***"
    if isinstance(value, dict):
        return {str(k): _redact(v, str(k)) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_redact(item) for item in value]
    if isinstance(value, Exception):
        return str(value)
    return value


class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload: dict[str, Any] = {
            "timestamp": datetime.now(UTC).isoformat(),
            "level": record.levelname,
            "service": "opticargo-graph-worker",
            "message": record.getMessage(),
            "logger": record.name,
        }
        context = getattr(record, "context", None)
        if isinstance(context, dict):
            payload.update(_redact(context))
        if record.exc_info:
            payload["exception"] = self.formatException(record.exc_info)
        return json.dumps(payload, ensure_ascii=False, separators=(",", ":"), default=str)


def configure_logging(level: str = "INFO", log_format: str = "json") -> None:
    root = logging.getLogger()
    root.handlers.clear()
    root.setLevel(level.upper())
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JsonFormatter() if log_format.lower() == "json" else logging.Formatter())
    root.addHandler(handler)
    app_logger = logging.getLogger("opticargo.knowledge_graph")
    app_logger.handlers.clear()
    app_logger.setLevel(level.upper())
    app_handler = logging.StreamHandler(sys.stdout)
    app_handler.setFormatter(JsonFormatter() if log_format.lower() == "json" else logging.Formatter())
    app_logger.addHandler(app_handler)
    app_logger.propagate = False


def log_event(
    logger: logging.Logger,
    level_or_event: int | str,
    message: str | None = None,
    **context: Any,
) -> None:
    """Emit final structured logs and preserve the develop event-log facade."""
    if message is None and isinstance(level_or_event, str):
        payload = {"event": level_or_event, **redact(context)}
        logger.info(json.dumps(payload, default=str))
        return
    level = int(level_or_event)
    logger.log(level, str(message), extra={"context": context})

def get_logger(name: str = "opticargo.knowledge_graph") -> logging.Logger:
    return logging.getLogger(name)

def redact(payload: Any) -> Any:
    return _redact(payload)
