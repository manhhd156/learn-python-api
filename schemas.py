import re
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional

class TodoBase(BaseModel):
    task: str = Field(..., min_length=3, max_length=100, description="Task must be between 3 and 100 characters")
    status: bool = False

    @field_validator('task')
    def task_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Task cannot be empty or whitespace')
        return v.title()
    
    # Thêm custom validator trong schema cho task (regex: chỉ chữ/số, dùng pattern=r"^[a-zA-Z0-9 ]*$" trong Field).
    def task_must_be_alphanumeric(cls, v):
        if not re.match(r"^[a-zA-Z0-9 ]*$", v):
            raise ValueError('Task must be alphanumeric')
        return v

class TodoCreate(TodoBase):
    pass  # Dùng cho POST (không ID)

class TodoUpdate(TodoBase):
    task: Optional[str] = None  # Optional cho PATCH sau, nhưng dùng cho PUT
    status: Optional[bool] = None

class Todo(TodoBase):
    id: int  # ID từ DB

    class Config:
        orm_mode = True  # Cho phép convert từ DB object sang Pydantic
        
class UserBase(BaseModel):
    username: str = Field(..., min_length=3)
    email: EmailStr

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    username: str
    password: str

class User(UserBase):
    id: int
    is_active: bool

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str