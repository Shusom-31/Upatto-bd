"""Temporary in-process workspace registry for the single-process MVP."""

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from threading import RLock
from typing import Any
from uuid import uuid4

import pandas as pd

from app.core.config import settings


@dataclass
class DatasetState:
    dataset_id: str
    name: str
    original: pd.DataFrame
    current: pd.DataFrame
    revision: int = 0
    history: list[dict[str, Any]] = field(default_factory=list)
    operations: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    mutation_lock: RLock = field(default_factory=RLock, repr=False)


@dataclass
class Workspace:
    session_id: str
    token: str
    display_name: str
    last_activity: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    datasets: dict[str, DatasetState] = field(default_factory=dict)


class DatasetStore:
    def __init__(self) -> None:
        self._workspaces: dict[str, Workspace] = {}
        self._lock = RLock()

    def create(self, display_name: str, token: str) -> Workspace:
        workspace = Workspace(str(uuid4()), token, display_name.strip())
        with self._lock:
            self._workspaces[workspace.session_id] = workspace
        return workspace

    def workspace(self, session_id: str, token: str) -> Workspace:
        with self._lock:
            workspace = self._workspaces.get(session_id)
            if workspace is None or not secrets_equal(workspace.token, token):
                raise KeyError("Workspace not found")
            if datetime.now(timezone.utc) - workspace.last_activity > timedelta(minutes=settings.session_ttl_minutes):
                self._workspaces.pop(session_id, None)
                raise TimeoutError("Workspace expired")
            workspace.last_activity = datetime.now(timezone.utc)
            return workspace

    def dataset(self, dataset_id: str, token: str) -> tuple[Workspace, DatasetState]:
        with self._lock:
            for workspace in self._workspaces.values():
                if secrets_equal(workspace.token, token) and dataset_id in workspace.datasets:
                    return self.workspace(workspace.session_id, token), workspace.datasets[dataset_id]
        raise KeyError("Dataset not found")

    def add_dataset(self, workspace: Workspace, name: str, frame: pd.DataFrame) -> DatasetState:
        state = DatasetState(str(uuid4()), name, frame.copy(deep=True), frame.copy(deep=True))
        with self._lock:
            workspace.datasets[state.dataset_id] = state
        return state

    def delete(self, session_id: str, token: str) -> None:
        self.workspace(session_id, token)
        with self._lock:
            self._workspaces.pop(session_id, None)

    def cleanup(self) -> None:
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=settings.session_ttl_minutes)
        with self._lock:
            expired = [sid for sid, ws in self._workspaces.items() if ws.last_activity < cutoff]
            for sid in expired:
                self._workspaces.pop(sid, None)


def secrets_equal(left: str, right: str) -> bool:
    import hmac
    return hmac.compare_digest(left, right)


store = DatasetStore()
