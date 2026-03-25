from motor.motor_asyncio import AsyncIOMotorClient
import os

MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "movie_db")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]
movies_collection = database.get_collection("movies")