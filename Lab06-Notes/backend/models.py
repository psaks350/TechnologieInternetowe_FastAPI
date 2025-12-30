from typing import List, Optional
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

# TABELA ŁĄCZĄCA
class NoteTag(SQLModel, table=True):
    note_id: int = Field(default=None, foreign_key="note.id", primary_key=True)
    tag_id: int = Field(default=None, foreign_key="tag.id", primary_key=True)

# MODELE BAZY DANYCH

class Tag(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True) 
    
    notes: List["Note"] = Relationship(back_populates="tags", link_model=NoteTag)

class Note(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    body: str
    created_at: datetime = Field(default_factory=datetime.now)
    
    tags: List["Tag"] = Relationship(back_populates="notes", link_model=NoteTag)

# SCHEMATY API

class NoteCreate(SQLModel):
    title: str
    body: str

# To zwracamy frontendowi (zawiera listę tagów jako obiekty)
class NoteRead(SQLModel):
    id: int
    title: str
    body: str
    created_at: datetime
    tags: List[Tag] = []

# Payload do dodawania tagów
class TagList(SQLModel):
    tags: List[str] # np. ["pilne", "dom"]