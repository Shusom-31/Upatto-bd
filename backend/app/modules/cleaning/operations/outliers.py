import pandas as pd


def apply(frame: pd.DataFrame, columns: list[str], params: dict):
    method = params.get("method", "iqr")
    action = params.get("action", "flag")
    result = frame.copy(deep=True)
    mask = pd.Series(False, index=result.index)
    bounds = {}
    for column in columns:
        values = pd.to_numeric(result[column], errors="coerce")
        if method == "iqr":
            q1, q3 = values.quantile(.25), values.quantile(.75)
            spread = q3 - q1
            lower, upper = q1 - 1.5 * spread, q3 + 1.5 * spread
        elif method == "zscore":
            mean, std = values.mean(), values.std()
            if pd.isna(std) or std == 0:
                continue
            lower, upper = mean - 3 * std, mean + 3 * std
        else:
            raise ValueError("method must be iqr or zscore")
        bounds[column] = (lower, upper)
        mask |= (values < lower) | (values > upper)
    count = int(mask.sum())
    if action == "remove":
        result = result.loc[~mask].copy()
    elif action == "cap":
        for column, (lower, upper) in bounds.items():
            result[column] = pd.to_numeric(result[column], errors="coerce").clip(lower, upper)
    elif action != "flag":
        raise ValueError("action must be flag, remove, or cap")
    if len(result) == 0 or len(result.columns) == 0:
        raise ValueError("This operation would leave the dataset empty")
    return result, count, 0, ["Outliers are review candidates, not necessarily errors"]
