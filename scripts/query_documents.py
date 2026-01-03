"""
Script for querying documents from the vector database.
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# Add the project root directory to the python path
project_root = Path(__file__).parent.parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

from config.logging_config import get_logger
from database.vectordb import setup_chromadb, setup_embedding_model
from database.operations import load_existing_index
from query.query_engine import setup_query_engine, execute_query_with_sources

logger = get_logger(__name__)


def query_database(
        query_text: str,
        groq_api_key: Optional[str] = None,
        chroma_db_path: str = "./chroma_db",
        similarity_top_k: int = 10,
        reranker_top_n: int = 3,
        max_sources: int = 3,
        verbose: bool = True
) -> str:
    """
    Query the vector database with a question.

    Args:
        query_text: The question to ask
        groq_api_key: API key for Groq (uses env var if not provided)
        chroma_db_path: Path to ChromaDB storage
        similarity_top_k: Number of similar chunks to retrieve
        reranker_top_n: Number of chunks after reranking
        max_sources: Maximum number of sources to cite
        verbose: If True, print progress messages

    Returns:
        str: The response with citations

    Raises:
        ValueError: If API key is not found
        Exception: For other processing errors
    """

    try:
        # Validate API key
        api_key = groq_api_key or GROQ_API_KEY
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please set it in .env file or pass as argument"
            )

        if verbose:
            logger.info("🚀 Initializing query engine...")
            print("🚀 Initializing query engine...")

        # Initialize components
        chroma_collection = setup_chromadb(chroma_db_pathname = chroma_db_path)

        embed_model = setup_embedding_model()

        # Load existing index
        if verbose:
            logger.info("📂 Loading document index...")
            print("📂 Loading document index...")

        index = load_existing_index(chroma_collection, embed_model)

        # Setup query engine
        query_engine = setup_query_engine(
            index = index,
            api_key = api_key,
            similarity_top_k = similarity_top_k,
            reranker_top_n = reranker_top_n
        )

        # Execute query
        if verbose:
            logger.info(f"🔍 Executing query: {query_text}")
            print(f"\n🔍 Query: {query_text}\n")

        response = execute_query_with_sources(
            query_engine = query_engine,
            query_text = query_text,
            max_sources = max_sources
        )

        if verbose:
            print("=" * 80)
            print("RESPONSE:")
            print("=" * 80)
            print(response)
            print("=" * 80 + "\n")

        logger.info("✅ Query completed successfully")
        return response

    except Exception as e:
        logger.error(f"❌ Error during query: {str(e)}", exc_info=True)
        print(f"❌ Error: {str(e)}")
        raise


def interactive_query_mode(
        groq_api_key: Optional[str] = None,
        chroma_db_path: str = "./chroma_db"
):
    """
    Start an interactive query session.

    Args:
        groq_api_key: API key for Groq (uses env var if not provided)
        chroma_db_path: Path to ChromaDB storage
    """

    print("\n" + "=" * 80)
    print("INTERACTIVE QUERY MODE")
    print("=" * 80)
    print("Type your questions below. Type 'exit' or 'quit' to end the session.")
    print("=" * 80 + "\n")

    # Initialize components once
    api_key = groq_api_key or GROQ_API_KEY
    if not api_key:
        print("❌ Error: GROQ_API_KEY not found")
        return

    print("🚀 Initializing query engine...")
    chroma_collection = setup_chromadb(chroma_db_pathname = chroma_db_path)
    embed_model = setup_embedding_model()
    index = load_existing_index(chroma_collection, embed_model)
    query_engine = setup_query_engine(index = index, api_key = api_key)
    print("✅ Ready for queries!\n")

    while True:
        try:
            # Get user input
            query_text = input("❓ Your question: ").strip()

            # Check for exit commands
            if query_text.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Goodbye!")
                break

            # Skip empty queries
            if not query_text:
                continue

            # Execute query
            print()
            response = execute_query_with_sources(
                query_engine = query_engine,
                query_text = query_text,
                max_sources = 3
            )

            print("=" * 80)
            print("RESPONSE:")
            print("=" * 80)
            print(response)
            print("=" * 80 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")
            continue


def batch_query(
        queries: List[str],
        groq_api_key: Optional[str] = None,
        chroma_db_path: str = "./chroma_db",
        collection_name: str = "uploaded_docs",
        output_file: Optional[str] = None
) -> List[dict]:
    """
    Execute multiple queries in batch mode.

    Args:
        queries: List of query strings
        groq_api_key: API key for Groq (uses env var if not provided)
        chroma_db_path: Path to ChromaDB storage
        collection_name: Name of the ChromaDB collection
        output_file: Optional file path to save results

    Returns:
        List of dicts with 'query' and 'response' keys
    """

    results = []

    logger.info(f"📋 Starting batch query of {len(queries)} questions")
    print(f"\n📋 Starting batch query of {len(queries)} questions\n")

    for i, query_text in enumerate(queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Query {i}/{len(queries)}")
        print(f"{'=' * 80}")

        try:
            response = query_database(
                query_text = query_text,
                groq_api_key = groq_api_key,
                chroma_db_path = chroma_db_path,
                verbose = True
            )

            results.append({
                'query': query_text,
                'response': response,
                'status': 'success'
            })

        except Exception as e:
            logger.error(f"Failed query {i}: {str(e)}")
            results.append({
                'query': query_text,
                'response': f"Error: {str(e)}",
                'status': 'failed'
            })

    # Save to file if requested
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            for i, result in enumerate(results, 1):
                f.write(f"\n{'=' * 80}\n")
                f.write(f"Query {i}: {result['query']}\n")
                f.write(f"{'=' * 80}\n")
                f.write(f"{result['response']}\n")
        print(f"\n💾 Results saved to: {output_file}")

    return results


def main(query_text : str):
    """Main execution for querying documents."""

    groq_api_key_override = None  # Set to override .env

    # Config Database folder
    chroma_db_parent_folder = Path(__file__).parents[1]
    chroma_db_final_folder = "/chroma_db"
    chroma_db_path = f"{chroma_db_parent_folder}{chroma_db_final_folder}"

    # Option 1: Single query
    response = query_database(
        query_text = query_text,
        groq_api_key = groq_api_key_override,
        chroma_db_path = chroma_db_path
    )


if __name__ == "__main__":
    query_text = "what is the dNPS mentioned in the Allianz report?"
    main(query_text)