from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.core.security import verify_password
from app.core.jwt import create_access_token, create_refresh_token, decode_token
from app.models.models import User


def login_user(email: str, password: str, db: Session) -> dict:
    user = db.query(User).filter(User.email == email).first()

    if not user or not verify_password(password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(user.id, user.email)
    refresh_token = create_refresh_token(user.id, user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": "2 hours",
    }


def refresh_user_token(refresh_token: str, db: Session) -> dict:
    payload = decode_token(refresh_token, expected_type="refresh")
    user_id = int(payload["sub"])

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    new_access = create_access_token(user.id, user.email)
    new_refresh = create_refresh_token(user.id, user.email)

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
        "expires_in": "2 hours",
    }