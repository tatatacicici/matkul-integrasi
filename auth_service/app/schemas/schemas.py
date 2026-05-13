from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional, List, Generic, TypeVar
from enum import Enum

T = TypeVar("T")


# ──────────────────────────────────────────
# Pagination meta
# ──────────────────────────────────────────

class PaginationMeta(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int


class PaginatedResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: PaginationMeta


# ──────────────────────────────────────────
# Post status
# ──────────────────────────────────────────

class PostStatus(str, Enum):
    draft = "draft"
    published = "published"


# ──────────────────────────────────────────
# User schemas
# DB fields: id, name, email, password
# Exposed: id, full_name, email  ← password NEVER returned
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


class UserOut(BaseModel):
    """
    DB field abstraction: password excluded, 'name' exposed as 'full_name'.
    """
    id: int
    full_name: str   # maps from DB 'name'
    email: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, user) -> "UserOut":
        return cls(id=user.id, full_name=user.name, email=user.email)


# ──────────────────────────────────────────
# Author (embedded in Post / Comment)
# ──────────────────────────────────────────

class AuthorOut(BaseModel):
    id: int
    full_name: str

    model_config = {"from_attributes": True}

    @classmethod
    def from_orm_model(cls, user) -> "AuthorOut":
        return cls(id=user.id, full_name=user.name)


# ──────────────────────────────────────────
# Post schemas
# ──────────────────────────────────────────

class PostBase(BaseModel):
    title: str
    status: PostStatus = PostStatus.draft
    content: str

    @field_validator("title")
    @classmethod
    def title_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Title cannot be empty")
        if len(v) > 100:
            raise ValueError("Title cannot exceed 100 characters")
        return v

    @field_validator("content")
    @classmethod
    def content_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Content cannot be empty")
        return v


class PostCreate(PostBase):
    pass
    # user_id diambil dari token, BUKAN dari request body
    # → mencegah insecure direct object reference


class PostUpdate(BaseModel):
    title: Optional[str] = None
    status: Optional[PostStatus] = None
    content: Optional[str] = None


class PostOut(BaseModel):
    """
    DB field abstraction: user_id disembunyikan, ditampilkan sebagai author object.
    """
    id: int
    title: str
    status: PostStatus
    content: str
    author: Optional[AuthorOut] = None
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

    @field_validator("comment")
    @classmethod
    def comment_not_empty(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("Comment cannot be empty")
        if len(v) > 250:
            raise ValueError("Comment cannot exceed 250 characters")
        return v


class CommentCreate(CommentBase):
    pass  # user_id dari token


class CommentUpdate(BaseModel):
    comment: Optional[str] = None


class CommentOut(BaseModel):
    """
    DB field abstraction: user_id disembunyikan, ditampilkan sebagai author object.
    """
    id: int
    comment: str
    post_id: int
    author: Optional[AuthorOut] = None

    model_config = {"from_attributes": True}


PostOut.model_rebuild()
PostOutWithComments.model_rebuild()