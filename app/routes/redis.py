import json

import redis
from fastapi import APIRouter, Body, Depends, HTTPException

from config import REDIS_URL

router = APIRouter(prefix="/redis", tags=["redis"])


def get_redis() -> redis.Redis:
    return redis.from_url(REDIS_URL, decode_responses=True)


def _key_with_type(key: str, value_type: str) -> str:
    """Prefix key with type for namespacing."""
    return f"nosql:{value_type}:{key}"


@router.post("/string/{key}")
def set_string(key: str, value: str = Body(), redis_client=Depends(get_redis)):
    """Set a string value."""
    k = _key_with_type(key, "string")
    redis_client.set(k, value)
    return {"key": key, "value": value}


@router.get("/string/{key}")
def get_string(key: str, redis_client=Depends(get_redis)):
    """Get a string value."""
    k = _key_with_type(key, "string")
    value = redis_client.get(k)
    if value is None:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    return {"key": key, "value": value}


@router.post("/list/{key}/push")
def list_push(key: str, value: str = Body(), redis_client=Depends(get_redis)):
    """Push a value onto the list."""
    k = _key_with_type(key, "list")
    redis_client.rpush(k, json.dumps(value))
    length = redis_client.llen(k)
    return {"key": key, "value": value, "length": length, "type": "list"}


@router.post("/list/{key}/pop")
def list_pop(key: str, redis_client=Depends(get_redis)):
    """Pop a value from the end of the list."""
    k = _key_with_type(key, "list")
    raw = redis_client.rpop(k)
    if raw is None:
        raise HTTPException(
            status_code=404, detail=f"Key '{key}' not found or list is empty"
        )
    return {"key": key, "value": json.loads(raw), "type": "list"}


@router.get("/list/{key}")
def get_list(key: str, redis_client=Depends(get_redis)):
    """Get all values in the list."""
    k = _key_with_type(key, "list")
    raw_list = redis_client.lrange(k, 0, -1)
    if not raw_list:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    return {"key": key, "value": [json.loads(r) for r in raw_list], "type": "list"}


@router.post("/json/{key}")
def set_json(key: str, body: dict = Body(), redis_client=Depends(get_redis)):
    """Set a JSON object value."""
    k = _key_with_type(key, "json")
    redis_client.set(k, json.dumps(body))
    return {"key": key, "value": body, "type": "json"}


@router.get("/json/{key}")
def get_json(key: str, redis_client=Depends(get_redis)):
    """Get a JSON object value."""
    k = _key_with_type(key, "json")
    raw = redis_client.get(k)
    if raw is None:
        raise HTTPException(status_code=404, detail=f"Key '{key}' not found")
    try:
        value = json.loads(raw)
        if not isinstance(value, dict):
            raise ValueError("Not an object")
    except (json.JSONDecodeError, ValueError):
        raise HTTPException(
            status_code=400, detail=f"Value for '{key}' is not a valid JSON object"
        )
    return {"key": key, "value": value, "type": "json"}
