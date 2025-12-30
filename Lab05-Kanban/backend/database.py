from sqlmodel import SQLModel, create_engine, Session, select

sqlite_file_name = "kanban.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def create_seed_data():
    from models import Column, Task
    
    with Session(engine) as session:
        if session.exec(select(Column)).first():
            return 
        print("Baza pusta. Dodaję dane startowe (Kolumny + Zadania)")

        c1 = Column(name="Todo", ord=0)
        c2 = Column(name="In Progress", ord=1)
        c3 = Column(name="Done", ord=2)
        
        session.add(c1)
        session.add(c2)
        session.add(c3)
        session.commit()

        session.refresh(c1)
        session.refresh(c2)
        session.refresh(c3)

        t1 = Task(title="Napisać sprawozdanie", col_id=c1.id, ord=0)
        t2 = Task(title="Kupić kawę", col_id=c1.id, ord=1)
        t3 = Task(title="Opłacić rachunki", col_id=c1.id, ord=2)

        t4 = Task(title="Implementacja Lab05", col_id=c2.id, ord=0)

        t5 = Task(title="Instalacja Dockera", col_id=c3.id, ord=0)
        t6 = Task(title="Konfiguracja Git", col_id=c3.id, ord=1)

        session.add(t1); session.add(t2); session.add(t3)
        session.add(t4); session.add(t5); session.add(t6)
        
        session.commit()
        print("Dane startowe dodane pomyślnie")

def get_session():
    with Session(engine) as session:
        yield session