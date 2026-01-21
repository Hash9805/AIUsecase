from typing import List, Dict
import streamlit as st
from groq import Groq
from config import MAX_CONVERSATION_HISTORY


class ChatLogic:
    def __init__(self):
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        self.conversation_history = []
        self.max_history = MAX_CONVERSATION_HISTORY
        self.model = "llama3-8b-8192"


    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })

        # Keep only last N messages
        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def get_conversation_history(self) -> List[Dict]:
        return self.conversation_history.copy()

    def clear_history(self):
        self.conversation_history = []

    def detect_intent(self, user_message: str) -> str:
        """Detect user intent: booking / question / general"""
        text = user_message.lower()

        booking_keywords = [
            "book", "appointment", "schedule", "reserve",
            "haircut", "facial", "manicure", "pedicure",
            "spa", "massage", "makeup", "coloring"
        ]

        question_keywords = [
            "what", "when", "where", "how", "price",
            "cost", "services", "offer", "available"
        ]

        for k in booking_keywords:
            if k in text:
                return "booking"

        for k in question_keywords:
            if k in text:
                return "question"

        return "general"

    def generate_response(
        self,
        user_message: str,
        system_prompt: str = None,
        rag_context: str = None
    ) -> str:
        """Generate AI response using Groq (LLM layer of RAG)"""

        try:
            messages = []

            # System instruction
            messages.append({
                "role": "system",
                "content": system_prompt or
                "You are a friendly salon booking assistant. "
                "Answer clearly and concisely (2–3 sentences)."
            })

            # RAG augmentation
            if rag_context:
                messages.append({
                    "role": "system",
                    "content": f"Use this salon information to answer:\n{rag_context}"
                })

            # Conversation memory
            messages.extend(self.conversation_history[-6:])

            # User message
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.6,
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception:
            return (
                "Sorry 😕 I’m having trouble answering right now. "
                "Please try again in a moment."
            )

    def get_summary_for_context(self) -> str:
        if not self.conversation_history:
            return "No previous conversation."

        recent = self.conversation_history[-4:]
        return "\n".join(
            f"{msg['role']}: {msg['content'][:100]}"
            for msg in recent
        )
