"""
Script for ingesting and processing documents into the vector database.
"""

import sys
import os
from pathlib import Path
from typing import Optional, List
from dotenv import load_dotenv

# Add the project root directory to the python path
project_root = Path(__file__).parent.parent.absolute()
sys.path.append(str(project_root))

if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

from config.logging_config import get_logger
from chunking.chunker import setup_chunker
from parsing.parser_factory import get_parser
from database.vectordb import setup_chromadb, setup_embedding_model
from pipeline.processor import process_document_with_deduplication

logger = get_logger(__name__)


def ingest_document(
        document_path: str,
        company_name: str,
        document_name: str,
        chroma_db_path: str = "./chroma_db",
        force_reprocess: bool = False
) -> bool:
    """
    Ingest a single document into the vector database.

    Args:
        document_path: Path to the document to process
        company_name: Name of the company (for metadata)
        document_name: Name of the document (for metadata)
        chroma_db_path: Path to ChromaDB storage
        force_reprocess: If True, reprocess even if document exists

    Returns:
        bool: True if document was processed, False if skipped

    Raises:
        FileNotFoundError: If document doesn't exist
        Exception: For other processing errors
    """

    try:
        # Validate document exists
        if not Path(document_path).exists():
            raise FileNotFoundError(f"Document not found: {document_path}")

        logger.info(f"🚀 Starting document ingestion: {Path(document_path).name}")
        print(f"🚀 Starting document ingestion: {Path(document_path).name}")

        # Initialize components
        logger.info("⚙️ Initializing components...")
        print("⚙️ Initializing components...")

        chroma_collection = setup_chromadb(chroma_db_pathname = chroma_db_path)

        parser = get_parser(document_path)
        chunker = setup_chunker()
        embed_model = setup_embedding_model()

        # Process document
        logger.info(f"📄 Processing: {document_name}")
        print(f"📄 Processing: {document_name}")

        index, was_skipped = process_document_with_deduplication(
            file_path = document_path,
            company_name = company_name,
            document_name = document_name,
            chroma_collection = chroma_collection,
            parser = parser,
            chunker = chunker,
            embed_model = embed_model
        )

        if was_skipped:
            logger.info("📋 Document already in database")
            print("📋 Document already in database - skipped")
            return False
        else:
            logger.info("✅ Document successfully ingested")
            print("✅ Document successfully ingested into database")
            return True

    except Exception as e:
        logger.error(f"❌ Error during ingestion: {str(e)}", exc_info=True)
        print(f"❌ Error: {str(e)}")
        raise


def ingest_multiple_documents(
        documents: List[dict],
        chroma_db_path: str = "./chroma_db"
) -> dict:
    """
    Ingest multiple documents into the vector database.

    Args:
        documents: List of dicts with keys: 'path', 'company_name', 'document_name'
        chroma_db_path: Path to ChromaDB storage

    Returns:
        dict: Summary with 'processed', 'skipped', 'failed' counts
    """

    summary = {
        'processed': 0,
        'skipped': 0,
        'failed': 0,
        'total': len(documents)
    }

    logger.info(f"📚 Starting batch ingestion of {len(documents)} documents")
    print(f"\n📚 Starting batch ingestion of {len(documents)} documents\n")

    for i, doc in enumerate(documents, 1):
        print(f"\n{'=' * 80}")
        print(f"Document {i}/{len(documents)}")
        print(f"{'=' * 80}")

        try:
            was_processed = ingest_document(
                document_path = doc['path'],
                company_name = doc['company_name'],
                document_name = doc['document_name'],
                chroma_db_path = chroma_db_path
            )

            if was_processed:
                summary['processed'] += 1
            else:
                summary['skipped'] += 1

        except Exception as e:
            logger.error(f"Failed to process {doc['path']}: {str(e)}")
            summary['failed'] += 1
            continue

    # Print summary
    print(f"\n{'=' * 80}")
    print("INGESTION SUMMARY")
    print(f"{'=' * 80}")
    print(f"✅ Processed: {summary['processed']}")
    print(f"⏭️  Skipped:   {summary['skipped']}")
    print(f"❌ Failed:    {summary['failed']}")
    print(f"📊 Total:     {summary['total']}")
    print(f"{'=' * 80}\n")

    return summary


def ingest_doc_init(path_names_list = list,
                    company_name_list = list,
                    doc_name_list = list,
                    chroma_db_path: str = "./chroma_db"):
    """Main execution for document ingestion."""

    documents_to_ingest = []

    # Passing all the information of all the documents to parse
    for path, c_name, doc_name in zip(path_names_list, company_name_list, doc_name_list):

        single_doc_to_add = {}

        # Add info of a single document
        single_doc_to_add.update({
            'path': path,
            'company_name': c_name,
            'document_name': doc_name
        })

        documents_to_ingest.append(single_doc_to_add)

    # Ingest multiple documents (uncomment to use)
    summary = ingest_multiple_documents(
         documents = documents_to_ingest,
         chroma_db_path = chroma_db_path
    )


if __name__ == "__main__":

    # Config Database folder
    chroma_db_parent_folder = Path(__file__).parents[1]
    chroma_db_final_folder = "/chroma_db"

    chroma_db_path = f"{chroma_db_parent_folder}{chroma_db_final_folder}"

    print(chroma_db_path)

    input_path_names_list = [
        "/Users/scalabrindario/Library/Mobile Documents/com~apple~CloudDocs/Artificial Intelligence/Investor Relations/Benchmarking/Allianz/annual-report-2024.pdf",
        "/Users/scalabrindario/Library/Mobile Documents/com~apple~CloudDocs/Artificial Intelligence/Investor Relations/Benchmarking/AXA/annual-report-2024.pdf",
        "/Users/scalabrindario/Library/Mobile Documents/com~apple~CloudDocs/Artificial Intelligence/Investor Relations/Benchmarking/Chubb/annual-report-2024.pdf",
        "/Users/scalabrindario/Library/Mobile Documents/com~apple~CloudDocs/Artificial Intelligence/Investor Relations/Benchmarking/Generali/annual-report-2024.pdf",
        "/Users/scalabrindario/Library/Mobile Documents/com~apple~CloudDocs/Artificial Intelligence/Investor Relations/Benchmarking/Zurich Insurance/annual-report-2024.pdf"
    ]
    input_company_name_list = [
        "Allianz",
        "Axa",
        "Chubb",
        "Generali",
        "Zurich Insurance",

    ]

    input_doc_name_list = [
        "Annual Report 2024",
        "Annual Report 2024",
        "Annual Report 2024",
        "Annual Report 2024",
        "Annual Report 2024"
    ]

    ingest_doc_init(input_path_names_list, input_company_name_list, input_doc_name_list, chroma_db_path)

