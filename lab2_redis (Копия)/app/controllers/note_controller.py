from fastapi import APIRouter, HTTPException, Depends
from dependency_injector.wiring import inject, Provide
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from ..containers import Container
from ..services.note_service import NoteService

router = APIRouter()

class NoteCreate(BaseModel):
    title: str
    content: str

class NoteUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class NoteResponse(BaseModel):
    id: int
    title: str
    content: str
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True

class NoteMetaResponse(BaseModel):
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_read: Optional[str] = None

@router.post("/", response_model=NoteResponse)
@inject
def create_note(note: NoteCreate, note_service: NoteService = Depends(Provide[Container.note_service])):
    note_obj = note_service.create_note(note.title, note.content)
    return note_obj

@router.get("/{note_id}", response_model=NoteResponse)
@inject
def get_note(note_id: int, note_service: NoteService = Depends(Provide[Container.note_service])):
    note = note_service.get_note(note_id)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.put("/{note_id}", response_model=NoteResponse)
@inject
def update_note(note_id: int, note_update: NoteUpdate, note_service: NoteService = Depends(Provide[Container.note_service])):
    note = note_service.update_note(note_id, note_update.title, note_update.content)
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.delete("/{note_id}")
@inject
def delete_note(note_id: int, note_service: NoteService = Depends(Provide[Container.note_service])):
    note_service.delete_note(note_id)
    return {"message": "Note deleted"}

@router.get("/{note_id}/meta", response_model=NoteMetaResponse)
@inject
def get_note_meta(note_id: int, note_service: NoteService = Depends(Provide[Container.note_service])):
    meta = note_service.get_note_meta(note_id)
    if not meta:
        raise HTTPException(status_code=404, detail="Meta not found")
    return NoteMetaResponse(
        created_at=meta.get("created_at"),
        updated_at=meta.get("updated_at"),
        last_read=meta.get("last_read")
    )

@router.get("/", response_model=list[NoteResponse])
@inject
def list_notes(note_service: NoteService = Depends(Provide[Container.note_service])):
    notes = note_service.get_all_notes()
    return notes