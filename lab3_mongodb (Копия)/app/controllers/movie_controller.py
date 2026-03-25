from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Optional
from app.models import MovieCreate, MovieUpdate, MovieInDB
from app.repositories.movie_repository import MovieRepository
from bson import ObjectId

router = APIRouter(prefix="/movies", tags=["movies"])

def build_filters(
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    rating_min: Optional[float] = None,
    actor: Optional[str] = None,
    director: Optional[str] = None,
    genre: Optional[str] = None,
    status: Optional[str] = None,
) -> dict:
    filters = {}
    if year_from is not None or year_to is not None:
        year_filter = {}
        if year_from is not None:
            year_filter["$gte"] = year_from
        if year_to is not None:
            year_filter["$lte"] = year_to
        filters["year"] = year_filter
    if rating_min is not None:
        filters["rating"] = {"$gte": rating_min}
    if actor is not None:
        filters["actors"] = {"$in": [actor]}
    if director is not None:
        filters["director"] = director
    if genre is not None:
        filters["genre"] = genre
    if status is not None:
        filters["status"] = status
    return filters

@router.get("/", response_model=List[MovieInDB])
async def get_movies(
    year_from: Optional[int] = Query(None, description="Минимальный год"),
    year_to: Optional[int] = Query(None, description="Максимальный год"),
    rating_min: Optional[float] = Query(None, description="Минимальная оценка"),
    actor: Optional[str] = Query(None, description="Актёр"),
    director: Optional[str] = Query(None, description="Режиссёр"),
    genre: Optional[str] = Query(None, description="Жанр"),
    status: Optional[str] = Query(None, description="Статус (watched/not watched)"),
):
    filters = build_filters(year_from, year_to, rating_min, actor, director, genre, status)
    movies = await MovieRepository.get_all(filters)
    for movie in movies:
        movie["_id"] = str(movie["_id"])
    return movies

@router.get("/count", response_model=int)
async def count_movies(
    year_from: Optional[int] = Query(None, description="Минимальный год"),
    year_to: Optional[int] = Query(None, description="Максимальный год"),
    rating_min: Optional[float] = Query(None, description="Минимальная оценка"),
    actor: Optional[str] = Query(None, description="Актёр"),
    director: Optional[str] = Query(None, description="Режиссёр"),
    genre: Optional[str] = Query(None, description="Жанр"),
    status: Optional[str] = Query(None, description="Статус (watched/not watched)"),
):
    filters = build_filters(year_from, year_to, rating_min, actor, director, genre, status)
    count = await MovieRepository.count(filters)
    return count

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_movie(movie: MovieCreate):
    movie_data = movie.dict()
    inserted_id = await MovieRepository.create(movie_data)
    return {"id": inserted_id}

@router.get("/{movie_id}", response_model=MovieInDB)
async def get_movie(movie_id: str):
    movie = await MovieRepository.get_by_id(movie_id)
    if movie is None:
        raise HTTPException(status_code=404, detail="Movie not found")
    movie["_id"] = str(movie["_id"])
    return movie

@router.put("/{movie_id}", response_model=dict)
async def update_movie(movie_id: str, movie_update: MovieUpdate):
    update_data = {k: v for k, v in movie_update.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No fields to update")
    updated = await MovieRepository.update(movie_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie updated successfully"}

@router.delete("/{movie_id}", response_model=dict)
async def delete_movie(movie_id: str):
    deleted = await MovieRepository.delete(movie_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Movie not found")
    return {"message": "Movie deleted successfully"}