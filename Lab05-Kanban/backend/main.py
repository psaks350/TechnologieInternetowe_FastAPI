from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlmodel import Session, select, func
from database import init_db, create_seed_data, get_session
from models import Column, Task, TaskCreate, TaskMove, BoardData

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

@app.get("/api/board", response_model=BoardData)
def get_board(db: Session = Depends(get_session)):

    cols = db.exec(select(Column).order_by(Column.ord)).all()
    tasks = db.exec(select(Task).order_by(Task.ord)).all()
    
    return BoardData(cols=cols, tasks=tasks)

@app.post("/api/tasks", status_code=201)
def create_task(data: TaskCreate, db: Session = Depends(get_session)):

    max_ord = db.exec(
        select(func.max(Task.ord)).where(Task.col_id == data.col_id)
    ).one()
    
    new_ord = (max_ord if max_ord is not None else -1) + 1

    task = Task(title=data.title, col_id=data.col_id, ord=new_ord)
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@app.post("/api/tasks/{task_id}/move")
def move_task(task_id: int, move_data: TaskMove, db: Session = Depends(get_session)):
    task = db.get(Task, task_id)
    if not task:
        raise HTTPException(404, "Zadanie nie istnieje")
    
    task.col_id = move_data.col_id
    task.ord = move_data.ord
    
    db.add(task)
    db.commit()
    return {"status": "moved"}