from sqlalchemy.future import select
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from schemas import TodoCreate, Todo, TodoUpdate
import models
from dependencies import get_db_session
from auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(prefix="/todos", tags=["Todos"])  # Prefix và tags cho docs

@router.post("/", response_model=Todo)
async def create_todo(todo: TodoCreate, db: AsyncSession = Depends(get_db), current_user: models.UserDB = Depends(get_current_user)):
    db_todo = models.TodoDB(**todo.model_dump(), owner_id=current_user.id)  # Liên kết owner
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo

# Tương tự cho get, update, delete (chuyển async def nếu DB async)
# Ví dụ GET async giả lập
@router.get("/", response_model=list[Todo])
async def get_todos(db: AsyncSession = Depends(get_db), current_user: models.UserDB = Depends(get_current_user)):
    result = await db.execute(select(models.TodoDB).filter(models.TodoDB.owner_id == current_user.id))

    return result.scalars().all()

# Tương tự async cho get_by_id, update, delete (sử dụng await db.execute, filter owner_id)
