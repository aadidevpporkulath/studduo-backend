from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config import settings
from routers import chat_router, admin_router

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events."""
    # Startup
    logger.info("Starting StudduoAI API...")

    # Pre-load vector store to avoid cold start on first request
    logger.info("Pre-loading vector store and embeddings model...")
    try:
        from vector_store import vector_store
        await vector_store.initialize_async()
        logger.info("Vector store pre-loaded successfully")
    except Exception as e:
        logger.error(f"Failed to pre-load vector store: {e}")
        logger.warning("Vector store will initialize on first request")

    logger.info(f"Vector store directory: {settings.chroma_persist_dir}")
    logger.info(f"Knowledge directory: {settings.knowledge_dir}")
    logger.info("API startup complete - Ready for requests!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down StudduoAI API...")


# Create FastAPI app
app = FastAPI(
    title="StudduoAI API",
    description="Multi-domain RAG-based tutoring chatbot for student learning with teaching-focused responses",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # allow_origins=settings.origins_list,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(admin_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to StudduoAI API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/admin/health"
    }


@app.get("/api/health")
async def health():
    """Simple health check."""
    return {"status": "healthy", "service": "studduo-api"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.api_port,
        reload=True if settings.app_env == "development" else False
    )
