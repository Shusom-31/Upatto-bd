import pandas as pd


def apply(frame: pd.DataFrame, columns: list[str], params: dict):
    mapping = params.get("mapping", {})
    if not isinstance(mapping, dict) or not mapping:
        raise ValueError("Provide a non-empty value mapping")
    result = frame.copy(deep=True)
    changed = 0
    affected_rows = pd.Series(False, index=result.index)
    for column in columns:
        before = result[column]
        result[column] = before.replace(mapping)
        changed_mask = before.astype("string").fillna("<NA>") != result[column].astype("string").fillna("<NA>")
        changed += int(changed_mask.sum())
        affected_rows |= changed_mask
    return result, int(affected_rows.sum()), changed, []
