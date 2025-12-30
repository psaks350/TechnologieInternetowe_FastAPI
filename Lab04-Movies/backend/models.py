from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship


class Movie(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    year: int
    
    ratings: List["Rating"] = Relationship(back_populates="movie")

class Rating(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    movie_id: int = Field(foreign_key="movie.id")
    score: int = Field(ge=1, le=5)
    
    movie: Movie = Relationship(back_populates="ratings")


class MovieCreate(SQLModel):
    title: str
    year: int

class MovieRead(SQLModel):
    id: int
    title: str
    year: int
    avg_score: float = 0.0
    votes: int = 0
    
class RatingCreate(SQLModel):
    movie_id: int
    score: int = Field(ge=1, le=5)