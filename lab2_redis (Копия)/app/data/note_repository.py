from sqlalchemy.orm import Session
from .models import NoteModel
from datetime import datetime

class NoteRepository:
    def __init__(self, session_factory):
        self.session_factory = session_factory

    def _get_session(self):
        return next(self.session_factory())

    def create(self, title: str, content: str) -> NoteModel:
        db = self._get_session()
        note = NoteModel(title=title, content=content)
        db.add(note)
        db.commit()
        db.refresh(note)
        db.close()
        return note

    def get(self, note_id: int) -> NoteModel:
        db = self._get_session()
        note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
        db.close()
        return note

    def update(self, note_id: int, title: str = None, content: str = None) -> NoteModel:
        db = self._get_session()
        note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
        if note:
            if title is not None:
                note.title = title
            if content is not None:
                note.content = content
            note.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(note)
        db.close()
        return note

    def delete(self, note_id: int):
        db = self._get_session()
        note = db.query(NoteModel).filter(NoteModel.id == note_id).first()
        if note:
            db.delete(note)
            db.commit()
        db.close()

    def list_all(self):
        db = self._get_session()
        notes = db.query(NoteModel).all()
        db.close()
        return notes