from typing import Optional, List
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

class Post(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    body: str
    created_at: datetime = Field(default_factory=datetime.now)

    comments: List["Comment"] = Relationship(back_populates="post")

class Comment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    post_id: int = Field(foreign_key="post.id")
    author: str
    body: str
    created_at: datetime = Field(default_factory=datetime.now)
    approved: bool = Field(default=False)
    
    post: Optional[Post] = Relationship(back_populates="comments")

# DTO (Data Transfer Objects)

class PostCreate(SQLModel):
    title: str
    body: str

class CommentCreate(SQLModel):
    author: str
    body: str