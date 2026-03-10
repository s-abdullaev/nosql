from fastapi import FastAPI

from app.routes.mongodb import router as mongodb_router
from app.routes.postgis import router as postgis_router
from app.routes.redis import router as redis_router

app = FastAPI(title="NoSQL Demo", version="0.1.0")

app.include_router(mongodb_router)
app.include_router(redis_router)
app.include_router(postgis_router)


@app.get("/")
def root():
    return {"message": "Hello from nosql!"}


@app.get("/health")
def health():
    return {"status": "ok"}
