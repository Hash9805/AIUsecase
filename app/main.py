import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from models import init_db
from utils.rag_pipeline import RAGPipeline
from utils.tools import BookingTools
from app.chat_logic import ChatLogic
from app.booking_flow import BookingFlow
from app.admin_dashboard import show_admin_dashboard
from config import OPENAI_API_KEY, SALON_SERVICES, UPLOAD_DIR
import os

# Page configuration
st.set_page_config(
    page_title="Glamour Salon - AI Booking Assistant",
    page_icon="💅",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF69B4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stChatMessage {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 10px;
        margin: 5px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize database
init_db()

# DEFINE FUNCTION FIRST - BEFORE IT'S CALLED
def process_message(user_message: str) -> str:
    """Process user message and generate response"""
    
    # Check for confirmation in booking mode
    if st.session_state.booking_mode and st.session_state.booking_flow.confirmation_pending:
        user_lower = user_message.lower().strip()
        
        if user_lower in ['yes', 'y', 'confirm', 'correct', 'yeah', 'yep']:
            # Confirm and save booking
            booking_data = st.session_state.booking_flow.booking_data
            
            # Save to database
            result = st.session_state.booking_tools.booking_persistence_tool(booking_data)
            
            if result['success']:
                booking_id = result['booking_id']
                
                # Send email
                email_result = st.session_state.booking_tools.email_tool(
                    to_email=booking_data['email'],
                    customer_name=booking_data['name'],
                    booking_id=booking_id,
                    booking_type=booking_data['booking_type'],
                    date=booking_data['date'],
                    time=booking_data['time']
                )
                
                # Reset booking flow
                st.session_state.booking_mode = False
                st.session_state.booking_flow.reset()
                
                response = f"""✅ **Booking Confirmed!**

Your appointment has been successfully booked!

**Booking ID:** #{booking_id}
**Service:** {booking_data['booking_type']}
**Date:** {booking_data['date']}
**Time:** {booking_data['time']}

{email_result['message']}

We look forward to seeing you! 💅"""
                
                return response
            else:
                return f"❌ Sorry, there was an error saving your booking: {result['message']}\n\nPlease try again."
        
        elif user_lower in ['no', 'n', 'incorrect', 'wrong', 'nope']:
            st.session_state.booking_flow.reset()
            st.session_state.booking_flow.confirmation_pending = False
            return "No problem! Let's start over. What would you like to change?"
        
        else:
            return "Please reply with 'yes' to confirm or 'no' to make changes."
    
    # Check if in booking mode
    if st.session_state.booking_mode:
        # Extract information from message
        extracted = st.session_state.booking_flow.extract_info_from_message(user_message)
        
        if extracted:
            st.session_state.booking_flow.update_booking_data(extracted)
        
        # Check if all fields are collected
        if st.session_state.booking_flow.is_complete():
            st.session_state.booking_flow.confirmation_pending = True
            return st.session_state.booking_flow.get_confirmation_summary()
        else:
            # Ask for missing information
            next_question = st.session_state.booking_flow.get_next_question()
            return next_question
    
    # Detect intent
    intent = st.session_state.chat_logic.detect_intent(user_message)
    
    if intent == 'booking':
        st.session_state.booking_mode = True
        extracted = st.session_state.booking_flow.extract_info_from_message(user_message)
        if extracted:
            st.session_state.booking_flow.update_booking_data(extracted)
        
        if st.session_state.booking_flow.is_complete():
            st.session_state.booking_flow.confirmation_pending = True
            return st.session_state.booking_flow.get_confirmation_summary()
        else:
            next_question = st.session_state.booking_flow.get_next_question()
            return f"Perfect! Let me help you book an appointment. {next_question}"
    
    elif intent == 'question':
        # Try RAG
        rag_result = st.session_state.booking_tools.rag_tool(user_message)
        
        if rag_result['success'] and rag_result['answer']:
            # Generate response with RAG context
            response = st.session_state.chat_logic.generate_response(
                user_message,
                rag_context=rag_result['answer']
            )
            return response
        else:
            # No RAG context, generate regular response
            return st.session_state.chat_logic.generate_response(user_message)
    
    else:
        # General conversation
        return st.session_state.chat_logic.generate_response(user_message)

# Initialize session state
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.session_state.messages = []
    st.session_state.booking_mode = False
    st.session_state.booking_flow = BookingFlow()
    st.session_state.page = "chat"
    
    # Check for API key
    api_key = OPENAI_API_KEY or st.secrets.get("OPENAI_API_KEY", "")
    if not api_key:
        st.error("⚠️ OpenAI API key not found. Please set it in Streamlit secrets.")
        st.stop()
    
    st.session_state.api_key = api_key
    st.session_state.rag_pipeline = RAGPipeline(api_key)
    st.session_state.rag_pipeline.load_existing_vector_store()
    st.session_state.booking_tools = BookingTools(st.session_state.rag_pipeline)
    st.session_state.chat_logic = ChatLogic(api_key)

# Sidebar
with st.sidebar:
    st.markdown("### 💅 Glamour Salon")
    st.markdown("---")
    
    # Navigation
    page = st.radio(
        "Navigation",
        ["💬 Chat & Booking", "🔐 Admin Dashboard"],
        key="nav_radio"
    )
    
    st.markdown("---")
    
    # PDF Upload Section
    st.markdown("### 📄 Upload Salon Documents")
    st.caption("Upload PDFs containing salon information, services, pricing, etc.")
    
    uploaded_files = st.file_uploader(
        "Choose PDF files",
        type=['pdf'],
        accept_multiple_files=True,
        key="pdf_uploader"
    )
    
    if uploaded_files:
        if st.button("Process PDFs", type="primary"):
            with st.spinner("Processing PDFs..."):
                # Save uploaded files
                pdf_paths = []
                for uploaded_file in uploaded_files:
                    file_path = UPLOAD_DIR / uploaded_file.name
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    pdf_paths.append(str(file_path))
                
                # Process PDFs
                success = st.session_state.rag_pipeline.process_pdfs(pdf_paths)
                
                if success:
                    st.success(f"✅ Processed {len(uploaded_files)} PDF(s) successfully!")
                else:
                    st.error("❌ Error processing PDFs")
    
    st.markdown("---")
    
    # Quick Actions
    st.markdown("### ⚡ Quick Actions")
    
    if st.button("🆕 Start New Booking"):
        st.session_state.booking_mode = True
        st.session_state.booking_flow.reset()
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Great! Let's book your appointment. Which service would you like?\n\n" + 
                      "\n".join([f"• {service}" for service in SALON_SERVICES])
        })
        st.rerun()
    
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.booking_mode = False
        st.session_state.booking_flow.reset()
        st.session_state.chat_logic.clear_history()
        st.rerun()
    
    st.markdown("---")
    st.caption("💡 Tip: Upload salon documents to enable RAG-based Q&A")

# Main content area
if page == "💬 Chat & Booking":
    # Header
    st.markdown('<div class="main-header">💅 Glamour Salon AI Assistant</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Book appointments & ask questions about our services</div>', unsafe_allow_html=True)
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.chat_logic.add_message("user", prompt)
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Process message - NOW THIS FUNCTION EXISTS!
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = process_message(prompt)
                st.markdown(response)
        
        # Add assistant message
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.session_state.chat_logic.add_message("assistant", response)
        
        st.rerun()

else:  # Admin Dashboard
    show_admin_dashboard()

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #666;'>"
    "💅 Glamour Salon AI Booking Assistant | Powered by OpenAI & Streamlit"
    "</div>",
    unsafe_allow_html=True
)