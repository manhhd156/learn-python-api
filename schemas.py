from pydantic import BaseModel
from typing import Optional

class TodoBase(BaseModel):
    task: str
    status: bool = False

class TodoCreate(TodoBase):
    pass  # Dùng cho POST (không ID)

class TodoUpdate(TodoBase):
    task: Optional[str] = None  # Optional cho PATCH sau, nhưng dùng cho PUT
    status: Optional[bool] = None

class Todo(TodoBase):
    id: int  # ID từ DB

    class Config:
        orm_mode = True  # Cho phép convert từ DB object sang Pydantic