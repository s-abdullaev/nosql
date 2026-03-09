"""Load configuration from .env."""
from pathlib import Path

from dotenv import load_dotenv
import os

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "university")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
