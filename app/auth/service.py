from datetime import datetime, timezone

import httpx

from app.settings import get_settings

_cached_token: "AuthToken | None" = None


class AuthToken:
    def __init__(self, token: str, expires_at: datetime) -> None:
        self.token = token
        self.expires_at = expires_at

    def is_expired(self) -> bool:
        return datetime.now(timezone.utc) > self.expires_at


async def get_token() -> str:
    global _cached_token
    if _cached_token is None or _cached_token.is_expired():
        _cached_token = await _fetch_new_token()
    return _cached_token.token


async def _fetch_new_token() -> AuthToken:
    settings = get_settings()
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.employee_api_token_url,
            json={
                "grant_type": settings.employee_api_grant_type,
                "client_id": settings.employee_api_client_id,
                "client_secret": settings.employee_api_client_secret,
                "username": settings.employee_api_username,
                "password": settings.employee_api_password,
            },
        )
        response.raise_for_status()
        data = response.json()
        return AuthToken(
            token=data["access_token"],
            expires_at=datetime.fromisoformat(data["expires_at"]),
        )
