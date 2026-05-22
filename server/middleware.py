from fastapi import Header, HTTPException

from server import token_store


def verify_token(access_token: str = Header(alias="Access-Token")) -> None:
    parts = access_token.split(" ", 1)
    token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else None
    if token is None or not token_store.is_valid(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
