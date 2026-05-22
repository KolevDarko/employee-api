from datetime import datetime, timezone


_store: dict[str, datetime] = {}


def save_token(token: str, expires_at: datetime) -> None:
    _store[token] = expires_at


def is_valid(token: str) -> bool:
    expires_at = _store.get(token)
    if expires_at is None:
        return False
    return datetime.now(timezone.utc) < expires_at
