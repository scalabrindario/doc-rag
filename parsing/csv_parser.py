"""
CSV document parser.
"""
from typing import Any

from .base_parser import BaseParser
from config.logging_config import get_logger

logger = get_logger(__name__)


class CSVParser(BaseParser):
    """
    CSV document parser.

    NOTE: This is a placeholder for future implementation.
    Can be used for parsing CSV and Excel files.
    """

    def _setup(self):
        """Configure CSV parser."""
        self.logger.info("📄 Configuring CSV parser...")
        # TODO: Setup pandas or csv library
        self.logger.warning("⚠️ CSV parser not yet implemented")

    def parse(self, file_path: str) -> Any:
        """Parse a CSV document."""
        path = self.validate_file(file_path)
        raise NotImplementedError("CSV parsing not yet implemented")

    def supported_formats(self) -> list[str]:
        """Return supported file extensions for CSV."""
        return ['.csv', '.tsv', '.xlsx', '.xls']