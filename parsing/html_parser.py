"""
HTML document parser (placeholder for future implementation).
"""
from typing import Any

from .base_parser import BaseParser
from config.logging_config import get_logger

logger = get_logger(__name__)


class HTMLParser(BaseParser):
    """
    HTML document parser.

    NOTE: This is a placeholder for future implementation.
    """

    def _setup(self):
        """Configure HTML parser."""
        self.logger.info("📄 Configuring HTML parser...")
        # TODO: Setup HTML parsing library (e.g., BeautifulSoup, lxml)
        self.logger.warning("⚠️ HTML parser not yet implemented")

    def parse(self, file_path: str) -> Any:
        """Parse an HTML document."""
        path = self.validate_file(file_path)
        raise NotImplementedError("HTML parsing not yet implemented")

    def supported_formats(self) -> list[str]:
        """Return supported file extensions for HTML."""
        return ['.html', '.htm']