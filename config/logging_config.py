"""
Logging configuration for the entire application.
"""
import logging
from typing import Optional


def setup_logging(level: int = logging.INFO, format_string: Optional[str] = None):
    """
    Configure logging for the application.

    Args:
        level: Logging level (default: INFO)
        format_string: Custom format string (optional)
    """
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

    logging.basicConfig(
        level = level,
        format = format_string
    )

    # Suppress verbose third-party loggers
    suppress_third_party_loggers()


def suppress_third_party_loggers():
    """Suppress logging from third-party libraries."""

    # Docling related loggers
    logging.getLogger('docling').setLevel(logging.WARNING)
    logging.getLogger('docling_core').setLevel(logging.WARNING)
    logging.getLogger('docling.document_converter').setLevel(logging.WARNING)
    logging.getLogger('docling.datamodel').setLevel(logging.WARNING)

    # Other verbose libraries
    logging.getLogger('transformers').setLevel(logging.WARNING)
    logging.getLogger('sentence_transformers').setLevel(logging.WARNING)
    logging.getLogger('chromadb').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('httpcore').setLevel(logging.WARNING)
    logging.getLogger('urllib3').setLevel(logging.WARNING)

    # LlamaIndex related loggers
    logging.getLogger('llama_index').setLevel(logging.WARNING)
    logging.getLogger('llama_index.core').setLevel(logging.WARNING)

    # Hugging Face
    logging.getLogger('huggingface_hub').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance.

    Args:
        name: Name of the logger (typically __name__)

    Returns:
        logging.Logger: Configured logger instance
    """
    return logging.getLogger(name)


# Initialize default logging on import
setup_logging()