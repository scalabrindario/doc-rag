"""
Main processing pipeline with deduplication.
"""
from pathlib import Path
from typing import Tuple

from utils.file_hash import calculate_file_hash
from utils.deduplication import is_document_already_processed
from chunking.chunker import create_chunks_from_document
from database.operations import add_chunks_to_vectordb, load_existing_index
from config.logging_config import get_logger

logger = get_logger(__name__)


def process_document_with_deduplication(
        file_path: str,
        company_name: str,
        document_name: str,
        chroma_collection,
        parser,
        chunker,
        embed_model
) -> Tuple[any, bool]:
    """
    Main pipeline that checks for duplicates before processing.

    Args:
        file_path: Path to the document
        company_name: Name of the company
        document_name: Name of the document
        chroma_collection: ChromaDB collection instance
        parser: Configured document parser (BaseParser instance)
        chunker: Configured chunker
        embed_model: Configured embedding model

    Returns:
        Tuple[VectorStoreIndex, bool]: (index, was_skipped)
    """
    logger.info(f"🚀 Starting document processing: {Path(file_path).name}")

    # Step 1: Calculate file hash
    file_hash = calculate_file_hash(file_path)

    # Step 2: Check if already processed
    if is_document_already_processed(chroma_collection, file_hash):
        logger.info(f"⏭️ Skipping already processed document")

        # Return existing index
        index = load_existing_index(chroma_collection, embed_model)
        return index, True

    # Step 3: Process new document
    logger.info(f"🔄 Processing new document...")
    doc = parser.parse(file_path)

    # Step 4: Create chunks with hash
    nodes = create_chunks_from_document(
        chunker = chunker,
        doc = doc,
        company_name = company_name,
        document_name = document_name,
        document_hash = file_hash
    )

    # Step 5: Add to vector database
    index = add_chunks_to_vectordb(chroma_collection, embed_model, nodes)

    logger.info(f"✅ Document processing completed!")
    return index, False