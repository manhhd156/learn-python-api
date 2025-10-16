from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from schemas import TodoUpdate
from typing import Optional

# Dependency để lấy session DB (inject vào routes)
def get_db_session(db: Session = Depends(get_db)):
    return db

# Custom dependency: Kiểm tra quyền (giả lập, sau dùng cho auth)
def check_admin_role(current_user: str = "user"):  # Sau thay bằng auth
    if current_user != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

# Dependency cho pagination (inject vào GET)
def pagination_params(skip: int = 0, limit: int = 10):
    if limit > 100:  # Giới hạn max để tránh overload
        raise HTTPException(status_code=400, detail="Limit cannot exceed 100")
    # Thêm dependency cho rate limiting giả lập (e.g., check nếu skip < 0 raise error).
    if skip < 0:
        raise HTTPException(status_code=400, detail="Skip must be non-negative")
    
    return {"skip": skip, "limit": limit}