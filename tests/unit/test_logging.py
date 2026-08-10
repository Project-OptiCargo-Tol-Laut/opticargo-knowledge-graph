import logging

from opticargo_knowledge_graph.logging import configure_logging, get_logger


def test_configure_logging_is_idempotent() -> None:
    logger = get_logger()
    original_handlers = list(logger.handlers)
    try:
        logger.handlers.clear()
        configure_logging("WARNING")
        configure_logging("DEBUG")

        assert logger.level == logging.DEBUG
        assert len(logger.handlers) == 1
        assert logger.propagate is False
    finally:
        logger.handlers[:] = original_handlers
