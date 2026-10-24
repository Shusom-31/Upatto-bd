import pandas as pd


def apply(frame: pd.DataFrame, columns: list[str], params: dict):
    subset = columns or None
    keep = params.get("keep", "first")
    duplicates = frame.duplicated(subset=subset, keep=False)
    if keep == "all":
        result = frame.loc[~duplicates].copy()
    elif keep in ("first", "last"):
        result = frame.drop_duplicates(subset=subset, keep=keep).copy()
    else:
        raise ValueError("keep must be first, last, or all")
    rows = len(frame) - len(result)
    if len(result) == 0 or len(result.columns) == 0:
        raise ValueError("This operation would leave the dataset empty")
    return result, rows, 0, []
