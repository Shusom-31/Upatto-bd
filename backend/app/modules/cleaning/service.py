from typing import Any
import pandas as pd

from app.infrastructure.dataset_store import DatasetState, store
from app.modules.cleaning.operations import category_mapping, data_types, duplicates, filter_rows, missing_values, outliers, text_cleanup


HANDLERS = {"fill_missing": missing_values.apply, "drop_duplicates": duplicates.apply,
            "convert_type": data_types.apply, "outliers": outliers.apply, "text_cleanup": text_cleanup.apply,
            "map_categories": category_mapping.apply, "filter_rows": filter_rows.apply}


def transform(frame: pd.DataFrame, operation: str, columns: list[str], parameters: dict[str, Any]):
    if operation not in HANDLERS:
        raise ValueError(f"Unsupported operation: {operation}")
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"Unknown column(s): {', '.join(missing)}")
    return HANDLERS[operation](frame, columns, parameters)


def apply_operation(dataset_id: str, token: str, payload):
    _, dataset = store.dataset(dataset_id, token)
    with dataset.mutation_lock:
        _check_revision(dataset, payload.expected_revision)
        updated, rows, cells, warnings = transform(dataset.current, payload.operation, payload.columns, payload.parameters)
        dataset.history.append(dataset.current.copy(deep=True))
        dataset.current = updated
        dataset.revision += 1
        record = {"revision": dataset.revision, "operation": payload.operation, "columns": payload.columns,
                  "parameters": payload.parameters, "affected_rows": rows, "affected_cells": cells, "warnings": warnings}
        dataset.operations.append(record)
        preview = updated.head(10).astype(object).where(updated.head(10).notna(), None).to_dict(orient="records")
        return {**record, "preview": preview}


def preview_operation(dataset_id: str, token: str, payload):
    _, dataset = store.dataset(dataset_id, token)
    with dataset.mutation_lock:
        _check_revision(dataset, payload.expected_revision)
        updated, rows, cells, warnings = transform(dataset.current, payload.operation, payload.columns, payload.parameters)
        return {"revision": dataset.revision, "affected_rows": rows, "affected_cells": cells,
                "warnings": warnings, "preview": updated.head(10).astype(object).where(updated.head(10).notna(), None).to_dict(orient="records")}


def history(dataset_id: str, token: str):
    _, dataset = store.dataset(dataset_id, token)
    return {"revision": dataset.revision, "operations": dataset.operations}


def undo(dataset_id: str, token: str, expected_revision: int):
    _, dataset = store.dataset(dataset_id, token)
    with dataset.mutation_lock:
        _check_revision(dataset, expected_revision)
        if not dataset.history:
            raise ValueError("There is no operation to undo")
        dataset.current = dataset.history.pop()
        dataset.revision += 1
        dataset.operations.append({"revision": dataset.revision, "operation": "undo", "affected_rows": 0,
                                   "affected_cells": 0, "warnings": []})
        return {"revision": dataset.revision}


def reset(dataset_id: str, token: str, expected_revision: int):
    _, dataset = store.dataset(dataset_id, token)
    with dataset.mutation_lock:
        _check_revision(dataset, expected_revision)
        dataset.history.append(dataset.current.copy(deep=True))
        dataset.current = dataset.original.copy(deep=True)
        dataset.revision += 1
        dataset.operations.append({"revision": dataset.revision, "operation": "reset", "affected_rows": 0,
                                   "affected_cells": 0, "warnings": []})
        return {"revision": dataset.revision}


def _check_revision(dataset: DatasetState, expected: int):
    if expected != dataset.revision:
        from fastapi import HTTPException
        raise HTTPException(status_code=409, detail=f"Revision conflict. Current revision is {dataset.revision}.")
