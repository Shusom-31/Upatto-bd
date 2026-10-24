from app.infrastructure.dataset_store import store
from app.modules.datasets.profiling import profile


def get_profile(dataset_id: str, token: str):
    _, dataset = store.dataset(dataset_id, token)
    return {"dataset_id": dataset_id, "dataset_name": dataset.name, "revision": dataset.revision,
            **profile(dataset.current)}


def get_rows(dataset_id: str, token: str, page: int, page_size: int, revision: int | None):
    _, dataset = store.dataset(dataset_id, token)
    if revision is not None and revision != dataset.revision:
        raise ValueError("Requested revision is no longer current; refresh the preview")
    start = (page - 1) * page_size
    frame = dataset.current.iloc[start:start + page_size]
    rows = frame.astype(object).where(frame.notna(), None).to_dict(orient="records")
    return {"dataset_id": dataset_id, "revision": dataset.revision, "page": page, "page_size": page_size,
            "total_rows": len(dataset.current), "columns": [str(c) for c in frame.columns], "rows": rows}
