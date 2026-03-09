from fastapi import FastAPI

from app.routes.mongodb import router as mongodb_router

app = FastAPI(title="NoSQL Demo", version="0.1.0")

app.include_router(mongodb_router)


@app.get("/")
def root():
    return {"message": "Hello from nosql!"}


@app.get("/health")
def health():
    return {"status": "ok"}
