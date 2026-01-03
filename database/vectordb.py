"""
Vector database setup with ChromaDB.
"""
import chromadb
from chromadb.config import Settings
from llama_index.core import Settings as LlamaSettings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

from config.logging_config import get_logger

logger = get_logger(__name__)


def setup_chromadb(
        chroma_db_pathname: str = "./chroma_db",
        collection_name: str = "uploaded_docs"
):
    """
    Initialize ChromaDB client and collection.

    Args:
        chroma_db_pathname: Path to ChromaDB storage
        collection_name: Name of the collection

    Returns:
        Collection: ChromaDB collection instance
    """
    logger.info("🚀 Initializing ChromaDB...")

    chroma_client = chromadb.PersistentClient(
        path = chroma_db_pathname,
        settings = Settings(anonymized_telemetry = False)
    )
    logger.info(f"✅ ChromaDB client initialized ({chroma_db_pathname})")

    try:
        chroma_collection = chroma_client.get_collection(name = collection_name)
        logger.info(f"✅ Collection '{collection_name}' retrieved")
    except:
        chroma_collection = chroma_client.create_collection(
            name = collection_name,
            metadata = {"description": "Documents with enriched metadata"}
        )
        logger.info(f"✅ Collection '{collection_name}' created")

    return chroma_collection


def setup_embedding_model(embed_model_id: str = "BAAI/bge-base-en-v1.5"):
    """
    Configure embedding model.

    Args:
        embed_model_id: HuggingFace model ID for embeddings

    Returns:
        HuggingFaceEmbedding: Configured embedding model
    """
    logger.info("🤖 Configuring embedding model...")

    embed_model = HuggingFaceEmbedding(model_name = embed_model_id)
    LlamaSettings.embed_model = embed_model

    logger.info(f"✅ Embedding model configured: {embed_model_id}")

    return embed_model
