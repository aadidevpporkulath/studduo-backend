from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime


class ChatMessage(BaseModel):
    """Single chat message."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None


class ChatMessageWithSources(BaseModel):
    """Chat message with sources."""
    role: str = Field(..., description="Role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: Optional[datetime] = None
    sources: List[Dict[str, Any]] = Field(
        default_factory=list, description="Source documents used")

    model_config = {"populate_by_name": True}


class ChatRequest(BaseModel):
    """Request model for chat endpoint."""
    message: str = Field(..., min_length=1,
                         description="User's question or message")
    conversation_id: Optional[str] = Field(
        None, description="ID of existing conversation")
    include_history: bool = Field(
        True, description="Whether to include conversation history")
    prompt_type: str = Field(
        "explanation", description="Type of response: 'explanation', 'plan', 'example', 'summary', 'problem_solving', 'quiz'")
    is_temporary: bool = Field(
        False, description="If True, conversation won't be saved to database")


class Source(BaseModel):
    """Source document reference."""
    source: str = Field(..., description="Source filename")
    chunk_id: int = Field(..., description="Chunk identifier")
    relevance_score: Optional[float] = Field(
        None, description="Similarity score")


class ChatResponse(BaseModel):
    """Response model for chat endpoint."""
    message: str = Field(..., description="Assistant's response")
    conversation_id: str = Field(...,
                                 description="Conversation ID for follow-ups")
    sources: List[Source] = Field(
        default_factory=list, description="Source documents used")
    follow_up_questions: List[str] = Field(
        default_factory=list, description="Suggested follow-up questions")
    prompt_type: str = Field(
        "explanation", description="Type of response provided")
    is_temporary: bool = Field(
        False, description="Whether this is a temporary conversation")
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConversationSummary(BaseModel):
    """Summary of a conversation."""
    conversation_id: str
    title: str
    last_message: str
    message_count: int
    created_at: datetime
    updated_at: datetime
    prompt_type: Optional[str] = Field(
        "explanation", description="Type of responses in this conversation")
    is_temporary: bool = Field(
        False, description="Whether this is a temporary conversation")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    vector_store_status: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class IngestRequest(BaseModel):
    """Request to ingest documents."""
    force_reingest: bool = Field(
        False, description="Force reingestion of all documents")


class IngestResponse(BaseModel):
    """Response after document ingestion."""
    status: str
    documents_processed: int
    chunks_created: int
    time_taken: float
    message: str


class MessageFeedback(BaseModel):
    """Feedback on a message."""
    feedback: str = Field(..., description="'helpful' or 'not_helpful'")


class SearchResult(BaseModel):
    """Search result for conversations."""
    conversation_id: str
    title: str
    last_message: str
    message_count: int
    created_at: datetime
    updated_at: datetime


class SearchResponse(BaseModel):
    """Search response."""
    query: str
    total_results: int
    results: List[SearchResult]


class UpdateTitleRequest(BaseModel):
    """Request to update conversation title."""
    title: str = Field(..., min_length=1, max_length=200)


class UpdateTitleResponse(BaseModel):
    """Response after updating conversation title."""
    status: str
    conversation_id: str
    title: str


class DeleteConversationResponse(BaseModel):
    """Response after deleting a conversation."""
    status: str
    message: str


class MessageFeedbackResponse(BaseModel):
    """Response after adding message feedback."""
    status: str
    message: str
    feedback: str


class ConversationMessagesResponse(BaseModel):
    """Response containing conversation messages with sources."""
    conversation_id: str
    messages: List[ChatMessageWithSources]
