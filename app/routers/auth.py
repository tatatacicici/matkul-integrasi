from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr

from app.core.database import get_db
from app.services.auth_service import login_user, refresh_user_token

router = APIRouter(prefix="/auth", tags=["Auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """
    POST /auth/login
    Returns access_token (2h) + refresh_token (7d).
    Pass access_token as: Authorization: Bearer <token>
    """
    return login_user(payload.email, payload.password, db)


@router.post("/refresh")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    """
    POST /auth/refresh
    Exchange expired access_token for a new one using refresh_token.
    Old refresh_token is invalidated and a new one is issued.
    """
    return refresh_user_token(payload.refresh_token, db)


@router.post("/logout")
def logout():
    """
    POST /auth/logout
    Stateless logout — client must discard both tokens.
    For stateful revocation, implement a token blacklist (Redis recommended).
    """
    return {"message": "Logged out successfully. Discard your tokens on the client side."}