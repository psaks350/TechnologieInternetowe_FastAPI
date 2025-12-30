from datetime import date, timedelta
from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship

# === DB Models ===

class Member(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    email: str = Field(unique=True, index=True)
    
    loans: List["Loan"] = Relationship(back_populates="member")

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str = Field(index=True)
    copies: int = Field(default=1, gt=0)
    
    loans: List["Loan"] = Relationship(back_populates="book")

class Loan(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    member_id: int = Field(foreign_key="member.id")
    book_id: int = Field(foreign_key="book.id")
    
    loan_date: date = Field(default_factory=date.today)
    due_date: date = Field(default_factory=lambda: date.today() + timedelta(days=14))
    return_date: Optional[date] = None

    member: Member = Relationship(back_populates="loans")
    book: Book = Relationship(back_populates="loans")

# === API Schemas ===

class MemberCreate(SQLModel):
    name: str
    email: str

class MemberRead(MemberCreate):
    id: int

class BookCreate(SQLModel):
    title: str
    author: str
    copies: int = 1

class BookRead(BookCreate):
    id: int
    available_copies: int | None = None

class LoanCreate(SQLModel):
    member_id: int
    book_id: int
    days: int = 14

class LoanRead(SQLModel):
    id: int
    loan_date: date
    due_date: date
    return_date: Optional[date]
    book: BookRead
    member: MemberRead