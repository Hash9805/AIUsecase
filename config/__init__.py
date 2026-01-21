import os
from pathlib import Path

# Project paths
BASE_DIR = Path(__file__).parent.parent
VECTOR_STORE_DIR = BASE_DIR / "vector_store"
UPLOAD_DIR = BASE_DIR / "uploads"
DB_DIR = BASE_DIR / "database"

# Create directories if they don't exist
VECTOR_STORE_DIR.mkdir(exist_ok=True)
UPLOAD_DIR.mkdir(exist_ok=True)
DB_DIR.mkdir(exist_ok=True)

# API Keys (will be loaded from Streamlit secrets or .env)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Email Configuration
EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 587
EMAIL_USER = os.getenv("EMAIL_USER", "")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD", "")

# Database Configuration
DATABASE_URL = f"sqlite:///{DB_DIR}/salon_bookings.db"

# RAG Configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200
EMBEDDING_MODEL = "text-embedding-3-small"
LLM_MODEL = "gpt-3.5-turbo"
MAX_CONVERSATION_HISTORY = 20

# Booking Configuration
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

BUSINESS_HOURS = {
    "start": "09:00",
    "end": "20:00"
}