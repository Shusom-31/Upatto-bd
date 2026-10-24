import re
import pandas as pd


def apply(frame: pd.DataFrame, columns: list[str], params: dict):
    result = frame.copy(deep=True)
    action = params.get("action", "trim")
    changed = 0
    affected_rows = pd.Series(False, index=result.index)
    for column in columns:
        before = result[column]
        values = before.astype("string")
        if action == "trim":
            after = values.str.strip()
        elif action == "collapse_spaces":
            after = values.str.replace(r"\s+", " ", regex=True).str.strip()
        elif action == "lower":
            after = values.str.lower()
        elif action == "upper":
            after = values.str.upper()
        elif action == "replace":
            old, new = str(params.get("old", "")), str(params.get("new", ""))
            if not old:
                raise ValueError("Provide text to find")
            after = values.str.replace(old, new, regex=False)
        else:
            raise ValueError("Unknown text cleanup action")
        changed_mask = values.fillna("<NA>") != after.fillna("<NA>")
        changed += int(changed_mask.sum())
        affected_rows |= changed_mask
        result[column] = after
    return result, int(affected_rows.sum()), changed, []
