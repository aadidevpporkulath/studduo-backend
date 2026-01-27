from fastapi import APIRouter, HTTPException
from datetime import datetime
import time

from vector_store import vector_store
from chat_service import chat_service
from models import HealthResponse, ChatRequest, ChatResponse, Source

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
            include_history=request.include_history,
            prompt_type=request.prompt_type,
            is_temporary=request.is_temporary
        )

        return ChatResponse(
            message=result["message"],
            conversation_id=result["conversation_id"],
            sources=[Source(**src) for src in result["sources"]],
            follow_up_questions=result["follow_up_questions"],
            prompt_type=result["prompt_type"],
            is_temporary=result["is_temporary"]
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing chat: {str(e)}"
        )
