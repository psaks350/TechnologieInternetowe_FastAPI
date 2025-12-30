from contextlib import asynccontextmanager
from typing import List, Optional

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, col
from database import init_db, get_session, create_seed_data

from models import Note, NoteCreate, NoteRead, Tag, TagList, NoteTag

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    create_seed_data()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === API ===

@app.get("/api/notes", response_model=List[NoteRead])
def get_notes(
    q: Optional[str] = None, 
    db: Session = Depends(get_session)
):
    statement = select(Note)
    
    if q:
        statement = statement.where(
            col(Note.title).contains(q) | col(Note.body).contains(q)
        )
    
    statement = statement.order_by(Note.created_at.desc())
    return db.exec(statement).all()

@app.post("/api/notes", response_model=NoteRead, status_code=201)
def create_note(data: NoteCreate, db: Session = Depends(get_session)):
    note = Note.model_validate(data)
    db.add(note)
    db.commit()
    db.refresh(note)
    return note

@app.get("/api/tags", response_model=List[Tag])
def get_tags(db: Session = Depends(get_session)):
    return db.exec(select(Tag)).all()

@app.post("/api/notes/{note_id}/tags")
def add_tags_to_note(note_id: int, payload: TagList, db: Session = Depends(get_session)):
    note = db.get(Note, note_id)
    if not note:
        raise HTTPException(404, "Note not found")

    for tag_name in payload.tags:
        clean_name = tag_name.strip().lower() # Normalizacja
        if not clean_name:
            continue

        tag = db.exec(select(Tag).where(Tag.name == clean_name)).first()
        
        if not tag:
            tag = Tag(name=clean_name)
            db.add(tag)
            db.commit()
            db.refresh(tag)
        
        if tag not in note.tags:
            note.tags.append(tag)
    
    db.add(note)
    db.commit()
    db.refresh(note)
    
    return {"status": "tags_updated", "current_tags": note.tags}