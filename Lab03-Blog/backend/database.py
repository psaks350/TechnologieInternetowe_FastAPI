from sqlmodel import SQLModel, create_engine, Session, select
from datetime import datetime

sqlite_file_name = "blog.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

def create_seed_data():
    from models import Post, Comment
    
    with Session(engine) as session:
        if session.exec(select(Post)).first():
            return

        print("Seedowanie danych...")

        p1 = Post(title="Witamy na Blogu", body="To jest pierwszy post testowy.")
        session.add(p1)
        session.commit()
        session.refresh(p1)

        c1 = Comment(
            post_id=p1.id, 
            author="Janusz", 
            body="Super wpis!", 
            approved=True
        )
        
        c2 = Comment(
            post_id=p1.id, 
            author="Spammer", 
            body="Kup tanie okulary...", 
            approved=False
        )

        session.add(c1)
        session.add(c2)
        session.commit()
        print("Dane startowe dodane.")

def get_session():
    with Session(engine) as session:
        yield session