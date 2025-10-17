from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class TodoDB(Base):
    __tablename__ = "todos"  # Tên table trong DB

    id = Column(Integer, primary_key=True, index=True)  # PK, auto-increment
    task = Column(String, index=True)  # String column, index cho search nhanh
    status = Column(Boolean, default=False)  # Boolean column
    owner_id = Column(Integer)  # Giả lập user_id (sẽ dùng cho auth sau)
    
    
class UserDB(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String) # Lưu hashed password, không lưu password thẳng
    is_active = Column(Boolean, default=True)