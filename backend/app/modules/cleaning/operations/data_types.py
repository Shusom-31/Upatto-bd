import pandas as pd


def apply(frame: pd.DataFrame, columns: list[str], params: dict):
    target = params.get("target", "number")
    result = frame.copy(deep=True)
    failed = 0
    cells = 0
    affected_rows = pd.Series(False, index=result.index)
    for column in columns:
        before = result[column]
        if target == "number":
            converted = pd.to_numeric(before, errors="coerce")
        elif target == "date":
            converted = pd.to_datetime(before, errors="coerce", format=params.get("format"))
        elif target == "text":
            converted = before.astype("string")
        else:
            raise ValueError("target must be number, date, or text")
        failed += int((before.notna() & converted.isna()).sum())
        changed_mask = before.astype("string").fillna("<NA>") != converted.astype("string").fillna("<NA>")
        cells += int(changed_mask.sum())
        affected_rows |= changed_mask
        result[column] = converted
    warnings = [f"{failed} non-empty values could not be converted and became empty"] if failed else []
    return result, int(affected_rows.sum()), cells, warnings
