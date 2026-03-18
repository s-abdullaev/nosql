"""Load configuration from .env."""
from pathlib import Path

from dotenv import load_dotenv
import os

# Load .env from project root
load_dotenv(Path(__file__).resolve().parent / ".env")

MONGO_URI = os.getenv("MONGO_URI", "mongodb://admin:password@localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "university")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

POSTGRES_URL = os.getenv(
    "POSTGRES_URL", "postgresql://postgres:postgres@localhost:5432/geodemo"
)

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
