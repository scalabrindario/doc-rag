"""
DOCX document parser (placeholder for future implementation).
"""
from typing import Any

from .base_parser import BaseParser
from config.logging_config import get_logger

logger = get_logger(__name__)


class DOCXParser(BaseParser):
    """
    DOCX document parser.

    NOTE: This is a placeholder for future implementation.
    """

    def _setup(self):
        """Configure DOCX parser."""
        self.logger.info("📄 Configuring DOCX parser...")
        # TODO: Setup DOCX parsing library (e.g., python-docx, mammoth)
        self.logger.warning("⚠️ DOCX parser not yet implemented")

    def parse(self, file_path: str) -> Any:
        """Parse a DOCX document."""
        path = self.validate_file(file_path)
        raise NotImplementedError("DOCX parsing not yet implemented")

    def supported_formats(self) -> list[str]:
        """Return supported file extensions for DOCX."""
        return ['.docx', '.doc']