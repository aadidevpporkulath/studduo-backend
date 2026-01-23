# NoteGPT Backend API

A multi-domain RAG (Retrieval-Augmented Generation) chatbot API for students, designed to provide teaching-focused responses using any subject's course materials.

## 🚀 Features

- **RAG-based Q&A**: Answers questions using your PDF course materials (any subject)
- **Multi-Domain**: Works with any subject - add PDF materials in `./knowledge` folder
- **OCR Support**: Processes both digital and scanned PDFs
- **Teaching-Focused**: Responses designed like a teacher or friend explaining concepts
- **6 Response Types**: Explanation, Plan, Example, Summary, Problem Solving, Quiz
- **Temporary Conversations**: Quick queries that aren't saved to database
- **Chat History**: Stores conversations per user with follow-up context
- **Engaging Interactions**: Asks follow-up questions to deepen understanding
- **Firebase Authentication**: Secure user authentication
- **Free LLM**: Uses Google Gemini (generous free tier)

## 📋 Prerequisites

1. **Python 3.9+**
2. **Tesseract OCR** (for scanned PDFs)
   - Download from: <https://github.com/UB-Mannheim/tesseract/wiki>
   - Install to: `C:\Program Files\Tesseract-OCR\` (default)
3. **Poppler** (for PDF to image conversion)
   - Download from: <https://github.com/oschwartz10612/poppler-windows/releases>
   - Extract and add `bin` folder to PATH
4. **Google Gemini API Key**
   - Get free key from: <https://makersuite.google.com/app/apikey>
5. **Firebase Project**
   - Create project at: <https://console.firebase.google.com>
   - Enable Authentication
   - Download service account JSON

## 🛠️ Installation

### 1. Install Tesseract OCR

```powershell
# Download installer from:
# https://github.com/UB-Mannheim/tesseract/wiki

# Or using Chocolatey:
choco install tesseract
```

### 2. Install Poppler

```powershell
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
# Extract and add bin folder to PATH

# Or add to PATH manually:
$env:PATH += ";C:\path\to\poppler\bin"
```

### 3. Clone and Setup

```powershell
# Navigate to backend directory
cd c:\Users\aadid\Work\notegpt\backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

```powershell
# Copy example env file
cp .env.example .env

# Edit .env with your values
notepad .env
```

**Required `.env` variables:**

```env
# Get from https://makersuite.google.com/app/apikey
GOOGLE_API_KEY=your_gemini_api_key_here

# Your Firebase project details
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json

# CORS - Add your frontend URLs
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# Tesseract path (update if different)
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### 5. Add Firebase Credentials

1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate New Private Key"
3. Save as `firebase-credentials.json` in backend folder

## 📚 Ingest Documents

Before starting the API, you need to process and index your PDF documents:

```powershell
# First time ingestion
python ingest_documents.py

# Force reingest all documents
python ingest_documents.py --force
```

**What this does:**

- Scans all PDFs in the `knowledge/` folder
- Extracts text (uses OCR for scanned PDFs)
- Chunks documents into meaningful pieces
- Generates embeddings using Gemini
- Stores in ChromaDB vector database

⏱️ **Note**: Processing 60+ PDFs might take 10-30 minutes depending on:

- File sizes
- Whether they're scanned (OCR is slower)
- Your internet speed (for embeddings)

## 🚀 Running the API

```powershell
# Activate venv if not already
.\venv\Scripts\Activate.ps1

# Start the server
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --port 8000
```

The API will be available at:

- **API**: <http://localhost:8000>
- **Docs**: <http://localhost:8000/docs>
- **Health**: <http://localhost:8000/api/admin/health>

## 📡 API Endpoints

### Public Endpoints

- `GET /` - Welcome message
- `GET /api/health` - Simple health check
- `GET /api/admin/health` - Detailed health with vector store stats
- `POST /api/admin/ingest` - Ingest documents (add auth in production!)

### Protected Endpoints (Require Firebase Auth)

- `POST /api/chat/` - Send message and get AI response
- `GET /api/chat/conversations` - Get user's conversation history
- `GET /api/chat/conversations/{id}/messages` - Get specific conversation messages

## 🔐 Authentication

All chat endpoints require Firebase authentication. Include the Firebase ID token in the Authorization header:

```javascript
headers: {
  'Authorization': 'Bearer <firebase_id_token>'
}
```

## 💬 Example Usage

### Chat Request

```bash
POST http://localhost:8000/api/chat/
Authorization: Bearer <your_firebase_token>
Content-Type: application/json

{
  "message": "What is the purpose of surveying in civil engineering?",
  "conversation_id": null,
  "include_history": true
}
```

### Chat Response

```json
{
  "message": "Great question! Surveying is like the foundation of any civil engineering project...",
  "conversation_id": "abc-123-def",
  "sources": [
    {
      "source": "SURVEYING MODULE 1.pdf",
      "chunk_id": 5,
      "relevance_score": 0.89
    }
  ],
  "follow_up_questions": [
    "What equipment is commonly used in surveying?",
    "How does surveying help in construction planning?"
  ],
  "timestamp": "2026-01-15T10:30:00Z"
}
```

## 🏗️ Project Structure

``` txt
backend/
├── main.py                  # FastAPI application
├── config.py               # Configuration settings
├── auth.py                 # Firebase authentication
├── database.py             # SQLAlchemy models & setup
├── models.py               # Pydantic models
├── document_processor.py   # PDF processing with OCR
├── vector_store.py         # ChromaDB integration
├── chat_service.py         # RAG logic & teaching prompts
├── ingest_documents.py     # Document ingestion script
├── routers/
│   ├── chat.py            # Chat endpoints
│   └── admin.py           # Admin endpoints
├── knowledge/             # Your PDF files
├── chroma_db/            # Vector database (auto-created)
├── notegpt.db            # SQLite chat history (auto-created)
├── requirements.txt
├── .env                  # Your configuration
└── firebase-credentials.json  # Firebase service account
```

## 🔧 Configuration Options

Edit [`config.py`](config.py) or `.env` for:

- **Chunk Size**: How text is split (default: 1000 chars)
- **Top K Results**: Number of relevant docs retrieved (default: 5)
- **Temperature**: LLM creativity (default: 0.7)
- **Max Tokens**: Response length (default: 2048)

## 🐛 Troubleshooting

### Tesseract not found

```powershell
# Check if installed
tesseract --version

# If not, set path in .env
TESSERACT_CMD=C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Poppler not found

```powershell
# Add to PATH
$env:PATH += ";C:\path\to\poppler\bin"

# Or install via chocolatey
choco install poppler
```

### Firebase authentication fails

- Ensure `firebase-credentials.json` is in the backend folder
- Check `FIREBASE_PROJECT_ID` matches your Firebase project
- Verify the service account has necessary permissions

### ChromaDB issues

```powershell
# Delete and reingest
rm -r chroma_db
python ingest_documents.py --force
```

## 📝 Notes for Frontend Integration

### CORS Configuration

The API allows requests from origins specified in `ALLOWED_ORIGINS`. Update this in `.env`:

```env
ALLOWED_ORIGINS=http://localhost:3000,https://your-app.web.app
```

### Response Format

All chat responses include:

- `message`: The AI's teaching-focused response
- `conversation_id`: Use this for follow-up messages
- `sources`: Citations from your PDFs
- `follow_up_questions`: Suggested questions to explore
- `timestamp`: When the response was generated

### Error Handling

The API returns standard HTTP status codes:

- `200`: Success
- `401`: Authentication failed
- `500`: Server error

## 🎓 Teaching Approach

The chatbot is designed to:

1. **Explain concepts clearly** with real-world examples
2. **Ask follow-up questions** to check understanding
3. **Encourage critical thinking** about the material
4. **Provide context** from your course materials
5. **Be conversational** like a helpful friend

## 📊 Monitoring

Check system status:

```bash
GET http://localhost:8000/api/admin/health
```

Response includes:

- API status
- Vector store document count
- Database location

## 🚀 Deployment Tips

For production:

1. Use a proper database (PostgreSQL instead of SQLite)
2. Add authentication to admin endpoints
3. Set up proper logging and monitoring
4. Use environment-specific `.env` files
5. Consider rate limiting
6. Deploy behind a reverse proxy (nginx)

## 📄 License

This is a college project - free to use and modify!

## 🤝 Support

For issues or questions:

1. Check the logs in the terminal
2. Verify all prerequisites are installed
3. Ensure `.env` is configured correctly
4. Check Firebase credentials are valid

---

Built with ❤️ for students learning civil engineering!
