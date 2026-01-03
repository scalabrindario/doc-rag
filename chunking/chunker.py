"""
Document chunking with enriched metadata.
"""
from datetime import datetime
from typing import Any, List

from docling.chunking import HybridChunker
from docling_core.transforms.chunker.tokenizer.huggingface import HuggingFaceTokenizer
from llama_index.core.schema import TextNode
from transformers import AutoTokenizer

from config.logging_config import get_logger

logger = get_logger(__name__)


def setup_chunker(
        max_tokens_tokenizer: int = 512,
        embed_model_id: str = "sentence-transformers/all-MiniLM-L6-v2",
        max_tokens_chunker: int = 512,
        merge_peers: bool = True
) -> HybridChunker:
    """
    Configure tokenizer and chunker.

    Args:
        max_tokens_tokenizer: Max tokens for tokenizer
        embed_model_id: HuggingFace model ID for tokenization
        max_tokens_chunker: Max tokens per chunk
        merge_peers: Whether to merge peer chunks

    Returns:
        HybridChunker: Configured chunker instance
    """
    logger.info("🔪 Configuring chunker...")

    tokenizer = HuggingFaceTokenizer(
        tokenizer=AutoTokenizer.from_pretrained(embed_model_id),
        max_tokens=max_tokens_tokenizer,
    )

    chunker = HybridChunker(
        tokenizer=tokenizer,
        max_tokens=max_tokens_chunker,
        merge_peers=merge_peers,
    )
    logger.info(
        f"✅ Chunker configured:\n"
    )

    return chunker


def create_chunks_from_document(
        chunker: HybridChunker,
        doc: Any,
        company_name: str,
        document_name: str,
        document_hash: str
) -> List[TextNode]:
    """
    Create TextNode chunks from Docling document with enriched metadata.

    Args:
        chunker: Configured HybridChunker instance
        doc: Parsed Docling document
        company_name: Name of the company
        document_name: Name of the document
        document_hash: Hash of the document

    Returns:
        List[TextNode]: List of TextNode chunks with metadata
    """
    logger.info(f"🔪 Chunking document...")

    nodes = []

    for i, chunk in enumerate(chunker.chunk(doc)):
        # Extract page number
        page_no = None
        if chunk.meta.doc_items and chunk.meta.doc_items[0].prov:
            page_no = chunk.meta.doc_items[0].prov[0].page_no

        # Extract headings
        headings = []
        if chunk.meta.headings:
            headings = [h for h in chunk.meta.headings]

        # Create enriched metadata
        enriched_metadata = {
            # Company identification
            "company_name": company_name,

            # Document identification
            "document_name": document_name,
            "document_hash": document_hash,

            # Content localization
            "page_number": page_no,
            "chunk_index": i,

            # Context awareness
            "section": ", ".join(headings) if headings else "",

            # Temporal tracking
            "processed_at": datetime.now().isoformat(),
        }

        # Create TextNode
        node = TextNode(
            text=chunk.text,
            metadata=enriched_metadata,
            id_=f"{company_name}_{document_name}_{document_hash[:8]}_{i}"
        )

        nodes.append(node)

    logger.info(f"✅ {len(nodes)} chunks created")
    return nodes
