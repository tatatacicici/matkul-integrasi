# Blog REST API — FastAPI + PostgreSQL

Implementasi RESTful API dari contoh PHP ke Python menggunakan FastAPI, SQLAlchemy, dan PostgreSQL.

## Stack

| Layer | Tech |
|-------|------|
| Framework | FastAPI |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 16 |
| Validation | Pydantic v2 |
| Auth utils | Passlib + bcrypt |
| Server | Uvicorn |

## Struktur Project

```
blog-api/
├── app/
│   ├── main.py              # entrypoint FastAPI
│   ├── core/
│   │   ├── config.py        # settings (env vars)
│   │   ├── database.py      # engine + session + get_db
│   │   └── security.py      # password hashing
│   ├── models/
│   │   └── models.py        # SQLAlchemy ORM (User, Post, Comment)
│   ├── schemas/
│   │   └── schemas.py       # Pydantic request/response schemas
│   └── routers/
│       ├── users.py
│       ├── posts.py
│       └── comments.py
├── Dockerfile
├── docker-compose.yaml
├── requirements.txt
└── .env.example
```

## Cara Jalankan

```bash
# 1. Clone / copy project
cp .env.example .env

# 2. Build dan jalankan semua service
docker compose up --build

# 3. API tersedia di:
#    http://localhost:8000
#    http://localhost:8000/docs   ← Swagger UI
#    http://localhost:8000/redoc  ← ReDoc

# pgAdmin tersedia di:
#    http://localhost:5050
#    email: admin@blog.local / password: admin
```

## Endpoints

### Users
| Method | URL | Deskripsi |
|--------|-----|-----------|
| GET | /users/ | List semua user |
| POST | /users/ | Buat user baru |
| GET | /users/{id} | Detail user |

### Posts
| Method | URL | Deskripsi |
|--------|-----|-----------|
| GET | /posts/ | List semua post |
| POST | /posts/ | Buat post baru |
| GET | /posts/{id} | Detail post + comments |
| PATCH | /posts/{id} | Update sebagian post |
| DELETE | /posts/{id} | Hapus post |

### Comments
| Method | URL | Deskripsi |
|--------|-----|-----------|
| GET | /comments/ | List semua comment (filter: ?post_id=) |
| POST | /comments/ | Buat comment |
| GET | /comments/{id} | Detail comment |
| PATCH | /comments/{id} | Update comment |
| DELETE | /comments/{id} | Hapus comment |

## Contoh Request (curl)

```bash
# Buat user
curl -X POST http://localhost:8000/users/ \
  -H "Content-Type: application/json" \
  -d '{"name": "Haafiz", "email": "haafiz@email.com", "password": "qwerty"}'

# Buat post
curl -X POST http://localhost:8000/posts/ \
  -H "Content-Type: application/json" \
  -d '{"title": "First Post", "content": "Hello world", "status": "published", "user_id": 1}'

# List posts
curl http://localhost:8000/posts/

# Update post (PATCH)
curl -X PATCH http://localhost:8000/posts/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}'

# Hapus post
curl -X DELETE http://localhost:8000/posts/1
```