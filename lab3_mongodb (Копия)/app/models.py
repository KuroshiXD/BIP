from pydantic import BaseModel, Field
from typing import List, Optional
from bson import ObjectId
from enum import Enum

class StatusEnum(str, Enum):
    watched = "watched"
    not_watched = "not_watched"

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class MovieBase(BaseModel):
    title: str
    studio: str
    year: int
    rating: float = Field(ge=0, le=10)
    status: StatusEnum
    actors: List[str]
    director: str
    genre: str

class MovieCreate(MovieBase):
    pass

class MovieUpdate(BaseModel):
    title: Optional[str] = None
    studio: Optional[str] = None
    year: Optional[int] = None
    rating: Optional[float] = Field(None, ge=0, le=10)
    status: Optional[StatusEnum] = None
    actors: Optional[List[str]] = None
    director: Optional[str] = None
    genre: Optional[str] = None

class MovieInDB(MovieBase):
    id: str = Field(alias="_id")

    class Config:
        populate_by_name = True        # вместо allow_population_by_field_name
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}