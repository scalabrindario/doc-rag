"""
Document Processing System - Main package initialization.
"""
__version__ = "1.0.0"
__author__ = "Dario Scalabrin"

from .config.logging_config import get_logger
from .parsing import setup_pdf_parser, parse_pdf, get_parser, ParserFactory
from .chunking.chunker import setup_chunker, create_chunks_from_document
from .database.vectordb import setup_chromadb, setup_embedding_model
from .database.operations import add_chunks_to_vectordb, load_existing_index
from .pipeline.processor import process_document_with_deduplication
from .query.query_engine import setup_query_engine, execute_query_with_sources

__all__ = [
    'get_logger',
    'setup_pdf_parser',
    'parse_pdf',
    'get_parser',
    'ParserFactory',
    'setup_chunker',
    'create_chunks_from_document',
    'setup_chromadb',
    'setup_embedding_model',
    'add_chunks_to_vectordb',
    'load_existing_index',
    'process_document_with_deduplication',
    'setup_query_engine',
    'execute_query_with_sources',
]
