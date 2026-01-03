"""
Factory for creating appropriate parsers based on file type.
"""
from pathlib import Path
from typing import Optional

from .base_parser import BaseParser, ParserConfig
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .html_parser import HTMLParser
from .txt_parser import TXTParser
from .csv_parser import CSVParser
from config.logging_config import get_logger

logger = get_logger(__name__)


class ParserFactory:
    """
    Factory class for creating document parsers.

    Automatically selects the appropriate parser based on file extension.
    """

    _parsers = {
        '.pdf': PDFParser,
        '.docx': DOCXParser,
        '.doc': DOCXParser,
        '.html': HTMLParser,
        '.htm': HTMLParser,
        '.txt': TXTParser,
        '.md': TXTParser,
        '.text': TXTParser,
        '.csv': CSVParser,
        '.tsv': CSVParser,
        '.xlsx': CSVParser,
        '.xls': CSVParser,
    }

    @classmethod
    def create_parser(
            cls,
            file_path: str,
            config: Optional[ParserConfig] = None
    ) -> BaseParser:
        """
        Create appropriate parser for the given file.

        Args:
            file_path: Path to the document
            config: Parser configuration

        Returns:
            Configured parser instance

        Raises:
            ValueError: If file format is not supported
        """
        path = Path(file_path)
        extension = path.suffix.lower()

        if extension not in cls._parsers:
            supported = ', '.join(cls._parsers.keys())
            raise ValueError(
                f"Unsupported file format: {extension}. "
                f"Supported formats: {supported}"
            )

        parser_class = cls._parsers[extension]
        logger.info(f"🏭 Creating {parser_class.__name__} for {extension} file")

        return parser_class(config)

    @classmethod
    def get_supported_formats(cls) -> list[str]:
        """Get list of all supported file formats."""
        return list(cls._parsers.keys())


# Convenience function
def get_parser(
        file_path: str,
        config: Optional[ParserConfig] = None
) -> BaseParser:
    """
    Get appropriate parser for a file (convenience function).

    Args:
        file_path: Path to the document
        config: Parser configuration

    Returns:
        Configured parser instance
    """
    return ParserFactory.create_parser(file_path, config)
