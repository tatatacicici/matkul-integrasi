from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.openapi.docs import get_redoc_html
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.limiter import limiter

from app.core.database import engine
from app.models.models import Base
from app.routers import posts, comments, users, auth
from fastapi.middleware.cors import CORSMiddleware


# ── Security headers middleware ───────────────────────────────────────────────

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Adds security headers to every response.
    In production, enforce HTTPS via reverse proxy (nginx/caddy).
    """
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Cache-Control"] = "no-store"
        return response


# ── Lifespan ──────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    # HAPUS ATAU KOMENTAR BARIS DI BAWAH INI:
    # Base.metadata.create_all(bind=engine)
    yield


# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="Blog REST API",
    description="RESTful API — FastAPI + PostgreSQL with auth, pagination, and security improvements",
    version="2.0.0",
    lifespan=lifespan,
    redoc_url=None,  # Disable default ReDoc to use a custom CDN
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)
app.add_middleware(SecurityHeadersMiddleware)

# ── Custom validation error handler (cleaner 422 response) ───────────────────

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        errors.append({
            "field": " → ".join(str(loc) for loc in err["loc"] if loc != "body"),
            "message": err["msg"],
        })
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation failed", "errors": errors},
    )


# ── Routers ───────────────────────────────────────────────────────────────────

api_v1_prefix = "/api/v1"
app.include_router(auth.router, prefix=api_v1_prefix)
app.include_router(users.router, prefix=api_v1_prefix)
app.include_router(posts.router, prefix=api_v1_prefix)
app.include_router(comments.router, prefix=api_v1_prefix)


@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="https://cdn.redoc.ly/redoc/latest/bundles/redoc.standalone.js",
    )


@app.get("/", response_class=HTMLResponse, tags=["Health"])
def root():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Blog REST API v2.0</title>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;800&display=swap" rel="stylesheet">
        <style>
            body {
                margin: 0;
                padding: 0;
                font-family: 'Inter', sans-serif;
                background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                color: #ffffff;
                height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .container {
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border: 1px solid rgba(255, 255, 255, 0.2);
                padding: 3rem;
                border-radius: 16px;
                text-align: center;
                box-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
                max-width: 500px;
                animation: fadeIn 1s ease-in-out;
            }
            h1 {
                font-size: 2.5rem;
                margin-bottom: 0.5rem;
                font-weight: 800;
            }
            p {
                font-size: 1.1rem;
                color: #d1d5db;
                margin-bottom: 2rem;
                line-height: 1.5;
            }
            .btn {
                display: inline-block;
                background: #3b82f6;
                color: white;
                padding: 10px 24px;
                border-radius: 8px;
                text-decoration: none;
                font-weight: 600;
                transition: background 0.3s, transform 0.2s;
                margin: 0 10px;
            }
            .btn:hover {
                background: #2563eb;
                transform: translateY(-2px);
            }
            .btn-outline {
                background: transparent;
                border: 2px solid #3b82f6;
            }
            .btn-outline:hover {
                background: rgba(59, 130, 246, 0.1);
            }
            .badges {
                margin-top: 2rem;
                display: flex;
                justify-content: center;
                gap: 10px;
            }
            .badge {
                background: rgba(255, 255, 255, 0.15);
                padding: 4px 10px;
                border-radius: 20px;
                font-size: 0.8rem;
                letter-spacing: 0.5px;
            }
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🚀 Blog API</h1>
            <p>RESTful API modern yang dibangun dengan FastAPI, PostgreSQL, dan SQLAlchemy.</p>
            <div>
                <a href="/docs" class="btn">📚 Swagger UI</a>
                <a href="/redoc" class="btn btn-outline">📖 ReDoc</a>
            </div>
            <div class="badges">
                <span class="badge">v2.0.0</span>
                <span class="badge">Status: Online</span>
            </div>
        </div>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)