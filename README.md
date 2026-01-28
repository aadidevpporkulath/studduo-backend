# StudduoAI Backend

A multi-domain RAG-based tutoring chatbot API designed to provide teaching-focused responses and student learning support.

## Overview

StudduoAI Backend is a FastAPI-based application that powers an intelligent tutoring system. It leverages Retrieval-Augmented Generation (RAG) with vector databases and Google Gemini to deliver personalized educational responses across multiple domains.

## Key Features

- **FastAPI REST API** - High-performance async web framework
- **RAG System** - Retrieval-Augmented Generation for contextual responses
- **Vector Database** - ChromaDB for efficient semantic search
- **PDF Processing** - Document ingestion with OCR capabilities using Tesseract
- **Firebase Integration** - Authentication and Firestore real-time database
- **Multi-domain Support** - Knowledge base organized across multiple subjects
- **Firestore Database** - Cloud-based storage for conversations, messages, and user interactions
- **Vector Database** - ChromaDB for efficient semantic search of document embeddings

## Project Structure

```txt
studduoai/backend/
├── main.py                    # FastAPI application entry point
├── config.py                  # Configuration and environment settings
├── requirements.txt           # Python dependencies
├── auth.py                    # Authentication logic
├── chat_service.py            # Chat request handling and processing
├── document_processor.py       # PDF and document processing
├── firestore_db.py            # Firestore database integration
├── ingest_documents.py        # Document ingestion pipeline
├── models.py                  # Pydantic data models
├── vector_store.py            # ChromaDB vector store management
├── firebase-credentials.json  # Firebase service account credentials
├── routers/                   # API route handlers
│   ├── chat.py               # Chat endpoint routes
│   └── admin.py              # Administrative endpoints
├── chroma_db/                # Vector database storage
└── knowledge/                # Document knowledge base
```

## Technologies

### Core Framework

- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server with performance optimizations
- **Pydantic** - Data validation and settings management

### AI/ML

- **LangChain** - LLM framework and utilities
- **Google Gemini** - Large language model integration
- **ChromaDB** - Vector database for embeddings

### Document Processing

- **PyPDF** - PDF reading and manipulation
- **pdf2image** - PDF to image conversion
- **Tesseract OCR** - Optical character recognition
- **Pillow** - Image processing

### Database & Storage

- **Firebase Admin** - Authentication and Firestore real-time database
- **Firestore** - Cloud-hosted NoSQL database for conversations and messages

### Utilities

- **python-dotenv** - Environment variable management
- **python-jose** - JWT token handling
- **httpx** - Async HTTP client

## Setup & Installation

### Prerequisites

- Python 3.11+
- Virtual environment (venv)
- Tesseract-OCR installed
- Firebase project with credentials
- Google API key for Gemini

### Installation Steps

1. **Create and activate virtual environment:**

   ```bash
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows PowerShell
   ```

2. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables:**
   Create a `.env` file in the project root:

   ``` env
   GOOGLE_API_KEY=your_google_api_key
   FIREBASE_PROJECT_ID=your_firebase_project_id
   FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
   APP_ENV=development
   API_PORT=8000
   ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
   CHROMA_PERSIST_DIR=./chroma_db
   KNOWLEDGE_DIR=./knowledge
   TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
   OCR_DPI=200
   OCR_GRAYSCALE=true
   ```

4. **Add Firebase credentials:**
   Place your Firebase service account JSON file at `./firebase-credentials.json`

## Running the Application

### Development Mode

```bash
python main.py
```

The API will start at `http://localhost:8000`

### API Documentation

- **Swagger UI**: <http://localhost:8000/docs>
- **ReDoc**: <http://localhost:8000/redoc>

## API Endpoints

### Chat Routes (`routers/chat.py`)

- `POST /chat` - Submit a chat message and receive a response
- `GET /chat/history` - Retrieve chat history

### Admin Routes (`routers/admin.py`)

- `POST /admin/ingest` - Ingest and process documents
- `GET /admin/status` - Check system status
- `POST /admin/reset` - Reset vector store

## Configuration

All settings are managed through environment variables in `config.py`:

| Variable | Default | Description |
| -------- | ------- | ----------- |
| `GOOGLE_API_KEY` | Required | Google Gemini API key |
| `FIREBASE_PROJECT_ID` | Required | Firebase project identifier |
| `APP_ENV` | development | Environment (development/production) |
| `API_PORT` | 8000 | Server port |
| `ALLOWED_ORIGINS` | localhost:3000,5173 | CORS allowed origins |
| `DATABASE_URL` | ./studduoai.db | SQLite database URL |
| `KNOWLEDGE_DIR` | ./knowledge | Knowledge base directory |
| `TESSERACT_CMD` | Program Files path | Tesseract executable location |

## Data Flow

1. **Document Ingestion**: PDFs uploaded to knowledge directory
2. **Processing**: Documents processed with OCR and text extraction
3. **Embedding**: Content embedded into vector store via ChromaDB
4. **User Query**: Chat request received via API
5. **Retrieval**: Relevant documents retrieved from vector store
6. **Generation**: Gemini generates response using retrieved context
7. **Response**: Teaching-focused response returned to user

## Database Schema

 Storage

### Firestore Cloud Database

**Collection Structure:**

- `users/{user_id}/conversations/{conversation_id}` - Conversation metadata
  - `id` - Unique conversation identifier
  - `title` - User-defined conversation title
  - `prompt_type` - Type of responses (explanation, plan, example, summary, problem_solving, quiz)
  - `is_temporary` - Whether conversation is saved permanently
  - `created_at` - Timestamp of creation
  - `updated_at` - Last update timestamp
  - `message_count` - Number of messages in conversation

- `users/{user_id}/conversations/{conversation_id}/messages/{message_id}` - Individual messages
  - `id` - Unique message identifier
  - `role` - Message sender (user or assistant)
  - `content` - Message text
  - `sources` - Referenced documents with chunk IDs and relevance scores
  - `timestamp` - When message was created

### ChromaDB Vector Store

- Document embeddings for semantic search
- Persistent storage in `./chroma_db/`
- Indexed metadata for efficient retrieval
- Cached embeddings from Google Gemini

## Logging

The application logs to stdout with the format:

``` txt
%(asctime)s - %(name)s - %(levelname)s - %(message)s
```

Log level is set to INFO by default.

## Performance Optimization

- **Vector Store Pre-loading**: Vector store initializes on startup to avoid cold starts
- **Async Processing**: Full async/await support for non-blocking operations
- **Connection Pooling**: Database connections pooled for efficiency
- **Embedding Caching**: Embeddings cached in ChromaDB

## Security Considerations

- Firebase authentication validates user requests
- CORS restricted to specified origins
- JWT tokens used for session management
- Environment variables for sensitive configuration
- No credentials committed to repository

## Development

### Code Organization

- **Routers**: API endpoints organized by domain
- **Services**: Business logic separated from routes
- **Models**: Data validation with Pydantic
- **Configuration**: Centralized settings management

### Adding New Features

1. Create route handlers in `routers/`
2. Implement service logic in new files
3. Define data models in `models.py`
4. Update `main.py` to register new routers

## Troubleshooting

### Vector Store Not Initializing

- Check `CHROMA_PERSIST_DIR` exists
- Verify disk space available
- Check logs for initialization errors

### OCR Not Working

- Verify Tesseract installation path
- Check `TESSERACT_CMD` configuration
- Ensure PDF2image dependencies installed

### Firebase Connection Issues

- Validate `firebase-credentials.json` path
- Check Firebase project permissions
- Verify network connectivity
