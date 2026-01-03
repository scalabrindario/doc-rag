"""
FastAPI backend server for the Document Processing RAG system.
"""

from fastapi import FastAPI, File, UploadFile, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
from pathlib import Path
import tempfile
import shutil
from dotenv import load_dotenv

# Server is in the root of document_processing, so modules are directly accessible
project_root = Path(__file__).parent.absolute()
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Load environment variables
load_dotenv()

# Import existing modules
from config.logging_config import get_logger
from chunking.chunker import setup_chunker
from parsing.parser_factory import get_parser
from database.vectordb import setup_chromadb, setup_embedding_model
from database.operations import load_existing_index
from pipeline.processor import process_document_with_deduplication
from query.query_engine import setup_query_engine, execute_query_with_sources
import chromadb

logger = get_logger(__name__)

# Initialize FastAPI app
app = FastAPI(title="Document Processing RAG API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
CHROMA_DB_PATH = str(project_root / "chroma_db")
COLLECTION_NAME = "uploaded_docs"

# Global variables to cache initialized components
_query_engine = None
_embed_model = None
_chroma_collection = None


# Pydantic models
class QueryRequest(BaseModel):
    query: str
    similarity_top_k: Optional[int] = 10
    reranker_top_n: Optional[int] = 3
    max_sources: Optional[int] = 3


class QueryResponse(BaseModel):
    response: str
    sources: List[str]
    status: str


class DocumentInfo(BaseModel):
    company: str
    document: str


class UploadResponse(BaseModel):
    status: str
    message: str
    processed: int
    skipped: int
    failed: int


# Initialize components on startup
@app.on_event("startup")
async def startup_event():
    """Initialize components when the server starts."""
    global _chroma_collection, _embed_model, _query_engine

    try:
        logger.info("🚀 Initializing server components...")

        # Initialize ChromaDB
        _chroma_collection = setup_chromadb(chroma_db_pathname=CHROMA_DB_PATH)

        # Initialize embedding model
        _embed_model = setup_embedding_model()

        # Initialize query engine
        if GROQ_API_KEY:
            index = load_existing_index(_chroma_collection, _embed_model)
            _query_engine = setup_query_engine(
                index=index,
                api_key=GROQ_API_KEY,
                similarity_top_k=10,
                reranker_top_n=3
            )
            logger.info("✅ Query engine initialized successfully")
        else:
            logger.warning("⚠️ GROQ_API_KEY not found. Query functionality will be limited.")

        logger.info("✅ Server startup complete")

    except Exception as e:
        logger.error(f"❌ Error during startup: {str(e)}", exc_info=True)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Check if the server is running and components are initialized."""
    return {
        "status": "healthy",
        "query_engine_ready": _query_engine is not None,
        "database_path": CHROMA_DB_PATH
    }


# Query endpoint
@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """
    Query the vector database with a question.
    """
    try:
        if not _query_engine:
            raise HTTPException(
                status_code=503,
                detail="Query engine not initialized. Please check GROQ_API_KEY."
            )

        logger.info(f"📝 Processing query: {request.query}")

        # Execute query
        response_text = execute_query_with_sources(
            query_engine=_query_engine,
            query_text=request.query,
            max_sources=request.max_sources
        )

        # Extract sources from response (simple parsing)
        sources = []
        if "**Sources:**" in response_text or "📚 Sources:" in response_text:
            # Handle both English and emoji versions
            separator = "**Sources:**" if "**Sources:**" in response_text else "📚 Sources:"
            sources_section = response_text.split(separator)[1].strip()
            sources = [line.strip("- ").strip() for line in sources_section.split("\n") if line.strip() and (line.strip().startswith("-") or line.strip()[0].isdigit())]

        logger.info("✅ Query completed successfully")

        return QueryResponse(
            response=response_text,
            sources=sources,
            status="success"
        )

    except Exception as e:
        logger.error(f"❌ Error during query: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# List documents endpoint
@app.get("/api/documents", response_model=List[DocumentInfo])
async def list_documents():
    """
    Retrieve a list of all documents in the database.
    """
    try:
        logger.info("📚 Fetching document list...")

        # Use already initialized collection instead of creating a new client
        if not _chroma_collection:
            raise HTTPException(
                status_code=503,
                detail="Database not initialized"
            )

        # Retrieve metadata
        results = _chroma_collection.get(include=["metadatas"])
        metadatas = results.get('metadatas', [])

        if not metadatas:
            logger.info("No documents found in database")
            return []

        # Extract unique documents
        unique_docs = {}
        for meta in metadatas:
            company = meta.get('company_name', 'Unknown')
            doc_name = meta.get('document_name', 'Unknown')
            key = f"{company}|{doc_name}"
            unique_docs[key] = DocumentInfo(company=company, document=doc_name)

        document_list = list(unique_docs.values())
        logger.info(f"✅ Found {len(document_list)} unique documents")

        return document_list

    except Exception as e:
        logger.error(f"❌ Error fetching documents: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Upload endpoint
@app.post("/api/upload", response_model=UploadResponse)
async def upload_documents(
    files: List[UploadFile] = File(...),
    company_names: str = Form(...),
    document_names: str = Form(...)
):
    """
    Upload and process documents into the vector database.

    Args:
        files: List of PDF files to upload
        company_names: Comma-separated list of company names
        document_names: Comma-separated list of document names
    """
    try:
        logger.info(f"📤 Received {len(files)} files for upload")

        # Parse metadata
        companies = [c.strip() for c in company_names.split(',')]
        doc_names = [d.strip() for d in document_names.split(',')]

        if len(files) != len(companies) or len(files) != len(doc_names):
            raise HTTPException(
                status_code=400,
                detail="Number of files must match number of company names and document names"
            )

        # Initialize components
        chroma_collection = setup_chromadb(chroma_db_pathname=CHROMA_DB_PATH)
        embed_model = setup_embedding_model()
        chunker = setup_chunker()

        processed = 0
        skipped = 0
        failed = 0

        # Process each file
        for file, company, doc_name in zip(files, companies, doc_names):
            try:
                logger.info(f"📄 Processing: {file.filename}")

                # Validate file type
                if not file.filename.endswith('.pdf'):
                    logger.warning(f"Skipping non-PDF file: {file.filename}")
                    failed += 1
                    continue

                # Save file to temporary location
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
                    shutil.copyfileobj(file.file, tmp_file)
                    tmp_path = tmp_file.name

                try:
                    # Get parser for the document
                    parser = get_parser(tmp_path)

                    # Process document
                    index, was_skipped = process_document_with_deduplication(
                        file_path=tmp_path,
                        company_name=company,
                        document_name=doc_name,
                        chroma_collection=chroma_collection,
                        parser=parser,
                        chunker=chunker,
                        embed_model=embed_model
                    )

                    if was_skipped:
                        logger.info(f"Document already exists: {doc_name}")
                        skipped += 1
                    else:
                        logger.info(f"✅ Successfully processed: {doc_name}")
                        processed += 1

                finally:
                    # Clean up temporary file
                    os.unlink(tmp_path)

            except Exception as e:
                logger.error(f"❌ Failed to process {file.filename}: {str(e)}")
                failed += 1
                continue

        # Reinitialize query engine with updated index
        global _query_engine
        if GROQ_API_KEY:
            index = load_existing_index(chroma_collection, embed_model)
            _query_engine = setup_query_engine(
                index=index,
                api_key=GROQ_API_KEY,
                similarity_top_k=10,
                reranker_top_n=3
            )

        message = f"Upload complete: {processed} processed, {skipped} skipped, {failed} failed"
        logger.info(message)

        return UploadResponse(
            status="success",
            message=message,
            processed=processed,
            skipped=skipped,
            failed=failed
        )

    except Exception as e:
        logger.error(f"❌ Error during upload: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    print("=" * 80)
    print("🚀 Starting Document Processing RAG API Server")
    print("=" * 80)
    print(f"📁 Database path: {CHROMA_DB_PATH}")
    print(f"🔑 API Key configured: {bool(GROQ_API_KEY)}")
    print("=" * 80)

    uvicorn.run(
        "api_server:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )