from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from math import ceil

from app.core.database import get_db
from app.core.config import settings
from app.models.models import Comment, Post
from app.schemas.schemas import (
    CommentCreate, CommentUpdate, CommentOut,
    PaginatedResponse, PaginationMeta,
)
from app.middleware.auth import get_current_user, CurrentUser

router = APIRouter(prefix="/comments", tags=["Comments"])


def build_comment_out(c: Comment) -> CommentOut:
    return CommentOut(
        id=c.id,
        comment=c.comment,
        post_id=c.post_id,
        author=None,
    )


# ── Public endpoints ─────────────────────────────────────────────────────────

@router.get("/", response_model=PaginatedResponse[CommentOut])
def get_all_comments(
    post_id: int | None = None,
    page: int = 1,
    page_size: int = settings.DEFAULT_PAGE_SIZE,
    db: Session = Depends(get_db),
):
    """
    GET /comments — list comments with pagination.
    Filter by ?post_id=. Public endpoint.
    """
    if page < 1:
        raise HTTPException(status_code=400, detail="page must be >= 1")
    if page_size > settings.MAX_PAGE_SIZE:
        raise HTTPException(status_code=400, detail=f"page_size max is {settings.MAX_PAGE_SIZE}")

    query = db.query(Comment)
    if post_id is not None:
        query = query.filter(Comment.post_id == post_id)

    total = query.count()
    comments = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedResponse(
        data=[build_comment_out(c) for c in comments],
        meta=PaginationMeta(
            total=total,
            page=page,
            page_size=page_size,
            total_pages=ceil(total / page_size) if total else 1,
        ),
    )


@router.get("/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """GET /comments/{id} — public."""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")
    return build_comment_out(comment)


# ── Protected endpoints ───────────────────────────────────────────────────────

@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    POST /comments — create comment. Requires auth.
    user_id dari token, bukan dari body.
    """
    post = db.query(Post).filter(Post.id == payload.post_id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")

    comment = Comment(
        comment=payload.comment,
        post_id=payload.post_id,
        user_id=current_user.id,  # insecure direct object reference fix
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return build_comment_out(comment)


@router.patch("/{comment_id}", response_model=CommentOut)
def update_comment(
    comment_id: int,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    PATCH /comments/{id} — update comment. Requires auth.
    Hanya owner yang bisa update.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comments",
        )

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(comment, field, value)
    db.commit()
    db.refresh(comment)
    return build_comment_out(comment)


@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
):
    """
    DELETE /comments/{id} — delete comment. Requires auth.
    Hanya owner yang bisa delete.
    """
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comments",
        )

    db.delete(comment)
    db.commit()
    return {"id": comment_id, "deleted": True}


# ── 405 untuk verb yang tidak diizinkan ──────────────────────────────────────

@router.put("/", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
@router.put("/{comment_id}", status_code=status.HTTP_405_METHOD_NOT_ALLOWED)
def method_not_allowed():
    raise HTTPException(
        status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
        detail="Method not allowed. Use PATCH for partial updates.",
    )