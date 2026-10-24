from fastapi import Depends, HTTPException

from app.core.security import require_credential
from app.infrastructure.dataset_store import store


def get_workspace(session_id: str, token: str = Depends(require_credential)):
    try:
        return store.workspace(session_id, token)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail="Workspace not found") from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=410, detail="Workspace expired") from exc
