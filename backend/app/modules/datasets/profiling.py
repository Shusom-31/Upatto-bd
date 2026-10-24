import pandas as pd


def profile(frame: pd.DataFrame) -> dict:
    columns = []
    for name in frame.columns:
        series = frame[name]
        numeric = pd.to_numeric(series, errors="coerce")
        dtype = "numeric" if numeric.notna().sum() and numeric.notna().sum() >= series.notna().sum() * 0.8 else "text"
        if dtype == "text" and series.dropna().nunique() < min(20, max(2, len(series) // 2)):
            dtype = "categorical"
        if pd.api.types.is_datetime64_any_dtype(series):
            dtype = "date"
        item = {"name": str(name), "inferred_type": dtype, "missing": int(series.isna().sum()),
                "missing_rate": round(float(series.isna().mean()), 4) if len(series) else 0,
                "unique": int(series.nunique(dropna=True)), "samples": [json_value(x) for x in series.dropna().head(5).tolist()]}
        if dtype == "numeric":
            stats = numeric.describe()
            item["statistics"] = {key: json_value(stats.get(key)) for key in ["count", "min", "max", "mean", "50%", "std"]}
        columns.append(item)
    missing = int(frame.isna().sum().sum())
    total = frame.shape[0] * frame.shape[1]
    return {"rows": len(frame), "columns": len(frame.columns), "missing_cells": missing,
            "missing_rate": missing / total if total else 0, "duplicate_rows": int(frame.duplicated().sum()),
            "columns_with_issues": sum(c["missing"] > 0 for c in columns), "column_profiles": columns}


def json_value(value):
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        value = value.item()
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value
