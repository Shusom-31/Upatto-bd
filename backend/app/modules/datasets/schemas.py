from pydantic import BaseModel


class UploadResponse(BaseModel):
    dataset_id: str
    dataset_name: str
    revision: int
    rows: int
    columns: int
    sheets: list[str] = []
