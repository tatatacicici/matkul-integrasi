from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import hash_password
from app.models.models import User
from app.schemas.schemas import UserCreate, UserOut
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    """POST /users — register. Public."""
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(name=payload.name, email=payload.email, password=hash_password(payload.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.from_orm_model(user)


@router.get("/me", response_model=UserOut)
def get_me(current_user: User = Depends(get_current_user)):
    """
    GET /users/me — get own profile.
    Insecure direct object reference fix: user resolved from token, not from URL param.
    Requires auth.
    """
    return UserOut.from_orm_model(current_user)


@router.patch("/me", response_model=UserOut)
def update_me(
    payload: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    PATCH /users/me — update own profile.
    User ID dari token, bukan dari URL.
    """
    if payload.email != current_user.email:
        if db.query(User).filter(User.email == payload.email).first():
            raise HTTPException(status_code=409, detail="Email already taken")
    current_user.name = payload.name
    current_user.email = payload.email
    current_user.password = hash_password(payload.password)
    db.commit()
    db.refresh(current_user)
    return UserOut.from_orm_model(current_user)


# ── Restrict: no direct /users/{id} modification ─────────────────────────────

@router.get("/{user_id}", status_code=status.HTTP_403_FORBIDDEN)
def get_user_by_id_forbidden():
    """
    GET /users/{id} — forbidden.
    Use /users/me instead. Prevents insecure direct object reference.
    """
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Direct user access by ID is not allowed. Use /users/me instead.",
    )