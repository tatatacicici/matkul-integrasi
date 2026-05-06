from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.models import Post
from app.schemas.schemas import PostCreate, PostUpdate, PostOut, PostOutWithComments

router = APIRouter(prefix="/posts", tags=["Posts"])


@router.get("/", response_model=List[PostOut])
def get_all_posts(db: Session = Depends(get_db)):
    """GET /posts — list all posts"""
    return db.query(Post).all()


@router.post("/", response_model=PostOut, status_code=status.HTTP_201_CREATED)
def create_post(payload: PostCreate, db: Session = Depends(get_db)):
    """POST /posts — create a new post"""
    post = Post(**payload.model_dump())
    db.add(post)
    db.commit()
    db.refresh(post)
    # attach link field
    post_out = PostOut.model_validate(post)
    post_out.link = f"/posts/{post.id}"
    return post_out


@router.get("/{post_id}", response_model=PostOutWithComments)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """GET /posts/{id} — get single post with its comments"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found"
        )
    return post


@router.patch("/{post_id}", response_model=PostOut)
def update_post(post_id: int, payload: PostUpdate, db: Session = Depends(get_db)):
    """PATCH /posts/{id} — partial update a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found"
        )
    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(post, field, value)
    db.commit()
    db.refresh(post)
    return post


@router.delete("/{post_id}", status_code=status.HTTP_200_OK)
def delete_post(post_id: int, db: Session = Depends(get_db)):
    """DELETE /posts/{id} — delete a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Post with id {post_id} not found"
        )
    db.delete(post)
    db.commit()
    return {"id": post_id, "deleted": True}