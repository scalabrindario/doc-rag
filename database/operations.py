"""
Database operations for adding and retrieving data.
"""
from typing import List

from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import VectorStoreIndex, StorageContext
from llama_index.core.schema import TextNode

from config.logging_config import get_logger

logger = get_logger(__name__)


def add_chunks_to_vectordb(chroma_collection, embed_model, nodes: List[TextNode]) -> VectorStoreIndex:
    """
    Add TextNode chunks to vector database.

    Args:
        chroma_collection: ChromaDB collection instance
        embed_model: Configured embedding model
        nodes: List of TextNode chunks

    Returns:
        VectorStoreIndex: Index for querying
    """
    logger.info(f"💾 Adding {len(nodes)} chunks to vector database...")

    vector_store = ChromaVectorStore(chroma_collection = chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store = vector_store)

    index = VectorStoreIndex(
        nodes = nodes,
        storage_context = storage_context,
        embed_model = embed_model,
        show_progress = True
    )

    logger.info(f"✅ Chunks successfully added to database!")
    return index


def load_existing_index(chroma_collection, embed_model) -> VectorStoreIndex:
    """
    Load existing index from ChromaDB.

    Args:
        chroma_collection: ChromaDB collection instance
        embed_model: Configured embedding model

    Returns:
        VectorStoreIndex: Loaded index
    """
    logger.info("📂 Loading existing index from database...")

    vector_store = ChromaVectorStore(chroma_collection = chroma_collection)
    # storage_context = StorageContext.from_defaults(vector_store = vector_store)

    index = VectorStoreIndex.from_vector_store(
        vector_store = vector_store,
        embed_model = embed_model
    )

    logger.info("✅ Index loaded successfully")
    return index