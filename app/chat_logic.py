from typing import List, Dict
import streamlit as st
from groq import Groq
from config import MAX_CONVERSATION_HISTORY


class ChatLogic:
    """Manages conversation flow and intent detection using Groq"""

    def __init__(self):
        self.client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        self.model = "llama3-8b-8192"
        self.conversation_history: List[Dict] = []
        self.max_history = MAX_CONVERSATION_HISTORY

    def add_message(self, role: str, content: str):
        self.conversation_history.append({
            "role": role,
            "content": content
        })

        if len(self.conversation_history) > self.max_history:
            self.conversation_history = self.conversation_history[-self.max_history:]

    def clear_history(self):
        self.conversation_history = []

    def detect_intent(self, user_message: str) -> str:
        msg = user_message.lower()

        booking_keywords = [
            "book", "appointment", "schedule", "reserve",
            "haircut", "facial", "massage", "spa", "makeup"
        ]

        question_keywords = [
            "what", "when", "where", "how", "why", "?"
        ]

        if any(k in msg for k in booking_keywords):
            return "booking"

        if any(k in msg for k in question_keywords):
            return "question"

        return "general"

    def generate_response(
        self,
        user_message: str,
        system_prompt: str = None,
        rag_context: str = None
    ) -> str:
        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                messages.append({
                    "role": "system",
                    "content": (
                        "You are a friendly salon booking assistant. "
                        "Help users book appointments and answer questions clearly."
                    )
                })

            if rag_context:
                messages.append({
                    "role": "system",
                    "content": f"Salon context:\n{rag_context}"
                })

            messages.extend(self.conversation_history[-6:])
            messages.append({"role": "user", "content": user_message})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:
            # TEMP: show real Groq error
            return f"Groq error: {str(e)}"
