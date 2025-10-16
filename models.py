from sqlalchemy import Column, Integer, String, Boolean
from database import Base

class TodoDB(Base):
    __tablename__ = "todos"  # Tên table trong DB

    id = Column(Integer, primary_key=True, index=True)  # PK, auto-increment
    task = Column(String, index=True)  # String column, index cho search nhanh
    status = Column(Boolean, default=False)  # Boolean column