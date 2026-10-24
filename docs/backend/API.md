# API reference

Base path: `/api/v1`. Protected routes require `X-Workspace-Token`, returned at session creation. Use TLS outside local development. JSON error bodies use `{ "detail": "..." }`.

| Method | Path | Purpose |
|---|---|---|
| `POST` | `/sessions` | Create a guest workspace: `{ "display_name": "Name" }`. Returns `session_id`, credential token and TTL. |
| `DELETE` | `/sessions/{sid}` | End the workspace and remove its datasets. |
| `POST` | `/sessions/{sid}/datasets/inspect` | Multipart `file`; return available XLSX worksheet names without creating a dataset. |
| `POST` | `/sessions/{sid}/datasets` | Multipart `file`; optional `sheet_name`, `delimiter`, `encoding`. Returns `dataset_id` and worksheet names. |
| `GET` | `/datasets/{did}/profile` | Current revision, overview metrics and per-column profile. |
| `GET` | `/datasets/{did}/rows?page=1&page_size=50&revision=N` | Paginated preview. Optional revision check. |
| `POST` | `/datasets/{did}/operations/preview` | Preview an operation without mutating current state. |
| `POST` | `/datasets/{did}/operations` | Apply operation with `expected_revision`. |
| `GET` | `/datasets/{did}/history` | List operations and current revision. |
| `POST` | `/datasets/{did}/undo?expected_revision=N` | Restore the preceding snapshot and create a new revision. |
| `POST` | `/datasets/{did}/reset?expected_revision=N` | Restore the original upload and create a new revision. |
| `POST` | `/datasets/{did}/charts` | Return revision-scoped chart aggregates. |
| `POST` | `/datasets/{did}/exports` | Stream `csv`, `xlsx`, or `pdf` for a requested revision. |

## Operation body

```json
{
  "operation": "fill_missing",
  "columns": ["Age"],
  "parameters": {"strategy": "median"},
  "expected_revision": 0
}
```

Implemented operations: `fill_missing` (`mean`, `median`, `mode`, `custom`, `drop_rows`, `drop_columns`), `drop_duplicates` (`keep`: `first`, `last`, or `all`), `text_cleanup` (`trim`, `collapse_spaces`, `lower`, `upper`, `replace`), `map_categories` (a literal old-value to new-value mapping), `filter_rows` (`eq`, `neq`, `contains`, numeric comparisons, `empty`, `not_empty`), `convert_type` (`number`, `date`, `text`) and `outliers` (`iqr` or `zscore`; `flag`, `remove`, `cap`).

Errors: `400` invalid input/configuration or unsupported file, `401` missing credential, `404` unknown session/dataset, `409` stale revision, `410` expired workspace, `413` upload exceeds the byte limit, and `422` request schema validation. Row/column limit violations currently return `400`. Processing is synchronous in the MVP; job endpoints are not implemented.

Template, dataset validation, schema update, ML preparation and Google Sheets routes in the source PDF remain future API work.
