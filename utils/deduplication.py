"""
Document deduplication utilities for ChromaDB.
"""
from config.logging_config import get_logger

logger = get_logger(__name__)


def is_document_already_processed(chroma_collection, file_hash: str) -> bool:
    """
    Check if document with given hash already exists in ChromaDB.

    Args:
        chroma_collection: ChromaDB collection instance
        file_hash: Hash of the document

    Returns:
        bool: True if document exists, False otherwise
    """
    try:
        results = chroma_collection.get(
            where = {"document_hash": file_hash},
            limit = 1
        )

        if results['ids']:
            logger.info(f"✅ Document already exists (hash: {file_hash[:16]}...)")
            return True
        else:
            logger.info(f"🆕 Document not found, will process")
            return False

    except Exception as e:
        logger.warning(f"⚠️ Error checking document existence: {e}")
        return False
