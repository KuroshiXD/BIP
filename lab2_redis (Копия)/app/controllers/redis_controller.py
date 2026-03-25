from fastapi import APIRouter, Depends, HTTPException
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from typing import Optional
from ..containers import Container
from ..services.redis_service import RedisService

router = APIRouter()

class StringSetRequest(BaseModel):
    key: str
    value: str
    ttl: Optional[int] = None

class ListPushRequest(BaseModel):
    key: str
    value: str
    left: bool = True

class ListRangeRequest(BaseModel):
    key: str
    start: int
    end: int

class HashSetRequest(BaseModel):
    key: str
    field: str
    value: str

class ExpireRequest(BaseModel):
    key: str
    ttl: int

@router.post("/string")
@inject
def set_string(req: StringSetRequest, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    redis_service.set_string(req.key, req.value, req.ttl)
    return {"message": "OK"}

@router.get("/string/{key}")
@inject
def get_string(key: str, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    value = redis_service.get_string(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found")
    return {"value": value}

@router.delete("/{key}")
@inject
def delete_key(key: str, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    redis_service.delete_key(key)
    return {"message": "Deleted"}

@router.post("/incr/{key}")
@inject
def increment(key: str, amount: int = 1, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    new_value = redis_service.increment(key, amount)
    return {"new_value": new_value}

@router.post("/list/push")
@inject
def list_push(req: ListPushRequest, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    redis_service.list_push(req.key, req.value, req.left)
    return {"message": "OK"}

@router.post("/list/range")
@inject
def list_range(req: ListRangeRequest, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    values = redis_service.list_range(req.key, req.start, req.end)
    return {"values": values}

@router.post("/list/pop")
@inject
def list_pop(key: str, left: bool = True, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    value = redis_service.list_pop(key, left)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found or list empty")
    return {"value": value}

@router.post("/hash/set")
@inject
def hash_set(req: HashSetRequest, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    redis_service.hash_set(req.key, req.field, req.value)
    return {"message": "OK"}

@router.get("/hash/{key}/{field}")
@inject
def hash_get(key: str, field: str, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    value = redis_service.hash_get(key, field)
    if value is None:
        raise HTTPException(status_code=404, detail="Field not found")
    return {"value": value}

@router.get("/hash/{key}")
@inject
def hash_get_all(key: str, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    data = redis_service.hash_get_all(key)
    if not data:
        raise HTTPException(status_code=404, detail="Key not found")
    return data

@router.delete("/hash/{key}/{field}")
@inject
def hash_delete(key: str, field: str, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    redis_service.hash_delete(key, field)
    return {"message": "Deleted"}

@router.post("/expire")
@inject
def expire(req: ExpireRequest, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    redis_service.expire(req.key, req.ttl)
    return {"message": "OK"}

@router.get("/ttl/{key}")
@inject
def ttl(key: str, redis_service: RedisService = Depends(Provide[Container.redis_service])):
    ttl = redis_service.ttl(key)
    return {"ttl": ttl}