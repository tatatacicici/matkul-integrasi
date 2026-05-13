from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
import enum


class PostStatus(str, enum.Enum):
    draft = "draft"
    published = "published"


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String(100), nullable=False)
    status = Column(Enum(PostStatus), nullable=False, default=PostStatus.draft)
    content = Column(Text, nullable=False)

    # UBAH: Hanya simpan ID-nya saja, tanpa ForeignKey ke tabel users
    user_id = Column(Integer, nullable=False)

    comments = relationship("Comment", back_populates="post")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    comment = Column(String(250), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id", ondelete="RESTRICT"), nullable=False)

    # UBAH: Hanya simpan ID-nya saja, tanpa ForeignKey ke tabel users
    user_id = Column(Integer, nullable=False)

    post = relationship("Post", back_populates="comments")