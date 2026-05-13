import httpx
from typing import List, Dict
from app.core.config import settings
from app.schemas.schemas import AuthorOut


def get_users_batch(user_ids: List[int]) -> Dict[int, AuthorOut]:
    """
    Mengambil data user dari Auth Service dan mengubahnya menjadi Dictionary
    agar mudah digabungkan (stitching) dengan data Post/Comment.

    Returns:
        Dict[user_id, AuthorOut] — kosong jika Auth Service tidak tersedia.
    """
    if not user_ids:
        return {}

    # Hilangkan ID yang duplikat agar request lebih ringan
    unique_ids = list(set(user_ids))

    try:
        url = f"{settings.AUTH_SERVICE_URL}/api/v1/users/batch"
        # Synchronous HTTP Call ke Auth Service
        response = httpx.post(url, json={"user_ids": unique_ids}, timeout=5.0)
        response.raise_for_status()

        users_data = response.json()

        # Ubah list response menjadi dictionary: { user_id: AuthorOut }
        return {
            user["id"]: AuthorOut(id=user["id"], full_name=user["full_name"])
            for user in users_data
        }
    except Exception as e:
        print(f"[user_client] Error fetching users from Auth Service: {e}")
        return {}  # Jika Auth Service mati, kembalikan dictionary kosong (graceful degradation)
