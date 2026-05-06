from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List
from enum import Enum


class PostStatus(str, Enum):
    draft = "draft"
    published = "published"


# ──────────────────────────────────────────
# User schemas
# ──────────────────────────────────────────

class UserBase(BaseModel):
    name: str
    email: EmailStr


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserOut(UserBase):
    id: int

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────
# Post schemas
# ──────────────────────────────────────────

class PostBase(BaseModel):
    title: str
    status: PostStatus = PostStatus.draft
    content: str
    user_id: int

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Title cannot be empty")
        if len(v) > 100:
            raise ValueError("Title cannot exceed 100 characters")
        return v


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[PostStatus] = None
    content: Optional[str] = None
    user_id: Optional[int] = None


class PostOut(PostBase):
    id: int
    link: Optional[str] = None

    model_config = {"from_attributes": True}


class PostOutWithComments(PostOut):
    comments: List["CommentOut"] = []

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────
# Comment schemas
# ──────────────────────────────────────────

class CommentBase(BaseModel):
    comment: str
    post_id: int
    user_id: int

    @field_validator("comment")
    @classmethod
    def comment_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Comment cannot be empty")
        if len(v) > 250:
            raise ValueError("Comment cannot exceed 250 characters")
        return v


class CommentCreate(CommentBase):
    pass


class CommentUpdate(BaseModel):
    comment: Optional[str] = None


class CommentOut(CommentBase):
    id: int

    model_config = {"from_attributes": True}


PostOutWithComments.model_rebuild()