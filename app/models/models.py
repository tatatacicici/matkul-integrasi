from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class PostStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    email = Column(String(50), unique=True, nullable=False, index=True)
    password = Column(String(255), nullable=False)

    posts = relationship("Post", back_populates="author")
    comments = relationship("Comment", back_populates="author")


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    status = Column(Enum(PostStatus), nullable=False, default=PostStatus.draft)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    author = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    comment = Column(String(250), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="RESTRICT"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="RESTRICT"), nullable=False)

    post = relationship("Post", back_populates="comments")
    author = relationship("User", back_populates="comments")