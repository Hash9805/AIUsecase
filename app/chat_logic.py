from typing import List, Dict
from config import MAX_CONVERSATION_HISTORY
from groq import Groq
import streamlit as st

class ChatLogic:
    """Manages conversation flow and intent detection using Groq AI"""
    
    def __init__(self, groq_api_key: str):
        self.client = Groq(api_key=groq_api_key)
        self.conversation_history = []
        self.max_history = MAX_CONVERSATION_HISTORY
        self.model = "llama-3.3-70b-versatile"  # Updated model
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history"""
        self.conversation_history.append({
            "role": role,
            "content": content
        })
        
        # Keep only last MAX_CONVERSATION_HISTORY messages
        if len(self.conversation_history) > self.max_history:
            system_msgs = [m for m in self.conversation_history if m['role'] == 'system']
            other_msgs = [m for m in self.conversation_history if m['role'] != 'system']
            other_msgs = other_msgs[-(self.max_history-len(system_msgs)):]
            self.conversation_history = system_msgs + other_msgs
    
    def get_conversation_history(self) -> List[Dict]:
        """Get current conversation history"""
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def detect_intent(self, user_message: str) -> str:
        """Detect user intent: 'booking', 'question', or 'general'"""
        user_message_lower = user_message.lower()
        
        # Booking keywords
        booking_keywords = [
            'book', 'appointment', 'schedule', 'reserve',
            'want', 'need', 'like to', 'interested',
            'haircut', 'coloring', 'manicure', 'pedicure',
            'facial', 'massage', 'spa', 'makeup'
        ]
        
        # Question keywords
        question_keywords = [
            'what', 'when', 'where', 'how', 'why', 'which',
            'tell me', 'show me', 'explain', '?'
        ]
        
        # Check for booking intent
        for keyword in booking_keywords:
            if keyword in user_message_lower:
                return 'booking'
        
        # Check for question intent
        for keyword in question_keywords:
            if keyword in user_message_lower:
                return 'question'
        
        return 'general'
    
    def generate_response(
        self,
        user_message: str,
        system_prompt: str = None,
        rag_context: str = None
    ) -> str:
        """Generate AI response using Groq"""
        try:
            messages = []
            
            # Add system prompt
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            else:
                default_system = """You are a helpful and friendly salon booking assistant for Glamour Salon. 
Your role is to help customers book appointments and answer questions about salon services.
Be warm, professional, and concise. Keep responses friendly but brief (2-3 sentences max)."""
                messages.append({"role": "system", "content": default_system})
            
            # Add RAG context if available
            if rag_context:
                context_message = f"Here is relevant information from our salon documents:\n\n{rag_context}\n\nUse this information to answer the customer's question."
                messages.append({"role": "system", "content": context_message})
            
            # Add conversation history (last few messages)
            recent_history = self.conversation_history[-6:] if len(self.conversation_history) > 6 else self.conversation_history
            messages.extend(recent_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})
            
            # Generate response using Groq
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=300,
                top_p=1,
                stream=False
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I'm having trouble generating a response right now. Error: {str(e)}"
    
    def get_summary_for_context(self) -> str:
        """Get a summary of recent conversation for context"""
        if not self.conversation_history:
            return "No previous conversation."
        
        recent = self.conversation_history[-4:]
        summary = "\n".join([f"{msg['role']}: {msg['content'][:100]}..." for msg in recent])
        return summary