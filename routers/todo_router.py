from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import TodoCreate, Todo, TodoUpdate
import models
from dependencies import get_db_session
from auth import get_current_user

router = APIRouter(prefix="/todos", tags=["Todos"])  # Prefix và tags cho docs

@router.post("/", response_model=Todo)
async def create_todo(todo: TodoCreate, db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    db_todo = models.TodoDB(**todo.dict(), owner_id=user.id)  # Liên kết owner
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Tương tự cho get, update, delete (chuyển async def nếu DB async)
# Ví dụ GET async giả lập
@router.get("/", response_model=list[Todo])
async def get_todos(db: Session = Depends(get_db_session), user=Depends(get_current_user)):
    return db.query(models.TodoDB).filter(models.TodoDB.owner_id == user.id).all()