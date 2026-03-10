from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import MONGO_URI, MONGO_DB_NAME, POSTGRES_URL

# ── MongoDB ──────────────────────────────────────────────────────────────────


def get_client() -> MongoClient:
    return MongoClient(MONGO_URI)


def get_db():
    return get_client()[MONGO_DB_NAME]


# ── PostGIS (PostgreSQL) ─────────────────────────────────────────────────────

engine = create_engine(POSTGRES_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass


def get_postgis_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
