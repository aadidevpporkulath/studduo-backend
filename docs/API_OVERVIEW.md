# API Overview

Complete reference for all NoteGPT API endpoints.

## Base URL

``` txt
Development: http://localhost:8000
Production: https://your-domain.com
```

## Authentication

All chat endpoints require Firebase Authentication.

```http
Authorization: Bearer <firebase_id_token>
```

Get the token from Firebase Auth in your frontend:

```typescript
const token = await user.getIdToken();
```

---

## Endpoints Summary

| Method | Endpoint | Auth | Description |
| ------ | -------- | ---- | ----------- |
| GET | `/` | No | Welcome message |
| GET | `/api/health` | No | Health check |
| POST | `/api/chat/` | Yes | Send message |
| GET | `/api/chat/conversations` | Yes | List conversations |
| GET | `/api/chat/conversations/search` | Yes | Search conversations |
| PATCH | `/api/chat/conversations/{id}` | Yes | Update title |
| DELETE | `/api/chat/conversations/{id}` | Yes | Delete conversation |
| GET | `/api/chat/conversations/{id}/messages` | Yes | Get messages |
| POST | `/api/chat/conversations/{id}/messages/{msg_id}/feedback` | Yes | Rate message |
| GET | `/api/admin/health` | No | Admin health check |
| POST | `/api/admin/ingest` | No* | Ingest documents |
| GET | `/api/admin/stats` | No* | Vector store stats |
| GET | `/api/admin/conversations/{id}/export` | Yes | Export conversation |

*⚠️ Admin endpoints should be protected in production

---

## Public Endpoints

### GET `/`

Welcome message with API information.

**Response:**

```json
{
  "message": "Welcome to NoteGPT API",
  "version": "1.0.0",
  "docs": "/docs",
  "health": "/api/admin/health"
}
```

---

### GET `/api/health`

Simple health check.

**Response:**

```json
{
  "status": "healthy",
  "service": "notegpt-api"
}
```

---

## Chat Endpoints (Authenticated)

### POST `/api/chat/`

Send a message and get AI response.

**Request Body:**

```json
{
  "message": "What is photosynthesis?",
  "conversation_id": null,           // Optional: continue conversation
  "include_history": true,           // Optional: use context (default: true)
  "prompt_type": "explanation",      // Optional: response style (default: explanation)
  "is_temporary": false              // Optional: don't save (default: false)
}
```

**Prompt Types:**

- `explanation` - Detailed teaching explanation (default)
- `plan` - Step-by-step procedure
- `example` - Worked examples
- `summary` - Quick reference
- `problem_solving` - Problem-solving guide
- `quiz` - Self-assessment questions

**Response:**

```json
{
  "message": "Photosynthesis is the process...",
  "conversation_id": "uuid-here",
  "sources": [
    {
      "source": "biology_notes.pdf",
      "chunk_id": 5,
      "relevance_score": 0.92
    }
  ],
  "follow_up_questions": [
    "What are the stages of photosynthesis?",
    "How does light affect photosynthesis rate?"
  ],
  "prompt_type": "explanation",
  "is_temporary": false,
  "timestamp": "2026-01-17T10:30:00"
}
```

**Status Codes:**

- `200` - Success
- `401` - Unauthorized (invalid/missing token)
- `500` - Server error

---

### GET `/api/chat/conversations`

Get user's conversation list with pagination.

**Query Parameters:**

- `offset` (int, optional) - Skip N conversations (default: 0)
- `limit` (int, optional) - Max conversations (default: 20, max: 100)

**Example:**

``` txt
GET /api/chat/conversations?offset=0&limit=20
```

**Response:**

```json
[
  {
    "conversation_id": "uuid-1",
    "title": "Photosynthesis Basics",
    "last_message": "Great! Let me explain...",
    "message_count": 8,
    "created_at": "2026-01-17T09:00:00",
    "updated_at": "2026-01-17T10:30:00",
    "prompt_type": "explanation",
    "is_temporary": false
  },
  {
    "conversation_id": "uuid-2",
    "title": "World War II Timeline",
    "last_message": "The war began in 1939...",
    "message_count": 12,
    "created_at": "2026-01-16T14:00:00",
    "updated_at": "2026-01-17T08:00:00",
    "prompt_type": "summary",
    "is_temporary": false
  }
]
```

**Status Codes:**

- `200` - Success
- `401` - Unauthorized

**Pagination Example:**

```typescript
// Page 1 (first 20)
GET /api/chat/conversations?offset=0&limit=20

// Page 2 (next 20)
GET /api/chat/conversations?offset=20&limit=20

// Page 3 (next 20)
GET /api/chat/conversations?offset=40&limit=20
```

---

### GET `/api/chat/conversations/{conversation_id}/messages`

Get all messages in a conversation.

**Path Parameters:**

- `conversation_id` (string, required) - Conversation UUID

**Example:**

``` txt
GET /api/chat/conversations/abc-123-def/messages
```

**Response:**

```json
{
  "conversation_id": "abc-123-def",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "What is photosynthesis?",
      "timestamp": "2026-01-17T10:00:00"
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "Photosynthesis is the process...",
      "sources": [
        {
          "source": "biology_notes.pdf",
          "chunk_id": 5,
          "relevance_score": 0.92
        }
      ],
      "timestamp": "2026-01-17T10:00:05"
    },
    {
      "id": "msg-3",
      "role": "user",
      "content": "What are the stages?",
      "timestamp": "2026-01-17T10:01:00"
    },
    {
      "id": "msg-4",
      "role": "assistant",
      "content": "There are two main stages...",
      "sources": [...],
      "timestamp": "2026-01-17T10:01:05"
    }
  ]
}
```

**Status Codes:**

- `200` - Success
- `401` - Unauthorized
- `404` - Conversation not found
- `500` - Server error

---

## Admin Endpoints

### GET `/api/admin/health`

Health check with vector store information.

**Response:**

```json
{
  "status": "healthy",
  "vector_store_status": {
    "collection_name": "notegpt_documents",
    "document_count": 1250,
    "persist_directory": "./chroma_db"
  },
  "timestamp": "2026-01-17T10:30:00"
}
```

**Status:**

- `status: "healthy"` - All systems operational
- `status: "unhealthy"` - Vector store error

---

### POST `/api/admin/ingest`

Ingest PDF documents into vector store.

**Request Body:**

```json
{
  "force_reingest": false    // Optional: delete existing and reingest all
}
```

**Behavior:**

- `force_reingest: false` - Add new PDFs to existing collection
- `force_reingest: true` - Delete all existing, reingest everything

**Response:**

```json
{
  "status": "success",
  "documents_processed": 5,
  "chunks_created": 250,
  "time_taken": 12.5,
  "message": "Successfully processed 5 documents into 250 chunks"
}
```

**Status Codes:**

- `200` - Success
- `400` - No documents found
- `500` - Processing error

**Process:**

1. Reads PDFs from `./knowledge/` folder
2. Extracts text (with OCR if needed)
3. Chunks text (1000 chars, 200 overlap)
4. Generates embeddings (HuggingFace)
5. Stores in ChromaDB

---

### GET `/api/admin/stats`

Get vector store statistics.

**Response:**

```json
{
  "status": "success",
  "vector_store": {
    "collection_name": "notegpt_documents",
    "document_count": 1250,
    "persist_directory": "./chroma_db"
  },
  "timestamp": "2026-01-17T10:30:00"
}
```

**Status Codes:**

- `200` - Success
- `500` - Error retrieving stats

---

## Error Responses

All endpoints return errors in this format:

```json
{
  "detail": "Error message here"
}
```

**Common Error Codes:**

- `400` - Bad request (invalid parameters)
- `401` - Unauthorized (missing/invalid token)
- `404` - Resource not found
- `500` - Internal server error

---

## Rate Limits

Currently no rate limiting implemented.

⚠️ **Recommended for production:**

- 100 requests/minute per user for chat
- 10 requests/hour for document ingestion

---

## CORS

Configured origins in `.env`:

```env
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
```

Add your frontend URL to this list.

---

## New Features: Student-Focused Endpoints

### GET `/api/chat/conversations/search`

Search conversations by title or content.

**Query Parameters:**

- `q` (string, required) - Search query

**Example:**

``` txt
GET /api/chat/conversations/search?q=photosynthesis
```

**Response:**

```json
{
  "query": "photosynthesis",
  "total_results": 3,
  "results": [
    {
      "conversation_id": "uuid-1",
      "title": "Photosynthesis Basics",
      "last_message": "Great! Let me explain...",
      "match_context": "Title contains 'photosynthesis'",
      "created_at": "2026-01-17T09:00:00"
    }
  ]
}
```

---

### PATCH `/api/chat/conversations/{conversation_id}`

Update conversation title.

**Path Parameters:**

- `conversation_id` (string, required) - Conversation UUID

**Request Body:**

```json
{
  "title": "My Custom Title"
}
```

**Response:**

```json
{
  "status": "success",
  "conversation_id": "abc-123-def",
  "title": "My Custom Title"
}
```

**Status Codes:**

- `200` - Success
- `401` - Unauthorized
- `500` - Server error

---

### DELETE `/api/chat/conversations/{conversation_id}`

Delete a conversation and all its messages.

**Path Parameters:**

- `conversation_id` (string, required) - Conversation UUID

**Example:**

``` txt
DELETE /api/chat/conversations/abc-123-def
```

**Response:**

```json
{
  "status": "success",
  "message": "Conversation deleted"
}
```

**Status Codes:**

- `200` - Deleted
- `401` - Unauthorized
- `500` - Server error

---

### POST `/api/chat/conversations/{conversation_id}/messages/{message_id}/feedback`

Rate a message as helpful or not helpful.

**Path Parameters:**

- `conversation_id` (string, required) - Conversation UUID
- `message_id` (string, required) - Message ID

**Request Body:**

```json
{
  "feedback": "helpful"
}
```

Feedback values: `"helpful"` or `"not_helpful"`

**Response:**

```json
{
  "status": "success",
  "message": "Feedback saved"
}
```

**Status Codes:**

- `200` - Feedback saved
- `400` - Invalid feedback value
- `401` - Unauthorized
- `500` - Server error

---

### GET `/api/admin/conversations/{conversation_id}/export`

Export a conversation as PDF or JSON.

**Path Parameters:**

- `conversation_id` (string, required) - Conversation UUID

**Query Parameters:**

- `format` (string, optional) - Export format: `pdf` or `json` (default: `pdf`)

**Examples:**

``` txt
# Export as PDF (default)
GET /api/admin/conversations/abc-123-def/export

# Export as PDF explicitly
GET /api/admin/conversations/abc-123-def/export?format=pdf

# Export as JSON
GET /api/admin/conversations/abc-123-def/export?format=json
```

**PDF Response:**

- Content-Type: `application/pdf`
- File download with conversation title as filename

**JSON Response:**

```json
{
  "conversation_id": "abc-123-def",
  "title": "Photosynthesis Basics",
  "created_at": "2026-01-17T09:00:00",
  "messages": [
    {
      "id": "msg-1",
      "role": "user",
      "content": "What is photosynthesis?",
      "timestamp": "2026-01-17T09:05:00"
    },
    {
      "id": "msg-2",
      "role": "assistant",
      "content": "Photosynthesis is...",
      "sources": [
        {
          "filename": "biology_notes.pdf",
          "relevance_score": 0.92
        }
      ],
      "timestamp": "2026-01-17T09:06:00"
    }
  ]
}
```

**Status Codes:**

- `200` - Success
- `401` - Unauthorized
- `404` - Conversation not found
- `400` - Invalid format
- `500` - Server error

---

## Interactive Documentation

FastAPI provides auto-generated interactive docs:

**Swagger UI:**

``` txt
http://localhost:8000/docs
```

**ReDoc:**

``` txt
http://localhost:8000/redoc
```

These allow you to test endpoints directly in the browser.

---

## Next Steps

- See [Frontend Integration](FRONTEND_INTEGRATION.md) for complete examples
- Read [Prompt Types](PROMPT_TYPES.md) to understand response styles
- Check [Temporary Conversations](TEMPORARY_CONVERSATIONS.md) for quick queries
- Review [Authentication](AUTHENTICATION.md) for Firebase setup
