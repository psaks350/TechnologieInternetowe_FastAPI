from datetime import date, timedelta
from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Response, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, func
from sqlalchemy.exc import IntegrityError

# ZMIANA 1: Importujemy create_seed_data
from database import get_session, init_db, create_seed_data
from models import (
    Member, MemberCreate, MemberRead,
    Book, BookCreate, BookRead,
    Loan, LoanCreate, LoanRead
)

# ZMIANA 2: Dodajemy wywołanie seedowania do lifespan
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()           # Tworzy tabele
    create_seed_data()  # Wypełnia dane (jeśli pusto)
    yield

app = FastAPI(title="Library API", lifespan=lifespan)

# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# === BEZPIECZEŃSTWO ===
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    if request.method == "GET":
        response.headers["Cache-Control"] = "no-store"
    return response

# === Members ===

@app.get("/api/members", response_model=list[MemberRead])
def get_members(db: Session = Depends(get_session)):
    return db.exec(select(Member)).all()

@app.post("/api/members", response_model=MemberRead, status_code=201)
def create_member(data: MemberCreate, response: Response, db: Session = Depends(get_session)):
    try:
        member = Member.model_validate(data)
        db.add(member)
        db.commit()
        db.refresh(member)
        response.headers["Location"] = f"/api/members/{member.id}"
        return member
    except IntegrityError:
        db.rollback()
        raise HTTPException(409, detail="Email must be unique")

# === Books ===

@app.get("/api/books", response_model=list[BookRead])
def get_books(db: Session = Depends(get_session)):
    books = db.exec(select(Book)).all()
    results = []
    for book in books:
        active_loans = db.exec(
            select(func.count(Loan.id))
            .where(Loan.book_id == book.id, Loan.return_date == None)
        ).one()
        
        book_dict = book.model_dump()
        book_dict["available_copies"] = book.copies - active_loans
        results.append(BookRead.model_validate(book_dict))
    return results

@app.post("/api/books", response_model=BookRead, status_code=201)
def create_book(data: BookCreate, response: Response, db: Session = Depends(get_session)):
    book = Book.model_validate(data)
    db.add(book)
    db.commit()
    db.refresh(book)
    response.headers["Location"] = f"/api/books/{book.id}"
    return BookRead.model_validate(book, update={"available_copies": book.copies})

# === Loans ===

@app.get("/api/loans", response_model=list[LoanRead])
def get_loans(db: Session = Depends(get_session)):
    return db.exec(select(Loan)).all()

@app.post("/api/loans/borrow", response_model=LoanRead, status_code=201)
def borrow_book(data: LoanCreate, response: Response, db: Session = Depends(get_session)):
    book = db.get(Book, data.book_id)
    member = db.get(Member, data.member_id)
    if not book or not member:
        raise HTTPException(404, detail="Book or Member not found")

    active_loans = db.exec(
        select(func.count(Loan.id))
        .where(Loan.book_id == book.id, Loan.return_date == None)
    ).one()

    if active_loans >= book.copies:
        raise HTTPException(409, detail="No copies available")

    due_date = date.today() + timedelta(days=data.days)
    loan = Loan(member_id=data.member_id, book_id=data.book_id, due_date=due_date)
    
    db.add(loan)
    db.commit()
    db.refresh(loan)
    
    response.headers["Location"] = f"/api/loans/{loan.id}"
    return loan

@app.post("/api/loans/return", response_model=LoanRead)
def return_book_by_body(payload: dict, db: Session = Depends(get_session)):
    loan_id = payload.get("loan_id")
    loan = db.get(Loan, loan_id)

    if not loan:
        raise HTTPException(404, detail="Loan not found")
    if loan.return_date:
        raise HTTPException(409, detail="Loan already returned")

    loan.return_date = date.today()
    db.add(loan)
    db.commit()
    db.refresh(loan)
    return loan