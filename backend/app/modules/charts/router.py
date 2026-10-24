from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
import pandas as pd

from app.core.security import require_credential
from app.infrastructure.dataset_store import store

router = APIRouter(prefix="/datasets/{dataset_id}/charts", tags=["charts"])


class ChartRequest(BaseModel):
    kind: str
    x: str
    y: str | None = None
    aggregation: str = "count"
    top_n: int = Field(default=12, ge=1, le=100)
    revision: int


@router.post("")
def chart_data(dataset_id: str, request: ChartRequest, token: str = Depends(require_credential)):
    try:
        _, dataset = store.dataset(dataset_id, token)
        with dataset.mutation_lock:
            if request.revision != dataset.revision:
                raise HTTPException(status_code=409, detail="Dataset changed; refresh before generating the chart")
            revision = dataset.revision
            frame = dataset.current.copy(deep=True)
        if request.x not in frame.columns or (request.y and request.y not in frame.columns):
            raise HTTPException(status_code=400, detail="Choose existing columns")
        if request.kind == "histogram":
            values = pd.to_numeric(frame[request.x], errors="coerce").dropna()
            counts, edges = pd.cut(values, bins=min(20, max(1, values.nunique())), retbins=True)
            grouped = counts.value_counts(sort=False)
            data = [{"label": str(interval), "value": int(count)} for interval, count in grouped.items()]
        elif request.kind == "scatter":
            if not request.y:
                raise HTTPException(status_code=400, detail="Choose a Y column")
            sample = frame[[request.x, request.y]].dropna()
            seed = 42
            if len(sample) > 5000:
                sample = sample.sample(5000, random_state=seed)
            data = [{"x": row[request.x], "y": row[request.y]} for _, row in sample.iterrows()]
            return {"dataset_id": dataset_id, "revision": revision, "kind": request.kind,
                    "data": data, "sample_size": len(data), "seed": seed}
        elif request.kind == "line" and request.y:
            grouped = frame.groupby(request.x, dropna=True)[request.y]
            values = grouped.size() if request.aggregation == "count" else getattr(grouped, request.aggregation)()
            data = [{"label": str(k), "value": json_num(v)} for k, v in values.sort_index().head(500).items()]
        elif request.y:
            grouped = frame.groupby(request.x, dropna=True)[request.y]
            if request.aggregation not in ("sum", "mean", "count"):
                raise HTTPException(status_code=400, detail="Aggregation must be sum, mean, or count")
            values = getattr(grouped, request.aggregation)().sort_values(ascending=False).head(request.top_n)
            data = [{"label": str(k), "value": json_num(v)} for k, v in values.items()]
        else:
            values = frame[request.x].value_counts(dropna=True).head(request.top_n)
            data = [{"label": str(k), "value": int(v)} for k, v in values.items()]
        return {"dataset_id": dataset_id, "revision": revision, "kind": request.kind, "data": data}
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=410, detail="Workspace expired") from exc


def json_num(value):
    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value
