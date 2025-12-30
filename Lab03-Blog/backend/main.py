import time
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select
from database import init_db, create_seed_data, get_session
from models import Post, Comment, PostCreate, CommentCreate

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    create_seed_data()
    yield

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
last_comment_times = {}

BAD_WORDS = ["spam", "casino", "viagra", "krypto", "tanie leki"]

# POSTY

@app.get("/api/posts", response_model=List[Post])
def get_posts(db: Session = Depends(get_session)):
    return db.exec(select(Post).order_by(Post.created_at.desc())).all()

@app.post("/api/posts", status_code=201)
def create_post(data: PostCreate, db: Session = Depends(get_session)):
    post = Post.model_validate(data)
    db.add(post)
    db.commit()
    return post

# KOMENTARZE (Dla czytelników)

@app.get("/api/posts/{post_id}/comments", response_model=List[Comment])
def get_post_comments(post_id: int, db: Session = Depends(get_session)):
    statement = select(Comment).where(
        Comment.post_id == post_id, 
        Comment.approved == True
    )
    return db.exec(statement).all()

# Dodaj komentarz (Zawsze approved=False)
@app.post("/api/posts/{post_id}/comments", status_code=201)
def add_comment(
    post_id: int, 
    data: CommentCreate, 
    request: Request,
    db: Session = Depends(get_session)
):
    content_lower = data.body.lower()
    for word in BAD_WORDS:
        if word in content_lower:
            raise HTTPException(status_code=400, detail=f"Komentarz zawiera niedozwolone słowo: {word}")

    client_ip = request.client.host
    current_time = time.time()
    
    if client_ip in last_comment_times:
        last_time = last_comment_times[client_ip]
        if current_time - last_time < 15:
            wait_time = int(15 - (current_time - last_time))
            raise HTTPException(status_code=429, detail=f"Możesz dodać kolejny komentarz za {wait_time} s.")

    last_comment_times[client_ip] = current_time

    comment = Comment(
        post_id=post_id,
        author=data.author,
        body=data.body,
        approved=False
    )
    db.add(comment)
    db.commit()
    return {"status": "pending_approval"}

# MODERACJA (Dla admina)

@app.get("/api/comments/pending", response_model=List[Comment])
def get_pending_comments(db: Session = Depends(get_session)):
    return db.exec(select(Comment).where(Comment.approved == False)).all()

@app.post("/api/comments/{comment_id}/approve")
def approve_comment(comment_id: int, db: Session = Depends(get_session)):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(404, "Komentarz nie istnieje")
    
    comment.approved = True
    db.add(comment)
    db.commit()
    return {"status": "approved"}

@app.delete("/api/comments/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_session)):
    comment = db.get(Comment, comment_id)
    if not comment:
        raise HTTPException(404, "Komentarz nie istnieje")
    
    db.delete(comment)
    db.commit()
    return {"status": "deleted"}