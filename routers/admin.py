from fastapi import APIRouter, HTTPException
from fastapi import Depends
from datetime import datetime
import time

from vector_store import vector_store
from document_processor import document_processor
from chat_service import chat_service
from models import HealthResponse, IngestRequest, IngestResponse, ChatRequest, ChatResponse, Source

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """
    Check the health status of the API and vector store.
    """
    try:
        stats = vector_store.get_collection_stats()

        return HealthResponse(
            status="healthy",
            vector_store_status=stats
        )
    except Exception as e:
        return HealthResponse(
            status="unhealthy",
            vector_store_status={"error": str(e)}
        )


@router.post("/ingest", response_model=IngestResponse)
async def ingest_documents(request: IngestRequest):
    """
    Ingest PDF documents from the knowledge folder into the vector store.

    - **force_reingest**: If True, deletes existing collection and reingests all documents

    ⚠️ This endpoint is not protected - add authentication in production!
    """
    try:
        start_time = time.time()

        # Check if we need to reingest
        if request.force_reingest:
            stats = vector_store.get_collection_stats()
            if stats["document_count"] > 0:
                vector_store.delete_collection()

        # Process documents
        documents = document_processor.process_directory()

        if not documents:
            raise HTTPException(
                status_code=400,
                detail="No documents found or all documents failed to process"
            )

        # Add to vector store
        vector_store.add_documents(documents)

        time_taken = time.time() - start_time

        # Count unique files
        unique_sources = set(doc["metadata"]["source"] for doc in documents)

        return IngestResponse(
            status="success",
            documents_processed=len(unique_sources),
            chunks_created=len(documents),
            time_taken=round(time_taken, 2),
            message=f"Successfully processed {len(unique_sources)} documents into {len(documents)} chunks"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error during ingestion: {str(e)}"
        )


@router.get("/stats")
async def get_stats():
    """
    Get statistics about the vector store and system.
    """
    try:
        stats = vector_store.get_collection_stats()
        return {
            "status": "success",
            "vector_store": stats,
            "timestamp": datetime.utcnow()
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving stats: {str(e)}"
        )


@router.post("/test-chat", response_model=ChatResponse)
async def test_chat(request: ChatRequest):
    """
    Test chat endpoint WITHOUT authentication (for development/testing only).

    ⚠️ REMOVE THIS IN PRODUCTION - Use /api/chat/ with auth instead!

    This is just for testing the chatbot without setting up Firebase auth.
    """
    try:
        # Use a test user ID
        result = await chat_service.chat(
            user_id="test-user",
            query=request.message,
            conversation_id=request.conversation_id,
            include_history=request.include_history
        )

        return ChatResponse(
            message=result["message"],
            conversation_id=result["conversation_id"],
            sources=[Source(**src) for src in result["sources"]],
            follow_up_questions=result["follow_up_questions"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )
