"""Opaque guest workspace credentials; names are display labels, not authentication."""

import secrets
from fastapi import Header, HTTPException


def new_credential() -> str:
    return secrets.token_urlsafe(32)


def require_credential(x_workspace_token: str | None = Header(default=None)) -> str:
    if not x_workspace_token:
        raise HTTPException(status_code=401, detail="Workspace credential is required")
    return x_workspace_token
