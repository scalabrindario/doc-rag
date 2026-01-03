"""
Plain text document parser.
"""
from typing import Any
from pathlib import Path

from .base_parser import BaseParser
from config.logging_config import get_logger

logger = get_logger(__name__)


class TXTParser(BaseParser):
    """
    Plain text document parser.

    NOTE: This is a placeholder for future implementation.
    Can be used for parsing .txt, .md, and other text files.
    """

    def _setup(self):
        """Configure TXT parser."""
        self.logger.info("📄 Configuring TXT parser...")
        # TODO: Add any specific text processing setup if needed
        self.logger.warning("⚠️ TXT parser not yet fully implemented")

    def parse(self, file_path: str) -> Any:
        """Parse a plain text document."""
        path = self.validate_file(file_path)

        self.logger.info(f"🔄 Parsing TXT: {path.name}")

        # Simple implementation - read file content
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        # TODO: Return in a structured format compatible with chunker
        # For now, return raw content
        self.logger.warning("⚠️ Returning raw text content - needs proper document structure")
        return content

    def supported_formats(self) -> list[str]:
        """Return supported file extensions for TXT."""
        return ['.txt', '.md', '.text']