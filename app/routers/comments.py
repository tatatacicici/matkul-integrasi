from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Comment, Post
from app.schemas.schemas import CommentCreate, CommentUpdate, CommentOut

router = APIRouter(prefix="/comments", tags=["Comments"])


@router.get("/", response_model=List[CommentOut])
def get_all_comments(post_id: int | None = None, db: Session = Depends(get_db)):
    """GET /comments — list all comments, optionally filter by ?post_id="""
    query = db.query(Comment)
    if post_id is not None:
        query = query.filter(Comment.post_id == post_id)
    return query.all()


@router.post("/", response_model=CommentOut, status_code=status.HTTP_201_CREATED)
def create_comment(payload: CommentCreate, db: Session = Depends(get_db)):
    """POST /comments — create a comment on a post"""
    # validate post exists
    post = db.query(Post).filter(Post.id == payload.post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {payload.post_id} not found"
        )
    comment = Comment(**payload.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/{comment_id}", response_model=CommentOut)
def get_comment(comment_id: int, db: Session = Depends(get_db)):
    """GET /comments/{id} — get a single comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found"
        )
    return comment


@router.patch("/{comment_id}", response_model=CommentOut)
def update_comment(comment_id: int, payload: CommentUpdate, db: Session = Depends(get_db)):
    """PATCH /comments/{id} — update a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found"
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/{comment_id}", status_code=status.HTTP_200_OK)
def delete_comment(comment_id: int, db: Session = Depends(get_db)):
    """DELETE /comments/{id} — delete a comment"""
    comment = db.query(Comment).filter(Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Comment with id {comment_id} not found"
        )
    db.delete(comment)
    db.commit()
    return {"id": comment_id, "deleted": True}