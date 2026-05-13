from app.models.models import Post

# ──────────────────────────────────────────
# A. Create Post (POST /posts)
# ──────────────────────────────────────────

def test_create_post_without_login(client):
    response = client.post("/api/v1/posts/", json={"title": "No Login", "content": "Test"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Not authenticated"


def test_create_post_after_login(authorized_client):
    payload = {
        "title": "My First Post",
        "content": "This is the content",
        "status": "published"
    }
    response = authorized_client.post("/api/v1/posts/", json=payload)
    assert response.status_code == 201
    
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["status"] == payload["status"]
    assert "id" in data


# ──────────────────────────────────────────
# B. Read Post (GET /posts & GET /posts/{id})
# ──────────────────────────────────────────

def test_list_posts(client, db_session, test_user):
    # Buat dummy posts
    post1 = Post(title="Post 1", content="Content 1", user_id=test_user.id)
    post2 = Post(title="Post 2", content="Content 2", user_id=test_user.id)
    db_session.add_all([post1, post2])
    db_session.commit()

    response = client.get("/api/v1/posts/")
    assert response.status_code == 200
    
    data = response.json()
    assert "data" in data
    assert "meta" in data
    assert isinstance(data["data"], list)
    assert len(data["data"]) == 2
    assert data["meta"]["total"] == 2


def test_get_single_post(client, db_session, test_user):
    post = Post(title="Single Post", content="Content", user_id=test_user.id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    response = client.get(f"/api/v1/posts/{post.id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single Post"


def test_get_single_post_not_found(client):
    response = client.get("/api/v1/posts/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


# ──────────────────────────────────────────
# C. Update Post (PATCH /posts/{id})
# ──────────────────────────────────────────

def test_update_post_correct_owner(authorized_client, db_session, test_user):
    post = Post(title="Old Title", content="Content", user_id=test_user.id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    response = authorized_client.patch(f"/api/v1/posts/{post.id}", json={"title": "New Title"})
    assert response.status_code == 200
    assert response.json()["title"] == "New Title"


def test_update_post_wrong_owner(other_authorized_client, db_session, test_user):
    post = Post(title="Old Title", content="Content", user_id=test_user.id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    response = other_authorized_client.patch(f"/api/v1/posts/{post.id}", json={"title": "New Title"})
    assert response.status_code == 403
    assert "not allowed to modify" in response.json()["detail"].lower()


def test_update_post_without_login(client, db_session, test_user):
    post = Post(title="Old Title", content="Content", user_id=test_user.id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    response = client.patch(f"/api/v1/posts/{post.id}", json={"title": "New Title"})
    assert response.status_code == 401


# ──────────────────────────────────────────
# D. Delete Post (DELETE /posts/{id})
# ──────────────────────────────────────────

def test_delete_post_correct_owner(authorized_client, db_session, test_user):
    post = Post(title="To Delete", content="Content", user_id=test_user.id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    response = authorized_client.delete(f"/api/v1/posts/{post.id}")
    assert response.status_code == 200
    assert response.json()["deleted"] is True

    # Validasi 404
    get_response = authorized_client.get(f"/api/v1/posts/{post.id}")
    assert get_response.status_code == 404


def test_delete_post_wrong_owner(other_authorized_client, db_session, test_user):
    post = Post(title="To Delete", content="Content", user_id=test_user.id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    response = other_authorized_client.delete(f"/api/v1/posts/{post.id}")
    assert response.status_code == 403
    assert "not allowed to delete" in response.json()["detail"].lower()


def test_delete_post_without_login(client, db_session, test_user):
    post = Post(title="To Delete", content="Content", user_id=test_user.id)
    db_session.add(post)
    db_session.commit()
    db_session.refresh(post)

    response = client.delete(f"/api/v1/posts/{post.id}")
    assert response.status_code == 401
