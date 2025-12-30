from contextlib import asynccontextmanager
from typing import List

from fastapi import FastAPI, Depends, HTTPException, Response, status, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import get_session, init_db, create_seed_data

from models import Movie, MovieCreate, MovieRead, Rating, RatingCreate

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    create_seed_data()
    yield

app = FastAPI(title="Movie Ranking API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    return response

@app.get("/api/movies", response_model=List[MovieRead])
def get_movies(db: Session = Depends(get_session)):
    movies = db.exec(select(Movie)).all()
    results = []

    for movie in movies:
        ratings_count = len(movie.ratings)
        
        if ratings_count > 0:
            total_score = sum(r.score for r in movie.ratings)
            avg = total_score / ratings_count
        else:
            avg = 0.0

        movie_dto = MovieRead(
            id=movie.id,
            title=movie.title,
            year=movie.year,
            avg_score=round(avg, 2),
            votes=ratings_count
        )
        results.append(movie_dto)

    results.sort(key=lambda x: x.avg_score, reverse=True)
    
    return results

@app.post("/api/movies", response_model=MovieRead, status_code=201)
def create_movie(data: MovieCreate, response: Response, db: Session = Depends(get_session)):
    movie = Movie.model_validate(data)
    db.add(movie)
    db.commit()
    db.refresh(movie)
    
    response.headers["Location"] = f"/api/movies/{movie.id}"
    
    return MovieRead(
        id=movie.id, 
        title=movie.title, 
        year=movie.year, 
        avg_score=0.0, 
        votes=0
    )

@app.post("/api/ratings", status_code=201)
def add_rating(data: RatingCreate, db: Session = Depends(get_session)):
    movie = db.get(Movie, data.movie_id)
    if not movie:
        raise HTTPException(404, detail="Film nie istnieje")

    rating = Rating.model_validate(data)
    db.add(rating)
    db.commit()
    
    return {"message": "Ocena dodana"}