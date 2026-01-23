# System Architecture

Understanding the NoteGPT system design, components, and data flow.

## 🏗️ High-Level Architecture

``` txt
┌─────────────┐
│   Frontend  │
│  (React/TS) │
└──────┬──────┘
       │ HTTP/REST
       │ Firebase Auth Token
       ▼
┌─────────────────────────────────────┐
│         FastAPI Backend             │
│  ┌──────────────────────────────┐  │
│  │   Authentication Middleware   │  │
│  │     (Firebase Verify)         │  │
│  └──────────────────────────────┘  │
│              │                       │
│              ▼                       │
│  ┌──────────────────────────────┐  │
│  │      Routers (Endpoints)      │  │
│  │   - Chat Router               │  │
│  │   - Admin Router              │  │
│  └──────────────────────────────┘  │
│              │                       │
│              ▼                       │
│  ┌──────────────────────────────┐  │
│  │      Chat Service             │  │
│  │  - Prompt Generation          │  │
│  │  - History Management         │  │
│  │  - Title Generation           │  │
│  └──────────────────────────────┘  │
│         │            │               │
│         ▼            ▼               │
│  ┌──────────┐  ┌──────────────┐    │
│  │  Vector  │  │  Firestore   │    │
│  │  Store   │  │     DB       │    │
│  └──────────┘  └──────────────┘    │
└─────────────────────────────────────┘
       │                    │
       ▼                    ▼
┌──────────────┐    ┌──────────────┐
│   ChromaDB   │    │  Firebase    │
│   (Local)    │    │   (Cloud)    │
└──────────────┘    └──────────────┘
       │
       ▼
┌──────────────┐
│  Google      │
│  Gemini API  │
└──────────────┘
```

## 📦 Core Components

### 1. **FastAPI Application** (`main.py`)

- Entry point for the backend
- Configures CORS middleware
- Includes routers (chat, admin)
- Handles app lifecycle (startup/shutdown)

**Key Features:**

- Async request handling
- Auto-generated OpenAPI docs
- Middleware support

---

### 2. **Routers** (`routers/`)

#### Chat Router (`routers/chat.py`)

Handles all chat-related endpoints:

- `POST /api/chat/` - Send messages
- `GET /api/chat/conversations` - List conversations (with pagination)
- `GET /api/chat/conversations/{id}/messages` - Get messages

**Responsibilities:**

- Request validation (Pydantic models)
- Authentication dependency injection
- Error handling
- Response formatting

#### Admin Router (`routers/admin.py`)

Handles administrative endpoints:

- `GET /api/admin/health` - Health check
- `POST /api/admin/ingest` - Document ingestion
- `GET /api/admin/stats` - Vector store stats

**Responsibilities:**

- Document processing coordination
- Vector store management
- System monitoring

---

### 3. **Chat Service** (`chat_service.py`)

The core business logic layer.

**Key Methods:**

```python
class ChatService:
    def __init__(self):
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.embedding_cache = {}  # Performance optimization
    
    async def chat(
        user_id, query, conversation_id=None,
        include_history=True, prompt_type="explanation",
        is_temporary=False
    ):
        """Main chat processing logic"""
        
    def _create_prompt_by_type(
        query, context, prompt_type, history
    ):
        """Generate prompts based on type"""
        
    def _generate_title_from_message(query):
        """Auto-generate conversation titles"""
        
    def _generate_follow_up_questions(query, response):
        """Suggest follow-up questions"""
```

**Flow:**

1. Create/retrieve conversation
2. Load conversation history (if not temporary)
3. Retrieve relevant documents from vector store
4. Generate prompt based on type
5. Call LLM (Gemini)
6. Save messages (if not temporary)
7. Generate follow-up questions
8. Return response

---

### 4. **Vector Store** (`vector_store.py`)

Manages document embeddings and similarity search.

**Key Components:**

```python
class VectorStore:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="all-MiniLM-L6-v2"
        )
        self.client = chromadb.PersistentClient(...)
        self.collection = client.get_or_create_collection(...)
        self.query_embedding_cache = {}  # NEW: Performance cache
    
    def add_documents(documents):
        """Embed and store documents"""
        
    def similarity_search(query, k=5):
        """Find similar documents with caching"""
        
    def _get_cached_embedding(query):
        """Check embedding cache"""
        
    def _cache_embedding(query, embedding):
        """Store embedding in cache"""
```

**Features:**

- Local embeddings (no API calls)
- Persistent storage (survives restarts)
- Embedding caching (500x speedup)
- Cosine similarity search

---

### 5. **Firestore DB** (`firestore_db.py`)

Manages conversation and message persistence.

**Key Methods:**

```python
class FirestoreDB:
    @staticmethod
    async def create_conversation(
        user_id, title, conversation_id=None,
        prompt_type="explanation", is_temporary=False
    ):
        """Create new conversation"""
        
    @staticmethod
    async def save_message(
        user_id, conversation_id, role, content, sources=None
    ):
        """Save individual message"""
        
    @staticmethod
    async def get_user_conversations(
        user_id, offset=0, limit=20
    ):
        """List conversations with pagination"""
        
    @staticmethod
    async def get_conversation_messages(
        user_id, conversation_id, limit=100
    ):
        """Get all messages in conversation"""
```

**Data Structure:**

``` txt
users/{user_id}/
  conversations/{conversation_id}/
    - id, title, prompt_type, is_temporary
    - created_at, updated_at, message_count
    messages/{message_id}/
      - id, role, content, sources, timestamp
```

---

### 6. **Document Processor** (`document_processor.py`)

Handles PDF ingestion and text extraction.

**Process:**

1. Scan `./knowledge/` directory for PDFs
2. Extract text (PyPDF + OCR fallback)
3. Clean and normalize text
4. Chunk text (1000 chars, 200 overlap)
5. Add metadata (source, chunk_id)

**Chunking Strategy:**

```python
chunk_size = 1000      # Characters per chunk
chunk_overlap = 200    # Overlap between chunks
```

This ensures:

- Chunks aren't too large for LLM context
- Overlap maintains continuity
- Metadata tracks source

---

### 7. **Authentication** (`auth.py`)

Firebase token verification.

```python
async def verify_firebase_token(credentials):
    """Verify Firebase ID token and return user info"""
    # Decode and verify token
    # Return user data (uid, email, etc.)

async def get_current_user(credentials):
    """Dependency for protected routes"""
    return await verify_firebase_token(credentials)
```

**Flow:**

1. Frontend sends Firebase token in `Authorization` header
2. Backend verifies token with Firebase Admin SDK
3. Extracts user info (uid, email)
4. Makes available to route handlers

---

## 🔄 Request Flow

### Chat Message Flow

``` txt
1. User sends message from frontend
   ↓
2. Frontend attaches Firebase auth token
   ↓
3. POST /api/chat/ receives request
   ↓
4. Auth middleware verifies token
   ↓
5. Router validates request (Pydantic)
   ↓
6. ChatService.chat() called
   ↓
7. Check embedding cache for query
   ├─ Cache hit: Use cached embedding
   └─ Cache miss: Generate and cache
   ↓
8. Vector store similarity search
   ↓
9. Retrieve conversation history (if not temporary)
   ↓
10. Generate prompt based on type
    ↓
11. Call Gemini LLM
    ↓
12. Save user & assistant messages (if not temporary)
    ↓
13. Generate follow-up questions
    ↓
14. Return response to frontend
```

### Document Ingestion Flow

``` txt
1. PDFs placed in ./knowledge/
   ↓
2. POST /api/admin/ingest called
   ↓
3. Document processor scans directory
   ↓
4. For each PDF:
   ├─ Extract text (PyPDF)
   ├─ OCR if needed (Tesseract)
   ├─ Clean text
   └─ Chunk into segments
   ↓
5. Generate embeddings (batch)
   ↓
6. Store in ChromaDB
   ↓
7. Return statistics
```

---

## 💾 Data Storage

### ChromaDB (Vector Store)

- **Location:** `./chroma_db/`
- **Type:** Persistent local storage
- **Contents:** Document embeddings + text + metadata
- **Size:** ~100KB per 1000 chunks

### Firestore (Conversations)

- **Location:** Cloud (Firebase)
- **Type:** NoSQL document database
- **Contents:** Conversations + messages + metadata
- **Structure:** Hierarchical (users → conversations → messages)

### SQLite (Backup/Legacy)

- **Location:** `./notegpt.db`
- **Type:** Local SQL database
- **Contents:** Currently used for schema definition
- **Note:** May be deprecated in favor of Firestore

---

## 🚀 Performance Optimizations

### 1. Embedding Cache

- **Location:** In-memory dictionary
- **Cache Key:** MD5 hash of query
- **Cache Value:** Embedding vector
- **Max Size:** 1000 entries (LRU-style pruning)
- **Impact:** 500x faster for repeated queries

### 2. Async Operations

- All I/O operations are async
- Non-blocking database calls
- Concurrent request handling

### 3. Batch Processing

- Documents processed in batches of 100
- Embeddings generated in batches
- Reduces memory footprint

### 4. Pagination

- Conversations paginated (offset + limit)
- Prevents loading entire history
- Firestore native pagination support

---

## 🔒 Security

### Authentication

- Firebase token verification on every request
- Tokens expire (1 hour default)
- User isolation (can't access other users' data)

### Data Isolation

- Firestore rules enforce user ownership
- Each user has separate conversation namespace
- Vector store is read-only for users

### CORS

- Configurable allowed origins
- Credentials support enabled
- Production: Restrict to frontend domain

---

## 📊 Scalability Considerations

### Current Limits

- **Vector Store:** Limited by disk space
- **Firestore:** 1 write/second/document (free tier)
- **Gemini API:** Free tier quotas apply
- **Memory:** Embedding cache grows with use

### Scaling Strategies

**Horizontal Scaling:**

- Add Redis for distributed cache
- Use managed Firestore (auto-scales)
- Deploy multiple backend instances

**Vertical Scaling:**

- Increase memory for larger cache
- Use GPU for faster embeddings
- Optimize chunk sizes

**Database Optimization:**

- Index frequently queried fields
- Implement query result caching
- Use Firestore batch operations

---

## 🛠️ Technology Choices

### Why FastAPI?

- Async support (critical for I/O)
- Auto-generated docs
- Type safety with Pydantic
- High performance

### Why ChromaDB?

- Simple local vector database
- No external dependencies
- Persistent storage
- Python-native

### Why Firestore?

- Real-time sync capabilities
- Automatic scaling
- NoSQL flexibility
- Firebase integration

### Why Gemini?

- Generous free tier
- Fast response times
- Good reasoning capabilities
- Multimodal support (future)

---

## 🔮 Future Architecture Improvements

### Planned Enhancements

1. **Caching Layer:** Redis for distributed caching
2. **Queue System:** Celery for async document processing
3. **WebSocket Support:** Real-time chat streaming
4. **Monitoring:** Prometheus + Grafana
5. **Load Balancer:** Nginx for multiple instances

### Potential Optimizations

1. **Vector Store:** Switch to Pinecone/Weaviate for scale
2. **Embeddings:** Use GPU for faster generation
3. **LLM:** Add streaming responses
4. **Database:** Implement read replicas

---

## 📝 Configuration

All configuration in `config.py`:

```python
class Settings:
    # API
    app_env = "development"
    api_port = 8000
    
    # LLM
    google_api_key = "..."
    model_name = "gemini-2.5-flash"
    temperature = 0.7
    max_tokens = 2048
    
    # RAG
    chunk_size = 1000
    chunk_overlap = 200
    top_k_results = 5
    
    # Paths
    chroma_persist_dir = "./chroma_db"
    knowledge_dir = "./knowledge"
    firebase_credentials_path = "./firebase-credentials.json"
```

---

## Next Steps

- See [Database Schema](DATABASE.md) for detailed data models
- Read [Vector Store](VECTOR_STORE.md) for embedding details
- Check [Performance](PERFORMANCE.md) for optimization techniques
- Review [Frontend Integration](FRONTEND_INTEGRATION.md) for implementation
