from typing import Dict, List, Any
from datetime import datetime, timedelta


class ConversationManager:
    """
    Manages conversation history for each user.
    Stores conversation context in memory (can be upgraded to Redis/DB later).
    """

    def __init__(self):
        # Format: {user_id: {"messages": [...], "last_updated": datetime}}
        self.conversations: Dict[int, Dict[str, Any]] = {}
        self.timeout_minutes = 30  # Clear conversation after 30 minutes of inactivity

    def get_history(self, user_id: int) -> List[Dict[str, str]]:
        """Get conversation history for a user"""
        self._cleanup_old_conversations()

        if user_id not in self.conversations:
            return []

        return self.conversations[user_id]["messages"]

    def add_message(self, user_id: int, role: str, content: str):
        """Add a message to user's conversation history"""
        if user_id not in self.conversations:
            self.conversations[user_id] = {
                "messages": [],
                "last_updated": datetime.now()
            }

        self.conversations[user_id]["messages"].append({
            "role": role,
            "content": content
        })
        self.conversations[user_id]["last_updated"] = datetime.now()

        # Keep only last 20 messages to avoid token limits
        if len(self.conversations[user_id]["messages"]) > 20:
            self.conversations[user_id]["messages"] = self.conversations[user_id]["messages"][-20:]

    def clear_history(self, user_id: int):
        """Clear conversation history for a user"""
        if user_id in self.conversations:
            del self.conversations[user_id]

    def _cleanup_old_conversations(self):
        """Remove conversations that have been inactive for too long"""
        cutoff_time = datetime.now() - timedelta(minutes=self.timeout_minutes)
        expired_users = [
            user_id for user_id, data in self.conversations.items()
            if data["last_updated"] < cutoff_time
        ]
        for user_id in expired_users:
            del self.conversations[user_id]


# Global instance
conversation_manager = ConversationManager()
