from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.core.database import engine
from app.models.models import Base
from app.routers import posts, comments, users


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Create all tables on startup
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Blog REST API",
    description="RESTful API for a blog with posts and comments — Python/FastAPI + PostgreSQL",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users.router)
app.include_router(posts.router)
app.include_router(comments.router)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Blog API is running"}