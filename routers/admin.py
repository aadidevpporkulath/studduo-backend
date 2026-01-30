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

