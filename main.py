import asyncio
from datetime import timedelta
import logging
from fastapi import FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Dict, List, Optional
from pydantic import Field

from fastapi.params import Depends
from pydantic import BaseModel
from auth import authenticate_user, create_access_token, get_current_user, get_current_user, get_password_hash
import auth
from database import engine, get_db, Base
from fastapi.middleware.cors import CORSMiddleware

import models
from routers.todo_router import router as todo_router
from routers.auth_router import router as auth_router
from schemas import Todo, TodoCreate, TodoUpdate, TodoUpdate, Token, User, UserCreate  # Để type hint cho data echo
from sqlalchemy.orm import Session
from dependencies import get_db_session, check_admin_role, pagination_params
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)  # Logging setup

app = FastAPI(
    title="My First Backend API",  # Tiêu đề hiển thị trong docs
    description="API cơ bản để học FastAPI - Ngày 1",
    version="1.0.0"
)

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# CORS middleware (best practice cho frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Thay bằng domain thực tế
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(todo_router)
app.include_router(auth_router)

# Rate limiting đơn giản (middleware)
@app.middleware("http")
async def rate_limit_middleware(request, call_next):
    # Giả lập: Log và check (thực tế dùng slowapi)
    logging.info(f"Request: {request.url}")
    response = await call_next(request)
    return response

# Async route ví dụ
@app.get("/async-test")
async def async_test():
    await asyncio.sleep(1)  # Giả lập async I/O
    return {"message": "Async working"}

@app.get("/")
def home():
    return {"message": "Hello World"}

# Tạo table tự động khi khởi động
models.Base.metadata.create_all(bind=engine)

todos: List[models.TodoDB] = []
next_id = 1

# Get todos with filters, pagination, sorting
class GetTodoParams(BaseModel):
    status: Optional[bool] = None
    sort: Optional[str] = "asc"
    id: Optional[int] = None
    search: Optional[str] = None


@app.get("/todos", response_model=List[Todo])
def get_todos(params: GetTodoParams = Depends(), pagination: dict = Depends(pagination_params), db: Session = Depends(get_db_session)):
    filters = []
    if params.id:
        filters.append(models.TodoDB.id == params.id)
    if params.status is not None:
        filters.append(models.TodoDB.status == params.status)
    if params.search:
        filters.append(models.TodoDB.task.ilike(f"%{params.search}%"))

    order_by = (
        models.TodoDB.id.asc()
        if params.sort.lower() == "asc"
        else models.TodoDB.id.desc()
    )

    todos = (
        db.query(models.TodoDB)
        .filter(*filters)
        .order_by(order_by)
        .offset(pagination["skip"])
        .limit(pagination["limit"])
        .all()
    )

    return todos


# Create new todo
@app.post("/add-todo", response_model=List[Todo], status_code=status.HTTP_201_CREATED)
def create_todo(items: List[TodoCreate], db: Session = Depends(get_db_session)):
    db_items = []
    
    for item in items:
        if not item.task.strip():
            raise HTTPException(status_code=400, detail="Task is required")
        db_item = models.TodoDB(**item.model_dump())
        db.add(db_item)
        db_items.append(db_item)
        
    db.commit()
    
    for db_item in db_items:
        db.refresh(db_item)
        
    return db_items

# Update todo by id
@app.put("/edit-todo", response_model=Todo)
def update_todo(param_item: TodoUpdate, db: Session = Depends(get_db_session), current_user: models.UserDB = Depends(get_current_user)):
    db_item = db.query(models.TodoDB).filter(models.TodoDB.id == param_item.id).first()
    if not db_item:
        raise HTTPException(status_code=404, detail="Todo not found")
    update_data = param_item.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)
         
    db.commit()
    db.refresh(db_item)
    return db_item
    
# Delete todo by id
@app.delete("/delete-todo/{todo_id}",response_model=dict)
def delete_todo(todo_id: int, db: Session = Depends(get_db_session), admin: str = Depends(check_admin_role)):
    db_item = db.query(models.TodoDB).filter(models.TodoDB.id == todo_id).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Todo deleted successfully"}


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    return {
        "error": exc.detail,
        "status_code": exc.status_code
    }
    
class CustomValidationError(ValueError):
    pass

@app.exception_handler(CustomValidationError)
async def custom_validation_handler(request, exc):
    return {
        "error": str(exc),
        "status_code": 400
    }
    


# USERS
@app.post("/register", response_model=User)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(models.UserDB).filter(models.UserDB.username == user.username).first()
    
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    
    hashed_password = get_password_hash(user.password)
    db_user = models.UserDB(username=user.username, email=user.email, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

# LOGIN: Trả về token (xem trong auth.py)
@app.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db:Session = Depends(get_db)):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}