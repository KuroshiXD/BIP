from app.database import movies_collection
from bson import ObjectId
from typing import Optional, Dict, Any, List

class MovieRepository:
    @staticmethod
    async def get_all(filters: Dict[str, Any]) -> List[Dict]:
        cursor = movies_collection.find(filters)
        return await cursor.to_list(length=1000)

    @staticmethod
    async def count(filters: Dict[str, Any]) -> int:
        return await movies_collection.count_documents(filters)

    @staticmethod
    async def create(movie_data: Dict) -> str:
        result = await movies_collection.insert_one(movie_data)
        return str(result.inserted_id)

    @staticmethod
    async def get_by_id(movie_id: str) -> Optional[Dict]:
        try:
            obj_id = ObjectId(movie_id)
        except:
            return None
        return await movies_collection.find_one({"_id": obj_id})

    @staticmethod
    async def update(movie_id: str, update_data: Dict) -> bool:
        try:
            obj_id = ObjectId(movie_id)
        except:
            return False
        result = await movies_collection.update_one({"_id": obj_id}, {"$set": update_data})
        return result.modified_count > 0

    @staticmethod
    async def delete(movie_id: str) -> bool:
        try:
            obj_id = ObjectId(movie_id)
        except:
            return False
        result = await movies_collection.delete_one({"_id": obj_id})
        return result.deleted_count > 0