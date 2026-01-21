# 💅 Glamour Salon - AI Booking Assistant

An intelligent conversational AI booking assistant for salon appointments with RAG capabilities, built using Streamlit, OpenAI, and LangChain.

## 🌟 Features

### Core Features
- **💬 Conversational AI Chatbot** - Natural language booking flow
- **📚 RAG (Retrieval Augmented Generation)** - Upload PDFs and get context-aware answers
- **🎯 Multi-turn Booking Flow** - Intelligent slot filling for appointments
- **✉️ Email Confirmations** - Automated booking confirmation emails
- **🔐 Admin Dashboard** - View, filter, and export all bookings
- **💾 Database Storage** - SQLite for persistent booking data
- **🧠 Short-term Memory** - Maintains context for last 20-25 messages

### Advanced Features
- **Intent Detection** - Automatically detects booking vs query intents
- **Field Validation** - Email, phone, date, and time format validation
- **Error Handling** - Graceful error messages for all failure scenarios
- **Tool Calling** - RAG tool, Booking persistence tool, Email tool
- **Responsive UI** - Clean, professional Streamlit interface

## 🏗️ Architecture

```
AIUsecase/
├── app/
│   ├── main.py              # Main Streamlit application
│   ├── chat_logic.py        # Conversation management & intent detection
│   ├── booking_flow.py      # Booking slot filling logic
│   └── admin_dashboard.py   # Admin interface for viewing bookings
├── models/
│   └── __init__.py          # SQLAlchemy database models
├── utils/
│   ├── rag_pipeline.py      # RAG implementation with FAISS
│   ├── email_service.py     # Email confirmation service
│   └── tools.py             # Tool implementations
├── config/
│   └── __init__.py          # Configuration and constants
├── database/                # SQLite database files
├── vector_store/            # FAISS vector store
├── uploads/                 # Uploaded PDF files
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## 🚀 Getting Started

### Prerequisites
- Python 3.8+
- OpenAI API Key
- Gmail account (for email confirmations)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd AIUsecase
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**

Create a `.streamlit/secrets.toml` file:
```toml
OPENAI_API_KEY = "your-openai-api-key"
EMAIL_USER = "your-email@gmail.com"
EMAIL_PASSWORD = "your-app-password"
```

**Note:** For Gmail, you need to generate an [App Password](https://support.google.com/accounts/answer/185833)

4. **Run the application**
```bash
streamlit run app/main.py
```

## 📖 Usage Guide

### For Customers

1. **Ask Questions**
   - Upload salon PDFs (services, pricing, policies)
   - Ask any question about the salon
   - Get AI-powered answers with RAG

2. **Book Appointments**
   - Say "I want to book an appointment" or similar
   - Provide requested information (name, email, phone, service, date, time)
   - Confirm your booking
   - Receive email confirmation

### For Admins

1. Navigate to "🔐 Admin Dashboard"
2. View all bookings in table format
3. Filter by name, email, or date
4. Export data as CSV
5. View service statistics

## 🛠️ Configuration

### Salon Services
Edit `config/__init__.py` to customize available services:
```python
SALON_SERVICES = [
    "Haircut",
    "Hair Coloring",
    "Manicure",
    "Pedicure",
    "Facial",
    "Massage",
    "Hair Spa",
    "Bridal Makeup",
    "Party Makeup"
]
```

### Business Hours
```python
BUSINESS_HOURS = {
    "start": "09:00",
    "end": "20:00"
}
```

## 📊 Database Schema

### Customers Table
- `customer_id` (PK)
- `name`
- `email` (unique)
- `phone`
- `created_at`

### Bookings Table
- `id` (PK)
- `customer_id` (FK)
- `booking_type`
- `date`
- `time`
- `status`
- `created_at`

## 🔧 Technical Details

### RAG Pipeline
- **Text Splitting:** RecursiveCharacterTextSplitter (1000 chars, 200 overlap)
- **Embeddings:** OpenAI text-embedding-3-small
- **Vector Store:** FAISS (lightweight, in-memory)
- **Retrieval:** Top-3 similarity search

### LLM
- **Model:** GPT-3.5-turbo
- **Temperature:** 0.7
- **Max Tokens:** 300
- **Context:** Last 20-25 messages

### Email Service
- **Protocol:** SMTP (Gmail)
- **Port:** 587 (TLS)
- **Format:** HTML with styled template

## 🚀 Deployment on Streamlit Cloud

1. **Push code to GitHub**
```bash
git add .
git commit -m "Initial commit"
git push origin main
```

2. **Deploy on Streamlit Cloud**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Connect your GitHub repository
   - Select `app/main.py` as main file
   - Add secrets in Streamlit Cloud settings

3. **Add Secrets**
   - Navigate to App Settings → Secrets
   - Add your API keys and email credentials

## 🧪 Testing Checklist

- [ ] PDF upload and processing
- [ ] RAG-based Q&A
- [ ] Booking intent detection
- [ ] Complete booking flow
- [ ] Field validation (email, phone, date, time)
- [ ] Booking confirmation summary
- [ ] Database storage
- [ ] Email delivery
- [ ] Admin dashboard access
- [ ] Booking filters
- [ ] CSV export
- [ ] Error handling
- [ ] Conversation memory

## 🎯 Future Enhancements

- [ ] Speech-to-Text (STT) integration
- [ ] Text-to-Speech (TTS) output
- [ ] Booking retrieval by customer
- [ ] Admin: Edit/Cancel bookings
- [ ] Multi-language support
- [ ] Payment integration
- [ ] SMS notifications
- [ ] Calendar sync

## 🐛 Known Limitations

- SQLite may reset on Streamlit Cloud restart (expected for assignment)
- Email requires Gmail App Password setup
- RAG quality depends on uploaded PDF content
- No authentication system (simplified for demo)

## 📝 License

This project is created for the Neostats Analytics AI Engineer assessment.

## 👤 Author

**Your Name**
- GitHub: [@yourusername](https://github.com/yourusername)
- Email: your.email@example.com

## 🙏 Acknowledgments

- OpenAI for GPT models
- Streamlit for the amazing framework
- LangChain for RAG tools
- Anthropic Claude for development assistance