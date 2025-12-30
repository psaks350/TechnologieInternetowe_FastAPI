from sqlmodel import SQLModel, create_engine, Session, select

sqlite_file_name = "movies.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

def init_db():
    SQLModel.metadata.create_all(engine)

# SEEDING DANYCH
def create_seed_data():

    from models import Movie, Rating 

    with Session(engine) as session:
        if session.exec(select(Movie)).first():
            return

        print("Baza pusta. Dodaję dane startowe")

        m1 = Movie(title="The Matrix", year=1999)
        m2 = Movie(title="Shrek", year=2001)
        m3 = Movie(title="Inception", year=2010)
        m4 = Movie(title="The Room", year=2003)

        session.add(m1)
        session.add(m2)
        session.add(m3)
        session.add(m4)
        session.commit()

        session.refresh(m1)
        session.refresh(m2)
        session.refresh(m3)
        session.refresh(m4)

        session.add(Rating(movie_id=m1.id, score=5))
        session.add(Rating(movie_id=m1.id, score=5))
        session.add(Rating(movie_id=m1.id, score=4))

        session.add(Rating(movie_id=m2.id, score=5))
        session.add(Rating(movie_id=m2.id, score=5))
        session.add(Rating(movie_id=m2.id, score=5))

        session.add(Rating(movie_id=m3.id, score=4))
        session.add(Rating(movie_id=m3.id, score=3))

        session.add(Rating(movie_id=m4.id, score=1))
        session.add(Rating(movie_id=m4.id, score=2))

        session.commit()
        print("Dane startowe dodane!")

def get_session():
    with Session(engine) as session:
        yield session