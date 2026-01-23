from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from typing import List

from auth import get_current_user
from chat_service import chat_service
from models import (
    ChatRequest,
    ChatResponse,
    ConversationSummary,
    Source,
    UpdateTitleRequest,
    UpdateTitleResponse,
    DeleteConversationResponse,
    MessageFeedbackResponse,
    MessageFeedback,
    SearchResponse,
    SearchResult
)

router = APIRouter(prefix="/api/chat", tags=["chat"])


@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Send a message and get AI response with teaching approach.

    - **message**: The user's question or message
    - **conversation_id**: Optional ID to continue existing conversation
    - **include_history**: Whether to use conversation history (default: True)
    """
    try:
        result = await chat_service.chat(
            user_id=current_user["uid"],
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


@router.get("/conversations", response_model=List[ConversationSummary])
async def get_conversations(
    current_user: dict = Depends(get_current_user),
    limit: int = 20
):
    """
    Get all conversations for the current user.

    - **limit**: Maximum number of conversations to return (default: 20)
    """
    try:
        conversations = await chat_service.get_user_conversations(
            user_id=current_user["uid"],
            limit=limit
        )

        return [ConversationSummary(**conv) for conv in conversations]

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving conversations: {str(e)}"
        )


@router.get("/conversations/search", response_model=SearchResponse)
async def search_conversations(
    q: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Search conversations by title.

    - **q**: Search query string
    """
    try:
        if not q or len(q.strip()) == 0:
            raise HTTPException(
                status_code=400,
                detail="Search query cannot be empty"
            )

        results = await chat_service.search_conversations(
            user_id=current_user["uid"],
            search_query=q
        )

        return SearchResponse(
            query=q,
            total_results=len(results),
            results=[SearchResult(**result) for result in results]
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error searching conversations: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages")
async def get_conversation_messages(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Get all messages in a specific conversation.

    - **conversation_id**: The ID of the conversation
    """
    try:
        messages = await chat_service.get_conversation_history(
            user_id=current_user["uid"],
            conversation_id=conversation_id,
            limit=100
        )

        return {"conversation_id": conversation_id, "messages": messages}

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving messages: {str(e)}"
        )


@router.patch("/conversations/{conversation_id}", response_model=UpdateTitleResponse)
async def update_conversation_title(
    conversation_id: str,
    request: UpdateTitleRequest,
    current_user: dict = Depends(get_current_user)
):
    """
    Update a conversation's title.

    - **conversation_id**: The ID of the conversation
    - **title**: New title for the conversation
    """
    try:
        success = await chat_service.update_conversation_title(
            user_id=current_user["uid"],
            conversation_id=conversation_id,
            new_title=request.title
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        return UpdateTitleResponse(
            status="success",
            conversation_id=conversation_id,
            title=request.title
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error updating conversation title: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}", response_model=DeleteConversationResponse)
async def delete_conversation(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Delete a conversation and all its messages.

    - **conversation_id**: The ID of the conversation to delete
    """
    try:
        success = await chat_service.delete_conversation(
            user_id=current_user["uid"],
            conversation_id=conversation_id
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found or already deleted"
            )

        return DeleteConversationResponse(
            status="success",
            message="Conversation deleted successfully"
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error deleting conversation: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/messages/{message_id}/feedback", response_model=MessageFeedbackResponse)
async def add_message_feedback(
    conversation_id: str,
    message_id: str,
    request: MessageFeedback,
    current_user: dict = Depends(get_current_user)
):
    """
    Add feedback (helpful/not_helpful) to a message.

    - **conversation_id**: The ID of the conversation
    - **message_id**: The ID of the message
    - **feedback**: Either 'helpful' or 'not_helpful'
    """
    try:
        if request.feedback not in ["helpful", "not_helpful"]:
            raise HTTPException(
                status_code=400,
                detail="Feedback must be either 'helpful' or 'not_helpful'"
            )

        success = await chat_service.add_message_feedback(
            user_id=current_user["uid"],
            conversation_id=conversation_id,
            message_id=message_id,
            feedback=request.feedback
        )

        if not success:
            raise HTTPException(
                status_code=404,
                detail="Message not found"
            )

        return MessageFeedbackResponse(
            status="success",
            message="Feedback added successfully",
            feedback=request.feedback
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error adding feedback: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/export")
async def export_conversation_pdf(
    conversation_id: str,
    current_user: dict = Depends(get_current_user)
):
    """
    Export a conversation as PDF.

    - **conversation_id**: The ID of the conversation to export
    """
    try:
        conversation = await chat_service.get_conversation_for_export(
            user_id=current_user["uid"],
            conversation_id=conversation_id
        )

        if not conversation:
            raise HTTPException(
                status_code=404,
                detail="Conversation not found"
            )

        # Generate PDF
        pdf_buffer = chat_service.generate_pdf_export(conversation)

        # Return as streaming response
        return StreamingResponse(
            iter([pdf_buffer.getvalue()]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=conversation_{conversation_id}.pdf"
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error exporting conversation: {str(e)}"
        )
