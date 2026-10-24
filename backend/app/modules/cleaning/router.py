from fastapi import APIRouter, Depends, HTTPException

from app.core.security import require_credential
from app.modules.cleaning.schemas import OperationRequest
from app.modules.cleaning.service import apply_operation, history, preview_operation, reset, undo

router = APIRouter(prefix="/datasets/{dataset_id}", tags=["cleaning"])


def handle(exc: Exception):
    if isinstance(exc, HTTPException):
        raise exc
    if isinstance(exc, KeyError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, TimeoutError):
        raise HTTPException(status_code=410, detail="Workspace expired") from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/operations/preview")
def preview(dataset_id: str, payload: OperationRequest, token: str = Depends(require_credential)):
    try:
        return preview_operation(dataset_id, token, payload)
    except (KeyError, TimeoutError, ValueError, HTTPException) as exc:
        handle(exc)


@router.post("/operations")
def apply(dataset_id: str, payload: OperationRequest, token: str = Depends(require_credential)):
    try:
        return apply_operation(dataset_id, token, payload)
    except (KeyError, TimeoutError, ValueError, HTTPException) as exc:
        handle(exc)


@router.get("/history")
def get_history(dataset_id: str, token: str = Depends(require_credential)):
    try:
        return history(dataset_id, token)
    except (KeyError, TimeoutError, ValueError) as exc:
        handle(exc)


@router.post("/undo")
def undo_last(dataset_id: str, expected_revision: int, token: str = Depends(require_credential)):
    try:
        return undo(dataset_id, token, expected_revision)
    except (KeyError, TimeoutError, ValueError, HTTPException) as exc:
        handle(exc)


@router.post("/reset")
def reset_dataset(dataset_id: str, expected_revision: int, token: str = Depends(require_credential)):
    try:
        return reset(dataset_id, token, expected_revision)
    except (KeyError, TimeoutError, ValueError, HTTPException) as exc:
        handle(exc)
