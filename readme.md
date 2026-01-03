# Document Processing RAG System

A full-stack Retrieval-Augmented Generation (RAG) system for processing, indexing, and querying PDF documents using vector embeddings and LLM-powered responses.

![Python](https://img.shields.io/badge/python-3.11+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## 🌟 Features

- **📄 PDF Processing**: Automatic parsing and chunking of PDF documents
- **🔍 Semantic Search**: Vector-based similarity search using ChromaDB
- **💬 Conversational Interface**: Chat-like UI for querying documents
- **📤 Easy Upload**: Drag-and-drop interface for adding new documents
- **📚 Document Management**: View and track all indexed documents
- **🎯 Source Citations**: Automatic source attribution for all responses
- **⚡ Fast Retrieval**: Optimized indexing and reranking for accurate results

## 🏗️ Architecture

```
┌─────────────────┐
│  React Frontend │
│   (Port 3000)   │
└────────┬────────┘
         │
         │ HTTP/REST
         │
┌────────▼────────┐
│  FastAPI Backend│
│   (Port 8000)   │
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼────┐
│Groq  │  │Chroma │
│ LLM  │  │  DB   │
└──────┘  └───────┘
```

## 📁 Project Structure

```
document_processing/
├── api_server.py              # FastAPI backend server
├── frontend/
│   └── index.html            # React web interface
├── scripts/
│   ├── query_documents.py    # CLI query interface
│   ├── ingest_documents.py   # Document ingestion script
│   └── show_loaded_docs.py   # List indexed documents
├── chunking/
│   └── chunker.py            # Document chunking logic
├── config/
│   └── logging_config.py     # Logging configuration
├── database/
│   ├── vectordb.py           # ChromaDB setup
│   └── operations.py         # Database operations
├── parsing/
│   ├── pdf_parser.py         # PDF parsing
│   ├── docx_parser.py        # DOCX parsing
│   ├── txt_parser.py         # Text file parsing
│   └── parser_factory.py     # Parser selection logic
├── pipeline/
│   └── processor.py          # Document processing pipeline
├── query/
│   └── query_engine.py       # Query execution engine
├── utils/
│   ├── deduplication.py      # Duplicate detection
│   └── file_hash.py          # File hashing utilities
├── chroma_db/                # Vector database storage
├── .env                      # Environment variables
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### Prerequisites

- Python 3.11 or higher
- pip package manager
- A Groq API key ([Get one here](https://console.groq.com/))

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/scalabrindario/doc-rag.git
cd doc-rag
```

2. **Create and activate virtual environment**
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
# Create .env file
echo "GROQ_API_KEY=your_groq_api_key_here" > .env
```

### Running the Application

1. **Start the backend server**
```bash
python api_server.py
```

The server will start on `http://localhost:8000`

2. **Start the frontend** (in a new terminal)
```bash
cd frontend
python -m http.server 3000
```

3. **Open your browser**

Navigate to `http://localhost:3000`

## 📖 Usage

### Web Interface

#### 1. Query Documents
- Navigate to the "Query Documents" tab
- Type your question in the input field
- Press Enter or click "Send"
- View the AI-generated response with source citations

#### 2. Upload Documents
- Navigate to the "Upload Documents" tab
- Click or drag PDF files to upload
- Fill in the source/category and document name
- Click "Upload and Process Documents"
- Wait for processing to complete

#### 3. View Documents
- Navigate to the "View Documents" tab
- See all documents currently indexed in the database
- Check document status and metadata

### Command Line Interface

#### Query documents via CLI
```bash
python scripts/query_documents.py
```

#### Ingest documents via CLI
```bash
# Edit the script to add your document paths
python scripts/ingest_documents.py
```

#### List all documents
```bash
python scripts/show_loaded_docs.py
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

### Chunking Parameters

Edit `chunking/chunker.py` to adjust:
- Chunk size
- Chunk overlap
- Sentence splitting behavior

### Query Parameters

Adjust in API calls or `query_engine.py`:
- `similarity_top_k`: Number of chunks to retrieve (default: 10)
- `reranker_top_n`: Number of chunks after reranking (default: 3)
- `max_sources`: Maximum sources to cite (default: 3)

## 🛠️ API Endpoints

### Health Check
```http
GET /health
```

### Query Documents
```http
POST /api/query
Content-Type: application/json

{
  "query": "What are the main topics?",
  "similarity_top_k": 10,
  "reranker_top_n": 3,
  "max_sources": 3
}
```

### List Documents
```http
GET /api/documents
```

### Upload Documents
```http
POST /api/upload
Content-Type: multipart/form-data

files: [PDF files]
company_names: "Category1,Category2"
document_names: "Doc1,Doc2"
```

## 🧪 Testing

### Test Backend Health
```bash
curl http://localhost:8000/health
```

### Test Document List
```bash
curl http://localhost:8000/api/documents
```

### Test Query
```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "What is this about?"}'
```

## 📊 Technologies Used

### Backend
- **FastAPI**: Modern web framework for building APIs
- **ChromaDB**: Vector database for embeddings
- **LlamaIndex**: Framework for building LLM applications
- **Groq**: Fast LLM inference
- **BGE Embeddings**: Sentence embeddings model

### Frontend
- **React**: UI library
- **TailwindCSS**: Utility-first CSS framework
- **Babel**: JavaScript transpiler

### Document Processing
- **PyMuPDF**: PDF parsing
- **python-docx**: Word document parsing
- **Semantic chunking**: Intelligent text splitting

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [LlamaIndex](https://www.llamaindex.ai/) for the RAG framework
- [ChromaDB](https://www.trychroma.com/) for vector storage
- [Groq](https://groq.com/) for fast LLM inference
- [FastAPI](https://fastapi.tiangolo.com/) for the backend framework

## 🐛 Known Issues

- Large PDF files (>50MB) may take significant time to process
- Currently only supports PDF documents (DOCX and TXT support coming soon)
- Memory usage scales with database size

## 🗺️ Roadmap

- [ ] Add support for more document formats (DOCX, TXT, HTML)
- [ ] Implement document deletion functionality
- [ ] Add user authentication and multi-user support
- [ ] Deploy to cloud (AWS/GCP/Azure)
- [ ] Add batch query processing
- [ ] Implement document versioning
- [ ] Add advanced filtering options
- [ ] Create Docker containerization

---

Made with ❤️ by [Dario Scalabrin]
