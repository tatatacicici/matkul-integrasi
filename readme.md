# Blog REST API — FastAPI + PostgreSQL

Implementasi RESTful API menggunakan FastAPI, SQLAlchemy, dan PostgreSQL dengan arsitektur yang modern, aman, dan *production-ready*.

## Stack Teknologi

| Kategori | Teknologi |
|----------|-----------|
| **Framework** | FastAPI |
| **Database & ORM** | PostgreSQL 16 + SQLAlchemy 2.0 |
| **Migrasi** | Alembic |
| **Validasi** | Pydantic v2 |
| **Autentikasi** | JWT (PyJWT) + bcrypt |
| **Rate Limiting** | SlowAPI |
| **Testing** | Pytest + httpx |
| **Server** | Uvicorn |
| **Containerization** | Docker + Docker Compose |
| **Tooling** | Make, pip-tools (via `pyproject.toml`) |

## Struktur Project

```text
blog-api/
├── app/
│   ├── main.py              # Entrypoint FastAPI
│   ├── core/                # Core configurations
│   │   ├── config.py        # Settings (Pydantic BaseSettings)
│   │   ├── database.py      # Engine + SessionLocal
│   │   ├── jwt.py           # JWT Token generation
│   │   ├── limiter.py       # SlowAPI Limiter
│   │   └── security.py      # Password hashing (bcrypt)
│   ├── middleware/
│   │   └── auth.py          # JWT Middleware / Dependencies
│   ├── models/
│   │   └── models.py        # SQLAlchemy ORM (User, Post, Comment)
│   ├── schemas/
│   │   └── schemas.py       # Pydantic request/response schemas
│   ├── services/
│   │   └── auth_service.py  # Login & Refresh token logic
│   └── routers/             # API Endpoints (v1)
│       ├── auth.py
│       ├── users.py
│       ├── posts.py
│       └── comments.py
├── alembic/                 # Alembic migration environment
│   ├── env.py               # Konfigurasi migration environment
│   ├── script.py.mako       # Template script migration
│   └── versions/            # File-file migration (auto-generated)
├── tests/                   # Pytest suites
├── alembic.ini              # Konfigurasi Alembic
├── Dockerfile               # Docker image definition
├── docker-compose.yml       # Docker services (API, DB, pgAdmin)
├── Makefile                 # Automation scripts
├── pyproject.toml           # Dependencies & tools config
├── requirements.txt         # Locked production dependencies
├── requirements-dev.txt     # Locked dev dependencies
└── .env.example             # Template environment variables
```

## Cara Menjalankan

Project ini sudah dilengkapi dengan `Makefile` untuk mempermudah eksekusi layaknya menggunakan Composer/Artisan.

### Via Docker (Rekomendasi)

```bash
# 1. Siapkan environment variables
cp .env.example .env

# 2. Jalankan docker (Build image & run services)
#    Database migration dijalankan otomatis via entrypoint
make up

# 3. Hentikan docker
make down

# 4. Lihat logs API
make logs
```

### Via Local Virtual Environment

```bash
# 1. Siapkan environment variables
cp .env.example .env

# 2. Setup virtual environment & install dependensi
make setup
make install

# 3. Jalankan database migration (Alembic)
.venv/bin/alembic upgrade head

# 4. Jalankan development server
make dev

# 5. Jalankan automated tests
.venv/bin/pytest
```

> **Akses Layanan:**
> - **API Base URL:** `http://localhost:8000`
> - **Swagger UI Docs:** `http://localhost:8000/docs`
> - **pgAdmin:** `http://localhost:5050` (Login: `admin@blog.local` / `admin`)

### Referensi Make Targets

| Target | Deskripsi |
|--------|-----------|
| `make setup` | Buat virtual environment |
| `make compile` | Generate `requirements*.txt` dari `pyproject.toml` |
| `make install` | Install semua dependensi (dev) |
| `make install-prod` | Install dependensi production saja |
| `make dev` | Jalankan development server (hot-reload) |
| `make format` | Format kode dengan Ruff |
| `make lint` | Cek linting dengan Ruff |
| `make up` | Build & jalankan Docker services |
| `make down` | Hentikan Docker services |
| `make logs` | Lihat logs service API |
| `make clean` | Hapus file `__pycache__` & `.pytest_cache` |

---

## Daftar Endpoints (API v1)

Semua endpoint utama kini menggunakan prefix `/api/v1`. Beberapa endpoint dibatasi dengan **Rate Limiting** dan dilindungi oleh **JWT Authentication**.

### Auth
| Method | URL | Deskripsi | Akses |
|--------|-----|-----------|-------|
| `POST` | `/api/v1/auth/login` | Login & dapatkan token | Public *(Max 5/mnt)* |
| `POST` | `/api/v1/auth/refresh` | Refresh access token | Public *(Max 10/mnt)* |
| `POST` | `/api/v1/auth/logout` | Logout (Client hapus token) | Public |

### Users
| Method | URL | Deskripsi | Akses |
|--------|-----|-----------|-------|
| `POST` | `/api/v1/users/` | Registrasi user baru | Public *(Max 5/mnt)* |
| `GET`  | `/api/v1/users/me` | Lihat profil sendiri | **Protected** |
| `PATCH`| `/api/v1/users/me` | Update profil sendiri | **Protected** |

### Posts
| Method | URL | Deskripsi | Akses |
|--------|-----|-----------|-------|
| `GET`  | `/api/v1/posts/` | List postingan (dengan paginasi) | Public |
| `GET`  | `/api/v1/posts/{id}` | Detail postingan + komentar | Public |
| `POST` | `/api/v1/posts/` | Buat postingan baru | **Protected** |
| `PATCH`| `/api/v1/posts/{id}` | Update postingan (hanya pemilik) | **Protected** |
| `DELETE`|`/api/v1/posts/{id}` | Hapus postingan (hanya pemilik) | **Protected** |

### Comments
| Method | URL | Deskripsi | Akses |
|--------|-----|-----------|-------|
| `GET`  | `/api/v1/comments/` | List komentar (`?post_id=`) | Public |
| `GET`  | `/api/v1/comments/{id}` | Detail komentar | Public |
| `POST` | `/api/v1/comments/` | Buat komentar baru | **Protected** |
| `PATCH`| `/api/v1/comments/{id}`| Update komentar (hanya pemilik)| **Protected** |
| `DELETE`|`/api/v1/comments/{id}`| Hapus komentar (hanya pemilik) | **Protected** |

---

## Contoh Request (cURL)

### 1. Registrasi & Login

```bash
# Registrasi User
curl -X POST http://localhost:8000/api/v1/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Budi", "email": "budi@email.com", "password": "rahasia"}'

# Login untuk mendapatkan Access Token
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "budi@email.com", "password": "rahasia"}'
  
# -> Copy "access_token" dari response untuk request selanjutnya!
```

### 2. Post & Comments (Membutuhkan JWT)

```bash
# Set variabel token (Ganti tulisan TOKEN_DISINI)
export TOKEN="TOKEN_DISINI"

# Buat Postingan Baru
# (Perhatikan: user_id tidak perlu dikirim karena diambil dari token otomatis)
curl -X POST http://localhost:8000/api/v1/posts/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My First Post", "content": "Hello World!", "status": "published"}'

# Update Postingan
curl -X PATCH http://localhost:8000/api/v1/posts/1 \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'

# Buat Komentar
curl -X POST http://localhost:8000/api/v1/comments/ \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"post_id": 1, "comment": "Bagus artikelnya!"}'
```

### 3. Public Endpoints (Tanpa JWT)

```bash
# Lihat daftar Postingan (Paginasi tersedia dengan ?page=1&page_size=10)
curl http://localhost:8000/api/v1/posts/

# Lihat detail Postingan beserta komentarnya
curl http://localhost:8000/api/v1/posts/1
```