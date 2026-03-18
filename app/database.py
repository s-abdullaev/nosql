from neo4j import GraphDatabase
from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from config import MONGO_URI, MONGO_DB_NAME, POSTGRES_URL, NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

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


# ── Neo4j ─────────────────────────────────────────────────────────────────────

neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))


def get_neo4j():
    with neo4j_driver.session() as session:
        yield session
