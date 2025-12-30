from typing import List, Optional
from sqlmodel import Field, SQLModel, Relationship

# MODELE BAZY DANYCH

class Column(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    ord: int 
    
    tasks: List["Task"] = Relationship(back_populates="column")

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    ord: int
    
    col_id: int = Field(foreign_key="column.id")
    column: Column = Relationship(back_populates="tasks")

# SCHEMATY API

class TaskCreate(SQLModel):
    title: str
    col_id: int

class TaskMove(SQLModel):
    col_id: int
    ord: int

class BoardData(SQLModel):
    cols: List[Column]
    tasks: List[Task]