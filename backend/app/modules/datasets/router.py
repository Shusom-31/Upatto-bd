from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile

from app.core.config import settings
from app.core.security import require_credential
from app.infrastructure.dataset_store import store
from app.modules.datasets.reader import inspect_sheets, read_upload
from app.modules.datasets.schemas import UploadResponse
from app.modules.datasets.service import get_profile, get_rows

router = APIRouter(tags=["datasets"])


def _error(exc: Exception):
    if isinstance(exc, TimeoutError):
        raise HTTPException(status_code=410, detail="Workspace expired") from exc
    if isinstance(exc, KeyError):
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    if isinstance(exc, ValueError):
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/sessions/{session_id}/datasets/inspect")
async def inspect_dataset(session_id: str, file: UploadFile = File(...), token: str = Depends(require_credential)):
    try:
        store.workspace(session_id, token)
        return {"sheets": await inspect_sheets(file)}
    except (TimeoutError, KeyError, ValueError) as exc:
        _error(exc)


@router.post("/sessions/{session_id}/datasets", response_model=UploadResponse, status_code=201)
async def upload_dataset(session_id: str, file: UploadFile = File(...), sheet_name: str | None = Form(None),
                         delimiter: str = Form(","), encoding: str = Form("utf-8"), token: str = Depends(require_credential)):
    try:
        workspace = store.workspace(session_id, token)
        frame, sheets = await read_upload(file, sheet_name, delimiter, encoding)
        dataset = store.add_dataset(workspace, file.filename or "dataset", frame)
        return UploadResponse(dataset_id=dataset.dataset_id, dataset_name=dataset.name, revision=0,
                              rows=len(frame), columns=len(frame.columns), sheets=sheets)
    except (TimeoutError, KeyError, ValueError) as exc:
        _error(exc)


@router.get("/datasets/{dataset_id}/profile")
def dataset_profile(dataset_id: str, token: str = Depends(require_credential)):
    try:
        return get_profile(dataset_id, token)
    except (TimeoutError, KeyError, ValueError) as exc:
        _error(exc)


@router.get("/datasets/{dataset_id}/rows")
def dataset_rows(dataset_id: str, page: int = Query(1, ge=1), page_size: int = Query(50, ge=1, le=500),
                 revision: int | None = None, token: str = Depends(require_credential)):
    try:
        return get_rows(dataset_id, token, page, page_size, revision)
    except (TimeoutError, KeyError, ValueError) as exc:
        _error(exc)
