from fastapi import FastAPI
from app.controllers.movie_controller import router as movie_router

app = FastAPI(title="Movie API", description="Backend for movie tracking using MongoDB")

app.include_router(movie_router)

@app.get("/")
async def root():
    return {"message": "Movie API is running"}