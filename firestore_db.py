from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import uuid
import asyncio

from firebase_admin import firestore
from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Firestore
db = firestore.client()

CONVERSATIONS_COLLECTION = "conversations"
MESSAGES_COLLECTION = "messages"


class FirestoreDB:
    """Firestore database operations for chat history and conversations."""

    @staticmethod
    async def create_conversation(
        user_id: str,
        title: str,
        conversation_id: Optional[str] = None,
        prompt_type: str = "explanation",
        is_temporary: bool = False
    ) -> str:
        """Create a new conversation."""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())

        conversation_data = {
            "id": conversation_id,
            "user_id": user_id,
            "title": title,
            "prompt_type": prompt_type,
            "is_temporary": is_temporary,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "message_count": 0,
        }

        try:
            # Wrap synchronous Firestore operation in thread
            def _create_conv():
                db.collection("users").document(user_id).collection(
                    CONVERSATIONS_COLLECTION
                ).document(conversation_id).set(conversation_data)
            
            await asyncio.to_thread(_create_conv)

            logger.info(
                f"Created conversation {conversation_id} for user {user_id}")
            return conversation_id
        except Exception as e:
            logger.error(f"Error creating conversation: {str(e)}")
            raise

    @staticmethod
    async def save_message(
        user_id: str,
        conversation_id: str,
        role: str,
        content: str,
        sources: Optional[List[Dict]] = None
    ) -> str:
        """Save a message to a conversation."""
        message_id = str(uuid.uuid4())

        message_data = {
            "id": message_id,
            "role": role,
            "content": content,
            "sources": sources or [],
            "timestamp": datetime.utcnow(),
        }

        try:
            # Wrap synchronous Firestore operations in thread
            def _save_msg():
                # Store in: users/{user_id}/conversations/{conversation_id}/messages/{message_id}
                db.collection("users").document(user_id).collection(
                    CONVERSATIONS_COLLECTION
                ).document(conversation_id).collection(MESSAGES_COLLECTION).document(
                    message_id
                ).set(message_data)

                # Update conversation's updated_at and message_count
                conversation_ref = (
                    db.collection("users")
                    .document(user_id)
                    .collection(CONVERSATIONS_COLLECTION)
                    .document(conversation_id)
                )
                conversation_ref.update({
                    "updated_at": datetime.utcnow(),
                    "message_count": firestore.Increment(1),
                })
            
            await asyncio.to_thread(_save_msg)

            logger.info(
                f"Saved message {message_id} to conversation {conversation_id}")
            return message_id
        except Exception as e:
            logger.error(f"Error saving message: {str(e)}")
            raise

    @staticmethod
    async def get_conversation_messages(
        user_id: str,
        conversation_id: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get all messages in a conversation."""
        try:
            # Wrap synchronous Firestore operations in thread
            def _get_messages():
                messages_ref = (
                    db.collection("users")
                    .document(user_id)
                    .collection(CONVERSATIONS_COLLECTION)
                    .document(conversation_id)
                    .collection(MESSAGES_COLLECTION)
                    .order_by("timestamp")
                    .limit(limit)
                )

                docs = messages_ref.stream()
                return [doc.to_dict() for doc in docs]
            
            messages = await asyncio.to_thread(_get_messages)

            logger.info(
                f"Retrieved {len(messages)} messages from conversation {conversation_id}")
            return messages
        except Exception as e:
            logger.error(f"Error retrieving messages: {str(e)}")
            return []

    @staticmethod
    async def get_user_conversations(
        user_id: str,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """Get all conversations for a user."""
        try:
            # Wrap synchronous Firestore operations in thread
            def _get_conversations():
                conversations_ref = (
                    db.collection("users")
                    .document(user_id)
                    .collection(CONVERSATIONS_COLLECTION)
                    .order_by("updated_at", direction=firestore.Query.DESCENDING)
                    .limit(limit)
                )

                docs = conversations_ref.stream()
                conversations = []

                for doc in docs:
                    conv_data = doc.to_dict()
                    # Get last message
                    messages_ref = (
                        db.collection("users")
                        .document(user_id)
                        .collection(CONVERSATIONS_COLLECTION)
                        .document(conv_data["id"])
                        .collection(MESSAGES_COLLECTION)
                        .order_by("timestamp", direction=firestore.Query.DESCENDING)
                        .limit(1)
                    )

                    last_msg_docs = messages_ref.stream()
                    last_message = ""

                    for msg_doc in last_msg_docs:
                        last_message = msg_doc.to_dict().get("content", "")[:100]

                    conversations.append({
                        "conversation_id": conv_data["id"],
                        "title": conv_data.get("title", "Conversation"),
                        "last_message": last_message,
                        "message_count": conv_data.get("message_count", 0),
                        "created_at": conv_data.get("created_at"),
                        "updated_at": conv_data.get("updated_at"),
                        "prompt_type": conv_data.get("prompt_type", "explanation"),
                        "is_temporary": conv_data.get("is_temporary", False),
                    })

                return conversations
            
            conversations = await asyncio.to_thread(_get_conversations)

            logger.info(
                f"Retrieved {len(conversations)} conversations for user {user_id}")
            return conversations
        except Exception as e:
            logger.error(f"Error retrieving conversations: {str(e)}")
            return []

    @staticmethod
    async def get_or_create_conversation(
        user_id: str,
        conversation_id: Optional[str] = None,
        query: str = None,
        prompt_type: str = "explanation",
        is_temporary: bool = False
    ) -> str:
        """Get existing conversation or create new one."""
        try:
            # Wrap synchronous Firestore operations in thread
            def _get_or_create():
                if conversation_id:
                    # Check if conversation exists
                    conv_ref = (
                        db.collection("users")
                        .document(user_id)
                        .collection(CONVERSATIONS_COLLECTION)
                        .document(conversation_id)
                    )
                    conv_doc = conv_ref.get()

                    if conv_doc.exists:
                        # Update updated_at
                        update_payload = {"updated_at": datetime.utcnow()}
                        if prompt_type:
                            update_payload["prompt_type"] = prompt_type
                        update_payload["is_temporary"] = is_temporary
                        conv_ref.update(update_payload)
                        return conversation_id

                # Create new conversation
                new_conv_id = str(uuid.uuid4())
                # Use a placeholder title that will be replaced after generating the response
                title = "New Conversation"

                new_conv_data = {
                    "id": new_conv_id,
                    "user_id": user_id,
                    "title": title,
                    "prompt_type": prompt_type,
                    "is_temporary": is_temporary,
                    "created_at": datetime.utcnow(),
                    "updated_at": datetime.utcnow(),
                    "message_count": 0,
                }
                
                db.collection("users").document(user_id).collection(
                    CONVERSATIONS_COLLECTION
                ).document(new_conv_id).set(new_conv_data)
                
                return new_conv_id
            
            result = await asyncio.to_thread(_get_or_create)
            return result

        except Exception as e:
            logger.error(f"Error getting/creating conversation: {str(e)}")
            raise

    @staticmethod
    async def delete_conversation(
        user_id: str,
        conversation_id: str
    ) -> bool:
        """Delete a conversation and all its messages."""
        try:
            # Wrap synchronous Firestore operations in thread
            def _delete():
                conv_ref = (
                    db.collection("users")
                    .document(user_id)
                    .collection(CONVERSATIONS_COLLECTION)
                    .document(conversation_id)
                )

                # Delete all messages first
                messages_ref = conv_ref.collection(MESSAGES_COLLECTION)
                for doc in messages_ref.stream():
                    doc.reference.delete()

                # Delete the conversation
                conv_ref.delete()
            
            await asyncio.to_thread(_delete)

            logger.info(
                f"Deleted conversation {conversation_id} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting conversation: {str(e)}")
            return False

    @staticmethod
    async def search_conversations(
        user_id: str,
        search_query: str
    ) -> List[Dict[str, Any]]:
        """Search conversations by title or last message."""
        try:
            # Wrap synchronous Firestore operations in thread
            def _search():
                conversations_ref = (
                    db.collection("users")
                    .document(user_id)
                    .collection(CONVERSATIONS_COLLECTION)
                    .order_by("updated_at", direction=firestore.Query.DESCENDING)
                )

                all_convs = [doc.to_dict() for doc in conversations_ref.stream()]

                # Client-side filtering for title matching
                search_lower = search_query.lower()
                filtered = [
                    conv
                    for conv in all_convs
                    if search_lower in conv.get("title", "").lower()
                ]

                return filtered[:20]  # Return top 20
            
            filtered = await asyncio.to_thread(_search)

            logger.info(
                f"Found {len(filtered)} conversations matching '{search_query}'")
            return filtered
        except Exception as e:
            logger.error(f"Error searching conversations: {str(e)}")
            return []

    @staticmethod
    async def update_conversation_title(
        user_id: str,
        conversation_id: str,
        new_title: str
    ) -> bool:
        """Update conversation title."""
        try:
            # Wrap synchronous Firestore operations in thread
            def _update():
                conv_ref = (
                    db.collection("users")
                    .document(user_id)
                    .collection(CONVERSATIONS_COLLECTION)
                    .document(conversation_id)
                )

                conv_doc = conv_ref.get()
                if not conv_doc.exists:
                    logger.warning(f"Conversation {conversation_id} not found")
                    return False

                conv_ref.update({
                    "title": new_title,
                    "updated_at": datetime.utcnow()
                })
                return True
            
            result = await asyncio.to_thread(_update)
            
            if result:
                logger.info(
                    f"Updated conversation {conversation_id} title to '{new_title}'")
            return result
        except Exception as e:
            logger.error(f"Error updating conversation title: {str(e)}")
            return False

    @staticmethod
    async def add_message_feedback(
        user_id: str,
        conversation_id: str,
        message_id: str,
        feedback: str
    ) -> bool:
        """Add feedback to a message (helpful/not_helpful)."""
        try:
            # Wrap synchronous Firestore operations in thread
            def _add_feedback():
                message_ref = (
                    db.collection("users")
                    .document(user_id)
                    .collection(CONVERSATIONS_COLLECTION)
                    .document(conversation_id)
                    .collection(MESSAGES_COLLECTION)
                    .document(message_id)
                )

                msg_doc = message_ref.get()
                if not msg_doc.exists:
                    logger.warning(f"Message {message_id} not found")
                    return False

                message_ref.update({
                    "feedback": feedback,
                    "feedback_timestamp": datetime.utcnow()
                })
                return True
            
            result = await asyncio.to_thread(_add_feedback)
            
            if result:
                logger.info(f"Added feedback to message {message_id}: {feedback}")
            return result
        except Exception as e:
            logger.error(f"Error adding message feedback: {str(e)}")
            return False

    @staticmethod
    async def get_conversation_for_export(
        user_id: str,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get complete conversation with all messages for export."""
        try:
            # Wrap synchronous Firestore operations in thread
            def _get_for_export():
                conv_ref = (
                    db.collection("users")
                    .document(user_id)
                    .collection(CONVERSATIONS_COLLECTION)
                    .document(conversation_id)
                )

                conv_doc = conv_ref.get()
                if not conv_doc.exists:
                    logger.warning(f"Conversation {conversation_id} not found")
                    return None

                conv_data = conv_doc.to_dict()

                # Get all messages
                messages_ref = (
                    db.collection("users")
                    .document(user_id)
                    .collection(CONVERSATIONS_COLLECTION)
                    .document(conversation_id)
                    .collection(MESSAGES_COLLECTION)
                    .order_by("timestamp")
                )

                messages = [doc.to_dict() for doc in messages_ref.stream()]

                conv_data["messages"] = messages
                return conv_data
            
            conv_data = await asyncio.to_thread(_get_for_export)
            
            if conv_data:
                logger.info(
                    f"Retrieved conversation {conversation_id} with {len(conv_data.get('messages', []))} messages for export")
            return conv_data
        except Exception as e:
            logger.error(f"Error retrieving conversation for export: {str(e)}")
            return None


# Initialize Firestore database
firestore_db = FirestoreDB()
