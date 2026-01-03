"""
Base parser class and configuration for all document parsers.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional

from config.logging_config import get_logger

logger = get_logger(__name__)


@dataclass
class ParserConfig:
    """Configuration for document parsers."""
    backend: str = "dpl"
    do_ocr: bool = False
    do_table_structure: bool = True
    generate_picture_images: bool = False
    do_picture_classification: bool = False

    # Additional generic options
    extract_images: bool = False
    preserve_formatting: bool = True


class BaseParser(ABC):
    """
    Abstract base class for all document parsers.

    All parser implementations should inherit from this class.
    """

    def __init__(self, config: Optional[ParserConfig] = None):
        """
        Initialize parser with configuration.

        Args:
            config: Parser configuration (uses defaults if None)
        """
        self.config = config or ParserConfig()
        self.logger = get_logger(self.__class__.__name__)
        self._setup()

    @abstractmethod
    def _setup(self):
        """Setup the parser (configure converter, load models, etc.)"""
        pass

    @abstractmethod
    def parse(self, file_path: str) -> Any:
        """
        Parse a document file.

        Args:
            file_path: Path to the document

        Returns:
            Parsed document object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        pass

    @abstractmethod
    def supported_formats(self) -> list[str]:
        """
        Return list of supported file extensions.

        Returns:
            List of supported extensions (e.g., ['.pdf', '.docx'])
        """
        pass

    def validate_file(self, file_path: str) -> Path:
        """
        Validate that file exists and has supported format.

        Args:
            file_path: Path to the file

        Returns:
            Path object

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file format is not supported
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if path.suffix.lower() not in self.supported_formats():
            raise ValueError(
                f"Unsupported file format: {path.suffix}. "
                f"Supported formats: {', '.join(self.supported_formats())}"
            )

        return path
