# Backend business logic

This document describes the rules the current API applies to a guest workspace. The uploaded workbook is treated as tabular values. The service does not execute formulas or preserve workbook layout.

## Workspace and ownership

1. The client sends a display name to `POST /api/v1/sessions`.
2. The service creates an opaque workspace ID and a random workspace credential.
3. Protected requests send that credential in `X-Workspace-Token`. A session ID or dataset ID by itself does not grant access.
4. Every access refreshes the workspace's last activity. After the configured idle TTL (60 minutes by default), the workspace is unavailable and cleanup removes its in-memory data.
5. End Session deletes the workspace and its datasets immediately.

The name is a greeting label, not proof of identity. The MVP stores state in process memory, so a process restart also ends every workspace.

## Upload and dataset identity

- Accept `.csv` and `.xlsx` only; limit file bytes, rows and columns using environment settings.
- For XLSX, inspect worksheet names and let the client select one. If none is sent, use the first sheet.
- CSV import accepts delimiter and encoding parameters. The UI currently sends defaults; the API can accept overrides.
- Read CSV columns as strings first so identifier-like headers (`id`, `phone`, `code`, etc.) retain leading zeros. Other columns are converted to numbers only when all populated values parse cleanly.
- Normalize blank headers to `Column N` and make repeated names unique before storing the frame.
- Keep a deep copy of the parsed frame as the original/reset reference. Create a separate working copy at revision `0`.

## Profiling and preview

The API computes summary metrics across the current full frame: row/column counts, missing cells and rate, duplicate row count, and columns with missing values. Missing rate is `missing cells / (rows × columns)`, or zero for a zero-cell dataset. Column profiles include an inferred type, missing count/rate, unique count, up to five samples and numeric summary values when applicable.

Type inference is a convenience heuristic, not a validated schema. The table endpoint returns only one requested page (50 rows by default), rather than sending the full frame to the browser.

## Cleaning operations

All operations accept selected columns (an empty list means all columns for operations that allow it), a parameter object and `expected_revision`.

| Operation | Current behavior |
|---|---|
| `fill_missing` | Fill with numeric mean/median, first sorted mode, or a custom value; alternatively drop rows with selected missing values or drop selected columns. Entirely missing columns are not mean/median filled. |
| `drop_duplicates` | Compare selected columns or all columns. Keep first/last, or remove every row in a duplicate group with `keep: all`. |
| `text_cleanup` | Trim, collapse whitespace, lowercase, uppercase, or perform literal replacement. |
| `map_categories` | Replace literal values using a caller supplied mapping. |
| `convert_type` | Convert selected values to number, date, or text. Unparseable non-empty values become missing and are reported in warnings. |
| `filter_rows` | Keep rows that match a single-column comparison (`eq`, `neq`, `contains`, `gt`, `gte`, `lt`, `lte`, `empty`, or `not_empty`). |
| `outliers` | Detect with IQR or a three-standard-deviation Z-score threshold; flag, cap, or remove affected rows. A flag operation records a revision but leaves values unchanged. |

Each operation is run against a deep copy. Preview calculates full-dataset impact counts and returns up to ten result rows without committing. Apply checks the expected revision, completes the transformation, then appends the previous state to history and increments the revision. A failed transform does not replace the current frame. An operation that would leave zero rows or zero columns is rejected.

## Revisions, Undo and Reset

- Revisions increase after Apply, Undo and Reset; revisions are not reused.
- Mutations are guarded by a per-dataset lock and compare `expected_revision` under that lock.
- A stale request returns `409 Conflict`; the caller must refresh before retrying.
- Undo restores the last saved frame snapshot. It does not decrement the revision.
- Reset restores the original upload as a new revision and keeps the operation history.
- Charts and exports are generated for a requested current revision, so stale requests are rejected.

## Charts and exports

Chart requests return numeric aggregate data for the browser. Category charts limit output to Top N (default 12); scatter charts sample at most 5,000 complete points with seed 42. The current API supports category counts/grouping, histograms, scatter samples and grouped lines, but does not yet persist chart specifications or embed selected charts in PDF reports.

Exports snapshot the requested current revision before generation:

- CSV: UTF-8 with BOM and formula-like text escaped.
- XLSX: value-based `Cleaned Data`, `Summary`, and optional `Cleaning Log` sheets; formula-like text cells are escaped.
- PDF: metadata, basic quality counts and cleaning history. The MVP PDF does not include selected charts or bundled Bengali fonts.

Original formulas, macros, styles, external links and arbitrary workbook layout are not guaranteed in output.

## Future business rules

The PDF blueprint's ML preparation, template generation/import, completed-file validation, schema updates and Google Sheets integration are planned extensions. In particular, a future ML-safe branch must split before fitting imputers, scalers and encoders, and must never impute the target using the feature imputer. Those rules are not implemented by the current API.
