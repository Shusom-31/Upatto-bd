from io import BytesIO
from pathlib import Path

import pandas as pd
from fastapi import HTTPException, UploadFile

from app.core.config import settings


async def read_upload(file: UploadFile, sheet_name: str | None = None, delimiter: str = ",", encoding: str = "utf-8") -> tuple[pd.DataFrame, list[str]]:
    suffix = Path(file.filename or "").suffix.lower()
    raw = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(raw) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds the {settings.max_upload_mb} MB limit")
    try:
        if suffix == ".csv":
            # Read strings first so CSV identifiers such as 00124 retain leading zeros.
            frame = pd.read_csv(BytesIO(raw), sep=delimiter, encoding=encoding, dtype=str)
            for column in frame.columns:
                if is_identifier(str(column)):
                    continue
                numeric = pd.to_numeric(frame[column], errors="coerce")
                populated = frame[column].notna().sum()
                if populated and numeric.notna().sum() == populated:
                    frame[column] = numeric
            sheets: list[str] = []
        elif suffix == ".xlsx":
            book = pd.ExcelFile(BytesIO(raw), engine="openpyxl")
            sheets = book.sheet_names
            selected = sheet_name or (sheets[0] if sheets else None)
            if not selected or selected not in sheets:
                raise ValueError("Select a worksheet from the uploaded workbook")
            frame = pd.read_excel(book, sheet_name=selected)
        else:
            raise ValueError("Only .csv and .xlsx files are supported")
    except (UnicodeDecodeError, pd.errors.ParserError, ValueError) as exc:
        raise ValueError(f"Could not read this file: {exc}") from exc
    except Exception as exc:
        raise ValueError("Could not read this file. It may be corrupt, encrypted, or unsupported.") from exc
    if frame.empty and len(frame.columns) == 0:
        raise ValueError("The selected file has no tabular data")
    frame.columns = unique_headers(frame.columns)
    if len(frame) > settings.max_rows or len(frame.columns) > settings.max_columns:
        raise ValueError(f"File exceeds the {settings.max_rows} row or {settings.max_columns} column limit")
    return frame, sheets


async def inspect_sheets(file: UploadFile) -> list[str]:
    suffix = Path(file.filename or "").suffix.lower()
    raw = await file.read(settings.max_upload_mb * 1024 * 1024 + 1)
    if len(raw) > settings.max_upload_mb * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"File exceeds the {settings.max_upload_mb} MB limit")
    if suffix != ".xlsx":
        if suffix != ".csv":
            raise ValueError("Only .csv and .xlsx files are supported")
        return []
    try:
        return pd.ExcelFile(BytesIO(raw), engine="openpyxl").sheet_names
    except Exception as exc:
        raise ValueError(f"Could not read this workbook: {exc}") from exc


def unique_headers(columns) -> list[str]:
    result: list[str] = []
    used: set[str] = set()
    for index, value in enumerate(columns, 1):
        base = str(value).strip() or f"Column {index}"
        name, suffix = base, 2
        while name in used:
            name = f"{base} ({suffix})"
            suffix += 1
        result.append(name)
        used.add(name)
    return result


def is_identifier(name: str) -> bool:
    normalized = "".join(character.lower() for character in name if character.isalnum())
    return normalized.endswith(("id", "phone", "mobile", "code", "zipcode", "postal")) or normalized.startswith(("phone", "mobile", "zipcode", "postal"))
