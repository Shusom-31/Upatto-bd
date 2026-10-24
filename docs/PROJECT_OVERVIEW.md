# Project overview

## Purpose

Tathyashala helps spreadsheet users understand data quality, preview cleaning changes, create a small set of charts and download the current data. A name personalizes a private guest workspace; it is not an account or identity check.

## First-release scope

The current MVP supports `.csv` and value-based `.xlsx` input, one selected sheet, profiling, paginated previews, missing-value handling, duplicate removal, text cleanup, category mapping, type conversion, row filtering, outlier review, history with Undo/Reset, simple chart data and CSV/XLSX/PDF exports. Initial upload limits default to 20 MB, 100,000 rows, 100 columns, and a 60-minute idle session.

Template generation/validation, ML-safe preprocessing, advanced chart configuration, persistent accounts, cloud history and Google Sheets are future work. The module directories reserve places for those additions.

## Product rules

- Preserve an unchanged original DataFrame as the reset reference.
- Preview an operation before applying it; a successful mutation creates a revision.
- Include the expected revision on mutations and reject stale requests with `409`.
- Retain the last valid revision if an operation fails.
- Do not send the whole dataset to the browser for the table preview.
- Treat detected outliers as review candidates.
- Explain value-based workbook export limits; formulas, macros and workbook styling are not preserved.

## Runtime limits

State currently lives in a process-local registry and expires after inactivity. The backend must run as a single process for this implementation. A process restart discards all open workspaces. Multi-worker deployments need coordinated temporary storage and cleanup.
