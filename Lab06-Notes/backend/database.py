from sqlmodel import SQLModel, create_engine, Session, select
from datetime import datetime, timedelta

sqlite_file_name = "notes.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def create_seed_data():
    from models import Note, Tag

    with Session(engine) as session:
        if session.exec(select(Note)).first():
            return

        print("Baza pusta. Dodaję dane startowe (Notatki + Tagi)")

        t_work = Tag(name="praca")
        t_home = Tag(name="dom")
        t_urgent = Tag(name="pilne")
        t_idea = Tag(name="pomysł")

        n1 = Note(
            title="Projekt Lab06", 
            body="Dokończyć implementację relacji wiele-do-wielu i przetestować API.",
            created_at=datetime.now()
        )
        n1.tags = [t_work, t_urgent]

        n2 = Note(
            title="Lista zakupów", 
            body="Mleko, chleb, kawa, owoce.",
            created_at=datetime.now() - timedelta(days=1) # Wczorajsza
        )
        n2.tags = [t_home]

        n3 = Note(
            title="Pomysł na aplikację", 
            body="Aplikacja do śledzenia nawyków z grywalizacją.",
            created_at=datetime.now() - timedelta(days=2) # Przedwczorajsza
        )
        n3.tags = [t_idea, t_work]
        
        n4 = Note(
            title="Spotkanie z zespołem",
            body="Omówienie sprintu i podział zadań na kolejny tydzień.",
            created_at=datetime.now() - timedelta(hours=5)
        )
        n4.tags = [t_work]

        session.add(n1)
        session.add(n2)
        session.add(n3)
        session.add(n4)
        
        session.commit()
        print("Dane startowe dodane pomyślnie!")

def get_session():
    with Session(engine) as session:
        yield session