"""
Document parsing module.

Supports multiple document formats:
- PDF (via pdf_parser.py)
- DOCX (via docx_parser.py) - placeholder
- HTML (via html_parser.py) - placeholder
- TXT (via txt_parser.py) - placeholder
- CSV (via csv_parser.py) - placeholder
"""
from .base_parser import BaseParser, ParserConfig
from .pdf_parser import PDFParser, setup_pdf_parser, parse_pdf
from .docx_parser import DOCXParser
from .html_parser import HTMLParser
from .txt_parser import TXTParser
from .csv_parser import CSVParser
from .parser_factory import ParserFactory, get_parser

__all__ = [
    'BaseParser',
    'ParserConfig',
    'PDFParser',
    'setup_pdf_parser',
    'parse_pdf',
    'DOCXParser',
    'HTMLParser',
    'TXTParser',
    'CSVParser',
    'ParserFactory',
    'get_parser',
]