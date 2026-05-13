import pytest

def test_rate_limiter_on_register(client):
    """
    Test rate limiting di endpoint POST /api/v1/users/
    Limit saat ini diset "5/minute".
    """
    url = "/api/v1/users/"
    
    # Payload dummy untuk tiap request
    # Kita tidak peduli dengan error 409 (Email already registered) karena yang penting adalah
    # apakah limiter memblokir berdasarkan jumlah request (meski request invalid).
    # Namun untuk clean testing, kita gunakan data unik.
    
    payload = {
        "name": "Rate Limit Test",
        "email": "ratelimit@example.com",
        "password": "password123"
    }

    # Hit 5 kali (harus berhasil melewati rate limiter,
    # walau mungkin request 2-5 kena error 409 Conflict karena email sudah ada,
    # tapi TIDAK BOLEH error 429 Too Many Requests).
    for i in range(5):
        payload["email"] = f"ratelimit{i}@example.com"
        response = client.post(url, json=payload)
        # Status code harus 201 Created
        assert response.status_code == 201

    # Hit ke-6 (harus kena blokir rate limiter)
    payload["email"] = "ratelimit6@example.com"
    response = client.post(url, json=payload)
    
    assert response.status_code == 429
    assert "Rate limit exceeded" in response.json()["error"]

