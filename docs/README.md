# NoteGPT Backend Documentation

Welcome to the NoteGPT Backend documentation! This folder contains comprehensive documentation for all features and capabilities.

## 📚 Documentation Index

### Getting Started
- [Installation Guide](INSTALLATION.md) - Setup and configuration
- [Quick Start](QUICK_START.md) - Get up and running in minutes
- [API Overview](API_OVERVIEW.md) - All available endpoints

### Features
- [Prompt Types](PROMPT_TYPES.md) - 6 different teaching response styles
- [Temporary Conversations](TEMPORARY_CONVERSATIONS.md) - Unsaved quick queries
- [Conversation Management](CONVERSATIONS.md) - Managing chat history
- [Embedding Cache](EMBEDDING_CACHE.md) - Performance optimization
- [Auto-Generated Titles](AUTO_TITLES.md) - Smart conversation naming
- [Student Features](STUDENT_FEATURES.md) - **NEW: Delete, Edit, Search, Feedback, Export** 🎓

### API Reference
- [Chat Endpoints](API_CHAT.md) - Chat and messaging APIs
- [Admin Endpoints](API_ADMIN.md) - Document ingestion and stats
- [Authentication](AUTHENTICATION.md) - Firebase auth integration

### Advanced Topics
- [Architecture](ARCHITECTURE.md) - System design and components
- [Database Schema](DATABASE.md) - SQLite and Firestore structure
- [Vector Store](VECTOR_STORE.md) - ChromaDB and embeddings
- [Performance](PERFORMANCE.md) - Optimization and caching

### Frontend Integration
- [Frontend Guide](FRONTEND_INTEGRATION.md) - Complete integration examples
- [TypeScript Examples](TYPESCRIPT_EXAMPLES.md) - Ready-to-use code

## 🎯 New in v1.1: Student-Focused Features 🎓

Five powerful features specifically designed for college students:

1. **Delete Conversation** - Remove old conversations to keep organized
2. **Edit Conversation Title** - Rename for better organization  
3. **Search Conversations** - Find past discussions easily
4. **Message Feedback** - Rate responses as helpful/unhelpful
5. **Export as PDF** - Download for offline study and sharing

[Learn more about Student Features →](STUDENT_FEATURES.md)

## 🚀 Quick Links

**New to NoteGPT?** Start with [Quick Start](QUICK_START.md)

**Student Features?** Check [Student Features Guide](STUDENT_FEATURES.md) - **NEW!**

**Implementing Frontend?** Check [Frontend Guide](FRONTEND_INTEGRATION.md)

**Need API Reference?** See [API Overview](API_OVERVIEW.md)

**Understanding Features?** Read [Features Overview](#features) above

## 📋 What is NoteGPT?

NoteGPT is a multi-domain RAG (Retrieval-Augmented Generation) tutoring chatbot that:
- Answers questions using your PDF course materials (any subject)
- Provides 6 different teaching response styles
- Maintains conversation history with context awareness
- Supports temporary (unsaved) conversations
- **NEW:** Offers complete conversation management for students 🎓
- Auto-generates conversation titles
- Caches embeddings for performance
- Uses Firebase authentication
- Powered by Google Gemini (free tier)

## 🎯 Key Features at a Glance

### 1. Prompt Types (6 Styles)
- **Explanation** - Detailed teaching explanations
- **Plan** - Step-by-step procedures
- **Example** - Worked examples with solutions
- **Summary** - Quick reference summaries
- **Problem Solving** - Guides to solve problems
- **Quiz** - Self-assessment questions

### 2. Temporary Conversations
- Quick queries not saved to database
- Perfect for exploring, testing, quizzes
- Don't clutter conversation history

### 3. Smart Caching
- Embedding cache for repeated queries
- 500x faster for cache hits
- Auto-pruning to manage memory

### 4. Auto-Generated Titles
- Conversation titles from first message
- Uses LLM for smart, concise titles
- Fallback to query truncation

### 5. Pagination
- Offset and limit parameters
- Efficient handling of large histories
- Supports infinite scroll patterns

## 🛠️ Tech Stack

- **Framework:** FastAPI (Python 3.9+)
- **LLM:** Google Gemini 2.5 Flash
- **Vector Store:** ChromaDB with HuggingFace embeddings
- **Database:** Firestore (conversations), SQLite (backup)
- **Authentication:** Firebase Auth
- **PDF Processing:** PyPDF, Tesseract OCR

## 📦 Project Structure

```
backend/
├── docs/                    # 📚 This documentation
├── routers/                 # API route handlers
│   ├── chat.py             # Chat endpoints
│   └── admin.py            # Admin endpoints
├── main.py                 # FastAPI application
├── chat_service.py         # Core chat logic
├── vector_store.py         # ChromaDB operations
├── firestore_db.py         # Firestore operations
├── document_processor.py   # PDF processing
├── auth.py                 # Firebase authentication
├── models.py               # Pydantic models
├── config.py               # Configuration
├── knowledge/              # PDF documents folder
└── chroma_db/              # Vector store data
```

## 🎓 Learning Path

### For Developers
1. Read [Architecture](ARCHITECTURE.md) to understand system design
2. Follow [Installation Guide](INSTALLATION.md) to set up
3. Review [API Overview](API_OVERVIEW.md) for endpoints
4. Check [Frontend Integration](FRONTEND_INTEGRATION.md) for implementation

### For Users
1. Start with [Quick Start](QUICK_START.md)
2. Learn about [Prompt Types](PROMPT_TYPES.md)
3. Understand [Conversations](CONVERSATIONS.md)
4. Explore [Temporary Conversations](TEMPORARY_CONVERSATIONS.md)

## 🤝 Contributing

When adding new features:
1. Update relevant documentation
2. Add examples to [Frontend Guide](FRONTEND_INTEGRATION.md)
3. Update [API Overview](API_OVERVIEW.md) if endpoints change
4. Document any new configuration in [Installation Guide](INSTALLATION.md)

## 📝 Documentation Conventions

- **Code blocks** use appropriate language tags
- **Examples** show both request and response
- **File paths** use relative paths from backend/
- **API endpoints** include HTTP method, path, and parameters
- **Warnings** highlighted with ⚠️
- **Tips** highlighted with 💡

## 🔗 External Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Google Gemini API](https://ai.google.dev/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Firebase Documentation](https://firebase.google.com/docs)

## ❓ Need Help?

- Check the relevant doc file for your topic
- Review example code in [TypeScript Examples](TYPESCRIPT_EXAMPLES.md)
- Verify configuration in [Installation Guide](INSTALLATION.md)
- Check [API Overview](API_OVERVIEW.md) for endpoint details

---

**Last Updated:** January 17, 2026
**Version:** 1.0.0
