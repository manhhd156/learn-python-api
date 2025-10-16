from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
from pydantic import Field

from fastapi.params import Depends
from pydantic import BaseModel
from database import engine, get_db

import models
from schemas import Todo, TodoCreate, TodoUpdate, TodoUpdate  # Để type hint cho data echo
from sqlalchemy.orm import Session

app = FastAPI(
    title="My First Backend API",  # Tiêu đề hiển thị trong docs
    description="API cơ bản để học FastAPI - Ngày 1",
    version="1.0.0"
)

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
    page: int = 1
    limit: int = 10


@app.get("/todos", response_model=List[Todo])
def get_todos(params: GetTodoParams = Depends(), db: Session = Depends(get_db)):
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

    skip = (params.page - 1) * params.limit
    todos = (
        db.query(models.TodoDB)
        .filter(*filters)
        .order_by(order_by)
        .offset(skip)
        .limit(params.limit)
        .all()
    )

    return todos


# Create new todo
@app.post("/add-todo", response_model=List[Todo], status_code=201)
def create_todo(items: List[TodoCreate], db: Session = Depends(get_db)):
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
def update_todo(param_item: TodoUpdate, db: Session = Depends(get_db)):
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
def delete_todo(todo_id: int, db: Session = Depends(get_db)):
    db_item = db.query(models.TodoDB).filter(models.TodoDB.id == todo_id).first()
    
    if not db_item:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(db_item)
    db.commit()
    return {"message": "Todo deleted successfully"}