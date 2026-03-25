from datetime import datetime
from typing import Optional
from .redis_service import RedisService
from ..data.note_repository import NoteRepository

class NoteService:
    def __init__(self, note_repository: NoteRepository, redis_service: RedisService):
        self.repo = note_repository
        self.redis = redis_service

    def create_note(self, title: str, content: str):
        note = self.repo.create(title, content)
        # Кэшируем содержимое
        self.redis.cache_note(note.id, content)
        # Сохраняем метаинформацию в Redis
        self.redis.set_note_meta(note.id, "created_at", note.created_at.isoformat())
        self.redis.set_note_meta(note.id, "updated_at", note.updated_at.isoformat())
        return note

    def get_note(self, note_id: int):
        # Пытаемся получить содержимое из кэша
        cached_content = self.redis.get_cached_note(note_id)
        note = self.repo.get(note_id)
        if note is None:
            return None
        # Обновляем время последнего чтения в Redis
        self.redis.set_note_meta(note_id, "last_read", datetime.utcnow().isoformat())
        # Если кэш отсутствует, обновляем его
        if cached_content is None:
            self.redis.cache_note(note_id, note.content)
            content = note.content
        else:
            content = cached_content
        return {
            "id": note.id,
            "title": note.title,
            "content": content,
            "created_at": note.created_at,
            "updated_at": note.updated_at
        }

    def update_note(self, note_id: int, title: Optional[str] = None, content: Optional[str] = None):
        note = self.repo.update(note_id, title, content)
        if note:
            if content is not None:
                self.redis.cache_note(note_id, content)
            self.redis.set_note_meta(note_id, "updated_at", note.updated_at.isoformat())
        return note

    def delete_note(self, note_id: int):
        self.repo.delete(note_id)
        self.redis.delete_cached_note(note_id)
        self.redis.delete_note_meta(note_id)

    def get_note_meta(self, note_id: int):
        return self.redis.get_note_meta(note_id)

    def get_all_notes(self):
        return self.repo.list_all()