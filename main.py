from fastapi import FastAPI, HTTPException
from typing import Dict, List, Optional
from pydantic import Field

from fastapi.params import Depends
from pydantic import BaseModel  # Để type hint cho data echo

app = FastAPI(
    title="My First Backend API",  # Tiêu đề hiển thị trong docs
    description="API cơ bản để học FastAPI - Ngày 1",
    version="1.0.0"
)

@app.get("/")
def home():
    return {"message": "Hello World"}

class TodoItem(BaseModel):
    id: Optional[int] = None
    task: str
    status: bool = False

    class Config:
        orm_mode = True # Cấu hình để hỗ trợ ORM nếu cần

todos: List[TodoItem] = []
next_id = 1

class GetTodoParams(BaseModel):
    status: Optional[bool] = None
    sort: Optional[str] = None # "asc" | "desc"
    id: Optional[int] = None

# Get list todos
@app.get("/todos", response_model=List[TodoItem])
def get_todos(params: GetTodoParams = Depends()):
    # Copy danh sách gốc để thao tác
    filtered_todos = todos.copy()
    # Lọc và sắp xếp todos dựa trên query params
    if params.sort == 'asc':
        filtered_todos = sorted(filtered_todos, key=lambda x: x.id)
    elif params.sort == 'desc':
        filtered_todos = sorted(filtered_todos, key=lambda x: x.id, reverse=True)
        
    # Lọc theo status nếu có
    if params.status is not None:
        filtered_todos = [todo for todo in filtered_todos if todo.status == params.status]

    
    # Lọc theo id nếu có
    if params.id is not None:
        return [todo for todo in filtered_todos if todo.id == params.id]
    return filtered_todos

# Create new todo
@app.post("/add-todo", response_model=List[TodoItem], status_code=201)
def create_todo(items: List[TodoItem]):
    """
    Thêm một todo mới.
    - Body: {"task": "Học FastAPI", "completed": false}
    - Validate: task phải là str, không rỗng (Pydantic tự check)
    """
    global next_id
    for item in items:
        if not item.task:
            raise HTTPException(status_code=400, detail="Task is required")
        item.id = next_id
        next_id += 1
        item.status = False
        todos.append(item)
    return items

# Update todo by id
@app.put("/edit-todo", response_model=TodoItem)
def update_todo(param_item: TodoItem):
    for index, item in enumerate(todos):
        if item.id == param_item.id:
            todos[index] = param_item
            return param_item
    raise HTTPException(status_code=404, detail="Todo not found")

# Delete todo by id
@app.delete("/delete-todo/{todo_id}", status_code=204)
def delete_todo(todo_id: int):
    for index, item in enumerate(todos):
        if item.id == todo_id:
            del todos[index]
            return {"message": "Todo deleted"}
    raise HTTPException(status_code=404, detail="Todo not found")