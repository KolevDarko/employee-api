from datetime import datetime, timedelta, timezone
from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel

from server import token_store

router = APIRouter(tags=["auth"])

TOKEN_TTL_MINUTES = 10


class TokenRequest(BaseModel):
    grant_type: str
    client_id: str
    client_secret: str
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    expires_at: str


def build_token_response() -> TokenResponse:
    token = str(uuid4())
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_TTL_MINUTES)
    token_store.save_token(token, expires_at)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_at=expires_at.isoformat(),
    )


@router.post("/token", response_model=TokenResponse)
def get_token(credentials: TokenRequest) -> TokenResponse:
    return build_token_response()
