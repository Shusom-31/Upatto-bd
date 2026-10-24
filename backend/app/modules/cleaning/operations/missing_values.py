import pandas as pd


def apply(frame: pd.DataFrame, columns: list[str], params: dict) -> tuple[pd.DataFrame, int, int, list[str]]:
    strategy = params.get("strategy", "median")
    result = frame.copy(deep=True)
    selected = columns or list(result.columns)
    missing = result[selected].isna()
    cells = int(missing.sum().sum())
    rows = int(missing.any(axis=1).sum())
    warnings: list[str] = []
    if strategy == "drop_rows":
        result = result.dropna(subset=selected)
    elif strategy == "drop_columns":
        result = result.drop(columns=selected)
    else:
        for column in selected:
            series = result[column]
            if strategy == "custom":
                value = params.get("value")
            elif strategy in ("mean", "median"):
                numeric = pd.to_numeric(series, errors="coerce")
                if numeric.notna().empty or numeric.notna().sum() == 0:
                    warnings.append(f"{column} has no valid numeric values; use a custom value or remove the column")
                    continue
                if series.isna().sum() == len(series):
                    warnings.append(f"{column} is entirely empty; {strategy} fill was skipped")
                    continue
                value = numeric.mean() if strategy == "mean" else numeric.median()
            elif strategy == "mode":
                modes = series.mode(dropna=True)
                if modes.empty:
                    warnings.append(f"{column} has no value to use as mode")
                    continue
                value = modes.iloc[0]
            else:
                raise ValueError("Unknown missing-value strategy")
            result[column] = result[column].fillna(value)
    if len(result) == 0 or len(result.columns) == 0:
        raise ValueError("This operation would leave the dataset empty")
    return result, rows, cells, warnings
