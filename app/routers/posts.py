from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from math import ceil

from app.core.database import get_db
from app.core.config import settings
from app.models.models import Post, User
from app.schemas.schemas import (
    PostCreate, PostUpdate, PostOut, PostOutWithComments,
    PaginatedResponse, PaginationMeta, AuthorOut, CommentOut
)
from app.middleware.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["Posts"])


def build_post_out(post: Post) -> PostOut:
    """Map ORM → PostOut with author abstraction."""
    return PostOut(
        id=post.id,
        title=post.title,
        status=post.status,
        content=post.content,
        author=AuthorOut.from_orm_model(post.author) if post.author else None,
        link=f"/posts/{post.id}",
    )


def build_comment_out(c) -> CommentOut:
    return CommentOut(
        id=c.id,
        comment=c.comment,
        post_id=c.post_id,
        author=AuthorOut.from_orm_model(c.author) if c.author else None,
    )


# ── Public endpoint ─────────────────────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse[PostOut])
def get_all_posts(
    page: int = 1,
    page_size: int = settings.DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
):
    """
    GET /posts — list all posts with pagination meta.
    Public endpoint, no auth required.
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if page_size > settings.MAX_PAGE_SIZE:
        raise HTTPException(status_code=400, detail=f"page_size max is {settings.MAX_PAGE_SIZE}")

    total = db.query(Post).count()
    posts = db.query(Post).offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        data=[build_post_out(p) for p in posts],
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if total else 1,
        ),
    )


@router.get("/{post_id}", response_model=PostOutWithComments)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """
    GET /posts/{id} — get single post with comments.
    Public endpoint, no auth required.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    return PostOutWithComments(
        id=post.id,
        title=post.title,
        status=post.status,
        content=post.content,
        author=AuthorOut.from_orm_model(post.author) if post.author else None,
        link=f"/posts/{post.id}",
        comments=[build_comment_out(c) for c in post.comments],
    )


# ── Protected endpoints (require Bearer token) ───────────────────────────────

@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(
    payload: PostCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),  # auth middleware
):
    """
    POST /posts — create post. Requires auth.
    user_id diambil dari token, bukan dari request body.
    """
    post = Post(
        title=payload.title,
        status=payload.status,
        content=payload.content,
        user_id=current_user.id,   # insecure direct object reference fix
    )
    db.add(post)
    db.commit()
    db.refresh(post)
    return build_post_out(post)


@router.patch("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    payload: PostUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    PATCH /posts/{id} — partial update. Requires auth.
    User hanya bisa update post miliknya sendiri.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    # ownership check
    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to modify another user's post",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return build_post_out(post)


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
def delete_post(
    post_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    DELETE /posts/{id} — delete post. Requires auth.
    User hanya bisa delete post miliknya sendiri.
    """
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    if post.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not allowed to delete another user's post",
        )

    db.delete(post)
    db.commit()
    return {"id": post_id, "deleted": True}


# ── 405 Method Not Allowed untuk verbs yang tidak diizinkan ─────────────────

@router.put("/", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
@router.put("/{post_id}", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_allowed():
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Method not allowed. Use PATCH for partial updates.",
    )