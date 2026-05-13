from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from app.core.jwt import decode_token

bearer_scheme = HTTPBearer()


# Buat class sederhana untuk menampung data user dari dalam Token
class CurrentUser(BaseModel):
    id: int
    email: str


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> CurrentUser:
    """
    Di Microservices, Blog Service tidak nge-hit database User.
    Cukup validasi signature JWT dan ambil data dari payload-nya.
    """
    payload = decode_token(credentials.credentials, expected_type="access")

    # Kembalikan object CurrentUser (bukan ORM Model)
    return CurrentUser(
        id=int(payload["sub"]),
        email=payload["email"]
    )