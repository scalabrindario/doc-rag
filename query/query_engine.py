"""
Query engine setup and execution.
"""
from llama_index.llms.groq import Groq
from llama_index.core import PromptTemplate, Settings
from llama_index.core.postprocessor import SentenceTransformerRerank

from config.logging_config import get_logger

logger = get_logger(__name__)


def setup_query_engine(
        index,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        similarity_top_k: int = 10,
        reranker_top_n: int = 3
):
    """
    Configure query engine with LLM and reranker.

    Args:
        index: VectorStoreIndex instance
        api_key: Groq API key
        model: Model name to use
        similarity_top_k: Number of similar chunks to retrieve
        reranker_top_n: Number of chunks after reranking

    Returns:
        QueryEngine: Configured query engine
    """
    logger.info("🤖 Setting up query engine...")

    # Configure the model
    Settings.llm = Groq(model = model, api_key = api_key)

    # Define a strict prompt
    strict_prompt_str = (
        "You are a virtual assistant who responds solely based on the documents provided.\n"
        "STRICT RULES:\n"
        "1. Use ONLY the information contained in the CONTEXT provided below.\n"
        "2. If the answer is not present in the context, respond exactly: "
        "'I'm sorry, but this information is not present in the uploaded documents.'\n"
        "3. Do not use your outside knowledge or facts not present in the text.\n"
        "4. If you encounter tabular data, analyze it precisely line by line.\n"
        "CONTEXT:\n{context_str}\n\n"
        "QUESTION: {query_str}\n\n"
    )
    strict_prompt = PromptTemplate(strict_prompt_str)

    # Add a reranker to improve relevance ordering
    reranker = SentenceTransformerRerank(
        model = "cross-encoder/ms-marco-MiniLM-L-2-v2",
        top_n = reranker_top_n
    )

    query_engine = index.as_query_engine(
        llm = Settings.llm,
        similarity_top_k = similarity_top_k,
        text_qa_template = strict_prompt,
        node_postprocessors = [reranker],
    )

    logger.info("✅ Query engine ready")
    return query_engine


def execute_query_with_sources(query_engine, query_text: str, max_sources: int = 3) -> str:
    """
    Execute query and return response with source citations.

    Args:
        query_engine: Configured query engine
        query_text: Query string
        max_sources: Maximum number of sources to cite

    Returns:
        str: Response with citations
    """
    logger.info(f"🔍 Executing query: {query_text[:100]}...")

    # Execute the query
    response = query_engine.query(query_text)

    # Extract unique sources from response
    if hasattr(response, 'source_nodes'):
        sources = []
        seen_pages = set()

        for node in response.source_nodes:
            page = node.metadata.get('page_number')
            doc_name = node.metadata.get('document_name')
            company_name = node.metadata.get('company_name')

            # Create unique identifier
            source_id = f"{doc_name}_{page}"

            if source_id not in seen_pages:
                sources.append({
                    'document': doc_name,
                    'page': page,
                    'company_name': company_name,
                    'score': node.score
                })
                seen_pages.add(source_id)

        # Sort by relevance score
        sources.sort(key=lambda x: x['score'], reverse=True)

        # Format citation string
        citation_str = "\n\n📚 Sources:\n"
        for i, source in enumerate(sources[:max_sources], 1):
            citation_str += f"{i}. {source['company_name']}{' - '}{source['document']}, Page {source['page']}\n"

        if str(response) == "I'm sorry, but this information is not present in the uploaded documents.":
            enhanced_response = str(response)
        else:
            enhanced_response = str(response) + citation_str

        logger.info("✅ Query completed")
        return enhanced_response

    return str(response)