from fastapi import APIRouter, Depends, HTTPException, Response

from app.core.config import settings
from app.core.security import require_credential
from app.infrastructure.dataset_store import store
from app.modules.sessions.schemas import SessionCreate, SessionResponse
from app.modules.sessions.service import create_session

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse, status_code=201)
def start_session(payload: SessionCreate):
    workspace = create_session(payload.display_name)
    return SessionResponse(session_id=workspace.session_id, display_name=workspace.display_name,
                           token=workspace.token, expires_in_minutes=settings.session_ttl_minutes)


@router.delete("/{session_id}", status_code=204)
def end_session(session_id: str, token: str = Depends(require_credential)):
    try:
        store.delete(session_id, token)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=410, detail=str(exc)) from exc
    return Response(status_code=204)
