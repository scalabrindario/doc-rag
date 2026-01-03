"""
Utility functions module.
"""
from .file_hash import calculate_file_hash
from .deduplication import is_document_already_processed

__all__ = ['calculate_file_hash', 'is_document_already_processed']