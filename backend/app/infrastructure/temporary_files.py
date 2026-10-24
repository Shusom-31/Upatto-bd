from pathlib import Path
from uuid import uuid4

from app.core.config import settings


def temp_path(suffix: str) -> Path:
    root = Path(settings.temporary_directory)
    root.mkdir(parents=True, exist_ok=True)
    return root / f"{uuid4().hex}{suffix}"
