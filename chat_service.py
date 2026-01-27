from typing import List, Dict, Any, Optional
import re
import logging
from io import BytesIO
from uuid import uuid4
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER

import google.generativeai as genai

from config import settings
from vector_store import vector_store
from firestore_db import firestore_db
from models import ChatMessage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure Gemini
genai.configure(api_key=settings.google_api_key)


class ChatService:
    """RAG-based chat service with teaching-focused responses and Firestore storage."""

    def __init__(self):
        # Use previous stable Gemini 2.5 Flash
        self.model = genai.GenerativeModel("gemini-2.5-flash")
        self.generation_config = {
            "temperature": settings.temperature,
            "max_output_tokens": settings.max_tokens,
        }

    def _create_teaching_prompt(
        self,
        query: str,
        context: str,
        conversation_history: List[ChatMessage] = None,
        prompt_type: str = "explanation"
    ) -> str:
        """Create a teaching-focused prompt for the LLM."""

        prompt_styles = {
            "explanation": "Give a clear, steadily paced explanation that builds intuition.",
            "plan": "Lay out a concise plan or set of steps the student can follow next.",
            "example": "Provide a worked example that illustrates the idea without overlong setup.",
            "summary": "Summarize the key points crisply; avoid new tangents.",
            "problem_solving": "Show the reasoning path to solve the problem, step by step.",
            "quiz": "Ask 2-3 short check-yourself questions with brief answers after each."
        }

        style_hint = prompt_styles.get(
            prompt_type, prompt_styles["explanation"])

        history_text = ""
        if conversation_history and len(conversation_history) > 0:
            history_text = "\n\nPrevious conversation:\n"
            for msg in conversation_history[-4:]:  # Last 2 exchanges
                history_text += f"{msg.role.upper()}: {msg.content[:200]}...\n"

        prompt = f"""You are a thoughtful, clear-thinking tutor who enjoys explaining ideas in a way that actually sticks.
Your goal is not to impress, but to help the student genuinely understand.

If the user greets or speaks casually, respond briefly and conversationally.
Do not introduce topics, explain concepts, or reference course material unless asked.

You adapt your tone and depth based on the student's question:
- If the question shows uncertainty, you slow down and ground the basics.
- If it shows confidence, you skip the obvious and go straight to insight.
- If it's vague, you clarify through explanation rather than interrogation.

When you explain:
- Start with the simplest accurate framing of the idea.
- Build forward naturally, one idea leading to the next.
- Use real-world or intuitive examples only when they add clarity.
- Prefer plain language over technical jargon unless precision requires it.
- Avoid sounding scripted, academic, or overly cheerful.

Requested response style: {style_hint}

Use the following information as authoritative context:
{context}
{history_text}

Student's question:
{query}

Your response should feel like a smart human explaining something out loud:
- Open with a direct, natural answer — no preamble.
- Explain the reasoning behind it as you go, not in a separate section.
- Break things up for readability, but don't over-format.
- If there's a common misunderstanding, surface it casually.
- End when the explanation feels complete — not with forced encouragement.

Aim for clarity, honesty, and flow over perfection."""

        return prompt

    def _should_generate_follow_ups(self, query: str, response: str) -> bool:
        """Determine if follow-up questions would be valuable."""
        query_lower = query.lower().strip()
        response_lower = response.lower()
        
        # Don't generate for greetings or casual exchanges
        greetings = ['hi', 'hello', 'hey', 'thanks', 'thank you', 'bye', 'goodbye']
        if any(query_lower.startswith(g) for g in greetings):
            return False
        
        # Don't generate for very short queries (likely casual)
        if len(query.split()) <= 3 and '?' not in query:
            return False
            
        # Don't generate if response is very short (likely acknowledgement)
        if len(response.split()) < 30:
            return False
            
        # Don't generate for procedural/navigation questions
        procedural_keywords = ['how do i', 'where can i', 'show me how', 'can you help', 'i need help with']
        if any(kw in query_lower for kw in procedural_keywords):
            return False
        
        # Don't generate if response indicates insufficient context
        if any(phrase in response_lower for phrase in ['i don\'t have', 'no information', 'cannot find']):
            return False
            
        return True

    def _generate_follow_up_questions(self, query: str, response: str) -> List[str]:
        """Generate relevant follow-up questions only when contextually appropriate."""
        try:
            # Check if follow-ups are needed
            if not self._should_generate_follow_ups(query, response):
                return []
            
            # Create specific, topic-focused follow-up questions
            prompt = f"""Based on this educational exchange, suggest 2 direct follow-up questions that would help the student go deeper.

Student asked: "{query}"

You explained: "{response[:500]}..."

Generate exactly 2 follow-up questions that:
- Explore a specific aspect or implication mentioned in the explanation
- Are directly related to the core topic (not meta-questions about studying)
- Can be answered with the available knowledge base
- Build naturally on what was just covered
- Are specific, not generic

Format: One question per line, no numbering, no extra text. Each line ends with '?'"""

            result = self.model.generate_content(prompt)

            # Safely check for response text
            if not result or not hasattr(result, 'text') or not result.text:
                logger.warning(
                    "Empty response when generating follow-up questions")
                return []

            # Parse and clean questions
            questions = []
            for line in result.text.strip().split('\n'):
                q = line.strip()
                # Remove numbering patterns like "1.", "1)", "Q1:", etc.
                q = re.sub(r'^[0-9]+[.):]?\s*', '', q)
                q = re.sub(r'^Q[0-9]+:?\s*', '', q, flags=re.IGNORECASE)
                q = q.strip()
                
                if q and q.endswith('?') and len(q.split()) > 3:
                    questions.append(q)
                    
            return questions[:2]
        except Exception as e:
            logger.error(f"Error generating follow-up questions: {str(e)}")
            return []

    async def get_conversation_history(
        self,
        user_id: str,
        conversation_id: str,
        limit: int = 10
    ) -> List[ChatMessage]:
        """Retrieve conversation history from Firestore."""
        try:
            messages = await firestore_db.get_conversation_messages(
                user_id, conversation_id, limit
            )

            return [
                ChatMessage(
                    role=msg["role"],
                    content=msg["content"],
                    timestamp=msg.get("timestamp")
                )
                for msg in messages
            ]
        except Exception as e:
            logger.error(f"Error retrieving conversation history: {str(e)}")
            return []

    async def save_message(
        self,
        user_id: str,
        conversation_id: str,
        role: str,
        content: str,
        sources: Optional[List[Dict]] = None
    ) -> None:
        """Save a message to Firestore."""
        try:
            await firestore_db.save_message(
                user_id, conversation_id, role, content, sources
            )
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            raise

    async def create_or_update_conversation(
        self,
        user_id: str,
        conversation_id: Optional[str] = None,
        query: str = None,
        prompt_type: str = "explanation",
        is_temporary: bool = False
    ) -> str:
        """Create new conversation or update existing one in Firestore."""
        try:
            if is_temporary:
                return conversation_id or str(uuid4())

            return await firestore_db.get_or_create_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                query=query,
                prompt_type=prompt_type,
                is_temporary=is_temporary
            )
        except Exception as e:
            logger.error(f"Error creating/updating conversation: {str(e)}")
            raise

    async def chat(
        self,
        user_id: str,
        query: str,
        conversation_id: Optional[str] = None,
        include_history: bool = True,
        prompt_type: str = "explanation",
        is_temporary: bool = False
    ) -> Dict[str, Any]:
        """
        Process a chat query using RAG with Firestore storage.

        Args:
            user_id: User ID from Firebase
            query: User's question
            conversation_id: Optional conversation ID for follow-ups
            include_history: Whether to include conversation history

        Returns:
            Dict containing response, sources, and conversation_id
        """
        try:
            # Create or get conversation (or a transient one)
            conversation_id = await self.create_or_update_conversation(
                user_id=user_id,
                conversation_id=conversation_id,
                query=query,
                prompt_type=prompt_type,
                is_temporary=is_temporary
            )

            # Get conversation history if requested and persisted
            history = []
            if include_history and conversation_id and not is_temporary:
                history = await self.get_conversation_history(
                    user_id, conversation_id
                )

            # Save user message when persistence is enabled
            if not is_temporary:
                await self.save_message(user_id, conversation_id, "user", query)

            # Retrieve relevant documents asynchronously
            relevant_docs = await vector_store.similarity_search_async(
                query, k=settings.top_k_results)

            # Build context from retrieved documents with better formatting
            context_parts = []
            for doc in relevant_docs:
                # Safely extract metadata with defaults
                metadata = doc.get('metadata', {})
                source_name = metadata.get(
                    'source', 'Unknown Source').replace('.pdf', '')
                doc_text = doc.get('text', '')

                if doc_text.strip():  # Only add non-empty documents
                    context_parts.append(
                        f"📖 **From {source_name}:**\n{doc_text}"
                    )

            # Build context - can be empty if no relevant docs found
            context = "\n\n---\n\n".join(context_parts)

            # Create teaching prompt
            prompt = self._create_teaching_prompt(
                query, context, history, prompt_type
            )

            # Generate response
            logger.info(f"Generating response for query: {query[:50]}...")
            try:
                response = self.model.generate_content(
                    prompt,
                    generation_config=self.generation_config
                )
            except Exception as e:
                err_text = str(e)
                # Try to extract suggested wait time from the error
                wait_seconds = None
                # Pattern 1: "Please retry in 43.40s"
                m = re.search(
                    r"Please retry in\s*([0-9]+)(?:\.[0-9]+)?s", err_text)
                if m:
                    wait_seconds = int(m.group(1))
                # Pattern 2: retry_delay {\n  seconds: 43\n}
                if wait_seconds is None:
                    m2 = re.search(
                        r"retry_delay\s*\{[^}]*seconds:\s*(\d+)", err_text)
                    if m2:
                        wait_seconds = int(m2.group(1))

                if "429" in err_text or "quota" in err_text.lower():
                    wait_hint = f" Please wait ~{wait_seconds}s and try again." if wait_seconds else " Please wait a bit and try again."
                    friendly_message = (
                        "⏳ You're temporarily rate-limited by the Gemini free tier." +
                        wait_hint +
                        " If this happens often, consider switching models or enabling billing for higher limits."
                    )

                    return {
                        "message": friendly_message,
                        "conversation_id": conversation_id,
                        "sources": [],
                        "follow_up_questions": [],
                        "prompt_type": prompt_type,
                        "is_temporary": is_temporary
                    }
                # For other model errors (e.g., 404 if model unavailable), surface a friendly message
                if "404" in err_text:
                    return {
                        "message": "The selected model is unavailable right now. Please try again shortly.",
                        "conversation_id": conversation_id,
                        "sources": [],
                        "follow_up_questions": [],
                        "prompt_type": prompt_type,
                        "is_temporary": is_temporary
                    }
                # Unknown error -> re-raise to be handled upstream
                raise

            # Safely extract response text
            if not response or not hasattr(response, 'text') or not response.text:
                raise ValueError("Empty response received from Gemini API")

            assistant_message = response.text.strip()

            if not assistant_message:
                raise ValueError(
                    "Response message is empty after stripping whitespace")

            # Prepare sources with better metadata and safer extraction
            sources = []
            for doc in relevant_docs[:3]:  # Top 3 sources
                metadata = doc.get('metadata', {})
                # Only add source if we have the required fields
                if metadata.get('source'):
                    sources.append({
                        "source": metadata['source'],
                        "chunk_id": metadata.get('chunk_id', -1),
                        "relevance_score": round(1 - doc.get('distance', 0), 2) if doc.get('distance') is not None else 0.95
                    })

            # Save assistant message
            if not is_temporary:
                await self.save_message(
                    user_id, conversation_id, "assistant", assistant_message, sources
                )

            # Generate follow-up questions
            follow_up_questions = self._generate_follow_up_questions(
                query, assistant_message)

            return {
                "message": assistant_message,
                "conversation_id": conversation_id,
                "sources": sources,
                "follow_up_questions": follow_up_questions,
                "prompt_type": prompt_type,
                "is_temporary": is_temporary
            }

        except Exception as e:
            logger.error(f"Error in chat service: {str(e)}")
            raise

    async def get_user_conversations(
        self,
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a user from Firestore."""
        try:
            return await firestore_db.get_user_conversations(user_id, limit)
        except Exception as e:
            logger.error(f"Error getting user conversations: {str(e)}")
            return []

    async def delete_conversation(
        self,
        user_id: str,
        conversation_id: str
    ) -> bool:
        """Delete a conversation."""
        try:
            return await firestore_db.delete_conversation(user_id, conversation_id)
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False

    async def search_conversations(
        self,
        user_id: str,
        search_query: str
    ) -> List[Dict[str, Any]]:
        """Search conversations by title."""
        try:
            results = await firestore_db.search_conversations(user_id, search_query)

            # Enrich results with last message
            enriched = []
            for conv in results:
                messages = await firestore_db.get_conversation_messages(
                    user_id, conv["id"], limit=1
                )
                last_message = ""
                if messages:
                    last_message = messages[-1].get("content", "")[:100]

                enriched.append({
                    "conversation_id": conv["id"],
                    "title": conv.get("title", "Conversation"),
                    "last_message": last_message,
                    "message_count": conv.get("message_count", 0),
                    "created_at": conv.get("created_at"),
                    "updated_at": conv.get("updated_at"),
                })

            return enriched
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            return []

    async def update_conversation_title(
        self,
        user_id: str,
        conversation_id: str,
        new_title: str
    ) -> bool:
        """Update conversation title."""
        try:
            return await firestore_db.update_conversation_title(
                user_id, conversation_id, new_title
            )
        except Exception as e:
            logger.error(f"Error updating conversation title: {str(e)}")
            return False

    async def add_message_feedback(
        self,
        user_id: str,
        conversation_id: str,
        message_id: str,
        feedback: str
    ) -> bool:
        """Add feedback to a message."""
        try:
            return await firestore_db.add_message_feedback(
                user_id, conversation_id, message_id, feedback
            )
        except Exception as e:
            logger.error(f"Error adding message feedback: {str(e)}")
            return False

    async def get_conversation_for_export(
        self,
        user_id: str,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get conversation for export."""
        try:
            return await firestore_db.get_conversation_for_export(
                user_id, conversation_id
            )
        except Exception as e:
            logger.error(f"Error getting conversation for export: {str(e)}")
            return None

    def generate_pdf_export(self, conversation: Dict[str, Any]) -> BytesIO:
        """Generate PDF from conversation data."""
        try:
            buffer = BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter)

            # Get styles
            styles = getSampleStyleSheet()
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=16,
                textColor=colors.HexColor('#1f2937'),
                spaceAfter=12,
                alignment=TA_CENTER
            )

            heading_style = ParagraphStyle(
                'CustomHeading',
                parent=styles['Heading2'],
                fontSize=11,
                textColor=colors.HexColor('#374151'),
                spaceAfter=6,
                spaceBefore=6
            )

            normal_style = ParagraphStyle(
                'CustomNormal',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.HexColor('#4b5563'),
                spaceAfter=4
            )

            # Build document elements
            story = []

            # Title
            title = conversation.get('title', 'Conversation Export')
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 0.2*inch))

            # Metadata
            metadata_text = f"""
            <b>Created:</b> {conversation.get('created_at', 'N/A')}<br/>
            <b>Last Updated:</b> {conversation.get('updated_at', 'N/A')}<br/>
            <b>Total Messages:</b> {conversation.get('message_count', 0)}
            """
            story.append(Paragraph(metadata_text, normal_style))
            story.append(Spacer(1, 0.3*inch))

            # Messages
            story.append(Paragraph("Conversation Messages", heading_style))
            story.append(Spacer(1, 0.1*inch))

            messages = conversation.get('messages', [])
            for msg in messages:
                role = msg.get('role', 'unknown').upper()
                content = msg.get('content', '')
                timestamp = msg.get('timestamp', 'N/A')

                # Role indicator with timestamp
                role_text = f"<b>{role}</b> - {timestamp}"
                story.append(Paragraph(role_text, heading_style))

                # Content
                content_text = content.replace(
                    '\n', '<br/>').replace('<', '&lt;').replace('>', '&gt;')
                story.append(Paragraph(content_text, normal_style))
                story.append(Spacer(1, 0.1*inch))

            # Build PDF
            doc.build(story)
            buffer.seek(0)
            return buffer

        except Exception as e:
            logger.error(f"Error generating PDF: {str(e)}")
            raise


# Singleton instance
chat_service = ChatService()
