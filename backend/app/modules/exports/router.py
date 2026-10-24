from io import BytesIO
from datetime import datetime, timezone
import csv

import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from app.core.security import require_credential
from app.infrastructure.dataset_store import store

router = APIRouter(prefix="/datasets/{dataset_id}/exports", tags=["exports"])


class ExportRequest(BaseModel):
    format: str
    revision: int
    include_log: bool = True


@router.post("")
def export_dataset(dataset_id: str, request: ExportRequest, token: str = Depends(require_credential)):
    try:
        workspace, dataset = store.dataset(dataset_id, token)
        with dataset.mutation_lock:
            if request.revision != dataset.revision:
                raise HTTPException(status_code=409, detail="Dataset changed; refresh before exporting")
            revision = dataset.revision
            operations = list(dataset.operations)
            frame = dataset.current.copy(deep=True)
        filename = safe_filename(dataset.name)
        if request.format == "csv":
            text = safe_for_csv(frame).to_csv(index=False, quoting=csv.QUOTE_MINIMAL, escapechar="\\")
            return StreamingResponse(iter([text.encode("utf-8-sig")]), media_type="text/csv; charset=utf-8",
                                     headers={"Content-Disposition": f'attachment; filename="{filename}.csv"'})
        if request.format == "xlsx":
            output = BytesIO()
            with pd.ExcelWriter(output, engine="openpyxl") as writer:
                safe_for_excel(frame).to_excel(writer, sheet_name="Cleaned Data", index=False)
                pd.DataFrame([{ "name": workspace.display_name, "dataset": dataset.name, "revision": revision,
                                "generated_at": datetime.now(timezone.utc).isoformat(), "rows": len(frame), "columns": len(frame.columns),
                                "missing_cells": int(frame.isna().sum().sum()), "duplicate_rows": int(frame.duplicated().sum()) }]).to_excel(writer, sheet_name="Summary", index=False)
                if request.include_log and operations:
                    pd.DataFrame(operations).to_excel(writer, sheet_name="Cleaning Log", index=False)
            output.seek(0)
            return StreamingResponse(output, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                     headers={"Content-Disposition": f'attachment; filename="{filename}-cleaned.xlsx"'})
        if request.format == "pdf":
            try:
                from reportlab.lib import colors
                from reportlab.lib.pagesizes import letter
                from reportlab.lib.styles import getSampleStyleSheet
                from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            except ImportError as exc:
                raise HTTPException(status_code=501, detail="PDF export dependencies are not installed") from exc
            output = BytesIO()
            doc = SimpleDocTemplate(output, pagesize=letter)
            styles = getSampleStyleSheet()
            story = [Paragraph("Tathyashala dataset report", styles["Title"]),
                     Paragraph(f"{dataset.name} · revision {revision}", styles["Heading2"]),
                     Paragraph(f"Prepared for {workspace.display_name} · {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}", styles["Normal"]),
                     Spacer(1, 14)]
            summary = [["Rows", "Columns", "Missing cells", "Duplicate rows"], [len(frame), len(frame.columns), int(frame.isna().sum().sum()), int(frame.duplicated().sum())]]
            table = Table(summary)
            table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f0eb")), ("GRID", (0, 0), (-1, -1), .5, colors.grey), ("PADDING", (0, 0), (-1, -1), 7)]))
            story += [table, Spacer(1, 14), Paragraph("Cleaning history", styles["Heading2"])]
            logs = [["Revision", "Operation", "Rows", "Cells"]] + [[str(o.get("revision", "")), str(o.get("operation", "")), str(o.get("affected_rows", 0)), str(o.get("affected_cells", 0))] for o in operations]
            if len(logs) == 1:
                logs.append([str(revision), "No changes", "0", "0"])
            log_table = Table(logs, repeatRows=1)
            log_table.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e8f0eb")), ("GRID", (0, 0), (-1, -1), .4, colors.grey), ("PADDING", (0, 0), (-1, -1), 5)]))
            story.append(log_table)
            story.append(Spacer(1, 12))
            story.append(Paragraph("This report summarizes the current value-based dataset revision. Original workbook formulas, macros, styles and layout are not preserved.", styles["BodyText"]))
            doc.build(story)
            output.seek(0)
            return StreamingResponse(output, media_type="application/pdf",
                                     headers={"Content-Disposition": f'attachment; filename="{filename}-report.pdf"'})
        raise HTTPException(status_code=400, detail="format must be csv, xlsx, or pdf")
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=410, detail="Workspace expired") from exc


def safe_filename(name: str) -> str:
    import re
    return re.sub(r"[^A-Za-z0-9_-]+", "-", name.rsplit(".", 1)[0]).strip("-") or "dataset"


def safe_for_excel(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    for column in result.select_dtypes(include=["object", "string"]).columns:
        result[column] = result[column].map(lambda value: "'" + value if isinstance(value, str) and value[:1] in "=+-@\t\r" else value)
    return result


def safe_for_csv(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy()
    dangerous = ("=", "+", "-", "@", "\t", "\r")
    for column in result.select_dtypes(include=["object", "string"]).columns:
        result[column] = result[column].map(lambda value: "'" + value if isinstance(value, str) and value.startswith(dangerous) else value)
    return result
