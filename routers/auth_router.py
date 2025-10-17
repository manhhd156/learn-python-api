from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from dependencies import get_db_session
from schemas import UserCreate
# Import tương tự, tạo router cho /register và /login

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register")
async def register_user(user: UserCreate, db: Session = Depends(get_db_session)):
    # Logic đăng ký người dùng
    pass

@router.post("/login")
async def login_user(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db_session)):
    # Logic đăng nhập người dùng
    pass