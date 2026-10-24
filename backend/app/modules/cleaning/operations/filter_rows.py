import pandas as pd


def apply(frame: pd.DataFrame, columns: list[str], params: dict):
    if len(columns) != 1:
        raise ValueError("Choose exactly one column to filter")
    column = columns[0]
    operator = params.get("operator", "eq")
    value = params.get("value", "")
    series = frame[column]
    if operator in ("gt", "gte", "lt", "lte"):
        numeric = pd.to_numeric(series, errors="coerce")
        number = pd.to_numeric(value, errors="coerce")
        if pd.isna(number):
            raise ValueError("Enter a number for this filter")
        mask = {"gt": numeric > number, "gte": numeric >= number, "lt": numeric < number, "lte": numeric <= number}[operator]
    elif operator == "eq":
        mask = series.astype("string") == str(value)
    elif operator == "neq":
        mask = series.astype("string") != str(value)
    elif operator == "contains":
        mask = series.astype("string").str.contains(str(value), regex=False, na=False)
    elif operator == "empty":
        mask = series.isna() | (series.astype("string").str.strip() == "")
    elif operator == "not_empty":
        mask = series.notna() & (series.astype("string").str.strip() != "")
    else:
        raise ValueError("Unsupported filter comparison")
    result = frame.loc[mask.fillna(False)].copy()
    removed = len(frame) - len(result)
    if len(result) == 0 or len(result.columns) == 0:
        raise ValueError("This filter would leave the dataset empty")
    return result, removed, 0, []
