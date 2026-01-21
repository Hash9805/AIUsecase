from typing import List, Dict
from config import MAX_CONVERSATION_HISTORY


class ChatLogic:
    """Manages conversation flow and intent detection (Rule-based, No OpenAI)"""

    def __init__(self, openai_api_key: str = None):
        self.conversation_history = []
        self.max_history = MAX_CONVERSATION_HISTORY

    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

        # Keep only last MAX_CONVERSATION_HISTORY messages
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history"""
        return self.conversation_history.copy()

    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

    def detect_intent(self, user_message: str) -> str:
        """Detect user intent: 'booking', 'question', or 'general'"""
        user_message_lower = user_message.lower()

        booking_keywords = [
            "book", "appointment", "schedule", "reserve",
            "haircut", "facial", "manicure", "pedicure",
            "spa", "massage", "makeup", "coloring"
        ]

        question_keywords = [
            "what", "when", "where", "how", "price",
            "cost", "services", "offer", "available"
        ]

        for word in booking_keywords:
            if word in user_message_lower:
                return "booking"

        for word in question_keywords:
            if word in user_message_lower:
                return "question"

        return "general"

    def generate_response(
        self,
        user_message: str,
        system_prompt: str = None,
        rag_context: str = None
    ) -> str:
        """
        Rule-based response generator (NO OpenAI, NO paid APIs)
        """

        intent = self.detect_intent(user_message)

        if intent == "booking":
            return (
                "✨ Great! I can help you book an appointment.\n\n"
                "Please tell me:\n"
                "• Service you want (haircut, facial, etc.)\n"
                "• Preferred date\n"
                "• Preferred time slot"
            )

        if intent == "question":
            return (
                "💇‍♀️ We offer the following services:\n\n"
                "• Haircuts & Styling\n"
                "• Hair Coloring\n"
                "• Facials & Skincare\n"
                "• Manicure & Pedicure\n"
                "• Makeup & Spa Services\n\n"
                "Would you like to book an appointment?"
            )

        return (
            "Hi 👋 Welcome to **Glamour Salon**!\n\n"
            "You can ask me about our services or say:\n"
            "👉 *I want to book a haircut tomorrow*"
        )

    def get_summary_for_context(self) -> str:
        """Get a summary of recent conversation"""
        if not self.conversation_history:
            return "No previous conversation."

        recent = self.conversation_history[-4:]
        return "\n".join(
            f"{msg['role']}: {msg['content'][:100]}"
            for msg in recent
        )
