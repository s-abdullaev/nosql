from fastapi import FastAPI

from app.database import get_db

app = FastAPI(title="NoSQL Demo", version="0.1.0")


@app.get("/")
def root():
    return {"message": "Hello from nosql!"}


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/departments")
def list_departments():
    """List all departments from MongoDB."""
    db = get_db()
    departments = list(db.department.find({}, {"_id": 0}))
    return {"departments": departments}
