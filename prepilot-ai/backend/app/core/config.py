import os
from decimal import Decimal
from pathlib import Path
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = BASE_DIR.parent

# Environment
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Security check - warn about insecure defaults in production
if ENVIRONMENT == "production" and SECRET_KEY == "change-this-in-production":
    raise ValueError("SECRET_KEY must be set for production deployment")

# Server configuration
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
DEBUG = ENVIRONMENT == "development"

# Security
SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY or SECRET_KEY == "change-this-in-production":
    raise ValueError("SECRET_KEY environment variable must be set")

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# Gemini AI configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable must be set")

GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models")

# Database configuration
# Freebuff D1 binding used in production; falls back to DATABASE_URL env var
DATABASE_URL = os.getenv("DATABASE_URL", "")
if not DATABASE_URL:
    # No DATABASE_URL set - use SQLite file for development
    DATABASE_URL = "sqlite:///./dev.db"

# Frontend configuration
FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173")
ALLOWED_ORIGINS = [
    origin.strip() for origin in os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:8000").split(",")
]

# Application settings
UPLOAD_DIR = ROOT_DIR / "uploads"
MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB default
ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "pdf,docx").split(",")

# Ensure upload directory exists
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
