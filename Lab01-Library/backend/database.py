import os
from sqlmodel import SQLModel, create_engine, Session, select

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///library.db")
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)

# SEEDOWANIE DANYCH
def create_seed_data():

    from models import Book, Member
    
    with Session(engine) as session:
        if session.exec(select(Book)).first():
            return 

        print("---- SEEDOWANIE: Tworzenie danych startowych... ----")

        members = [
            Member(name="Jan Kowalski", email="jan.kowalski@example.com"),
            Member(name="Anna Nowak", email="anna.nowak@example.com"),
            Member(name="Piotr Wiśniewski", email="piotr.wis@example.com"),
            Member(name="Maria Zielińska", email="maria.zielinska@example.com"),
        ]
        
        for member in members:
            session.add(member)

        books = [
            Book(title="Wiedźmin: Ostatnie Życzenie", author="Andrzej Sapkowski", copies=5),
            Book(title="Clean Code", author="Robert C. Martin", copies=2),
            Book(title="Pan Tadeusz", author="Adam Mickiewicz", copies=10),
            Book(title="Harry Potter i Kamień Filozoficzny", author="J.K. Rowling", copies=3),
            Book(title="Diuna", author="Frank Herbert", copies=4),
        ]

        for book in books:
            session.add(book)

        session.commit()
        print("SEEDOWANIE: Dane startowe zostały utworzone.")