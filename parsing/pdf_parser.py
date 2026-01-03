"""
PDF document parser using Docling.
"""
from pathlib import Path
from typing import Any, Optional

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions
from docling.document_converter import DocumentConverter, PdfFormatOption

from .base_parser import BaseParser, ParserConfig
from config.logging_config import get_logger

logger = get_logger(__name__)


class PDFParser(BaseParser):
    """PDF document parser using Docling."""

    def _setup(self):
        """Configure Docling PDF converter."""
        self.logger.info("📄 Configuring PDF parser (Docling)...")

        pipeline_options = PdfPipelineOptions(backend=self.config.backend)
        pipeline_options.do_ocr = self.config.do_ocr
        pipeline_options.do_table_structure = self.config.do_table_structure
        pipeline_options.generate_picture_images = self.config.generate_picture_images
        pipeline_options.do_picture_classification = self.config.do_picture_classification

        self.converter = DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

        self.logger.info("✅ PDF parser configured")

    def parse(self, file_path: str) -> Any:
        """
        Parse a PDF document.

        Args:
            file_path: Path to the PDF file

        Returns:
            Parsed Docling document

        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a PDF
        """
        path = self.validate_file(file_path)

        self.logger.info(f"🔄 Parsing PDF: {path.name}")

        result = self.converter.convert(str(path))
        doc = result.document

        self.logger.info(f"✅ PDF parsing completed")
        return doc

    def supported_formats(self) -> list[str]:
        """Return supported file extensions for PDF."""
        return ['.pdf']


# Convenience functions for backward compatibility
def setup_pdf_parser(
        backend: str = "dpl",
        do_ocr: bool = False,
        do_table_structure: bool = True,
        generate_picture_images: bool = False,
        do_picture_classification: bool = False
) -> PDFParser:
    """
    Setup and configure a PDF parser.

    Args:
        backend: Backend to use for parsing
        do_ocr: Enable OCR processing
        do_table_structure: Enable table structure detection
        generate_picture_images: Generate picture images
        do_picture_classification: Enable picture classification

    Returns:
        Configured PDFParser instance
    """
    config = ParserConfig(
        backend = backend,
        do_ocr = do_ocr,
        do_table_structure = do_table_structure,
        generate_picture_images = generate_picture_images,
        do_picture_classification = do_picture_classification
    )
    return PDFParser(config)


def parse_pdf(file_path: str, parser: Optional[PDFParser] = None) -> Any:
    """
    Parse a PDF document (convenience function).

    Args:
        file_path: Path to the PDF file
        parser: Configured PDFParser (creates default if None)

    Returns:
        Parsed document
    """
    if parser is None:
        parser = setup_pdf_parser()

    return parser.parse(file_path)

