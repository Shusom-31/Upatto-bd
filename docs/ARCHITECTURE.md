# Architecture

```text
React + TypeScript browser
   │ X-Workspace-Token, JSON/multipart, paginated rows
   ▼
FastAPI /api/v1 ── session and dataset registry (process-local, TTL)
   │
   ├── Pandas reader and profiler
   ├── serialized cleaning operation → revision/history
   ├── chart aggregates
   └── CSV / OpenPyXL / ReportLab exports
```

The browser owns navigation, forms, previews, chart configuration and downloads. The API owns uploaded data, profiling, transformations, revision checks and export generation. Each workspace has an opaque credential that is required to access its datasets. Dataset IDs alone do not grant access.

`backend/app/infrastructure/dataset_store.py` is intentionally a single-process MVP registry. The cleanup coroutine removes expired workspaces. `DatasetState.original` is immutable by convention and serves Reset; `current`, `history`, `operations`, and `revision` represent the working branch. Mutations should remain serialized per dataset.

The frontend sends an expected revision for preview/apply, Undo, Reset, charts and exports. A stale mutation is rejected with HTTP 409 so the client can refresh. The API currently performs operations inline and has no job queue. Deployment with multiple workers, persistent session state or large asynchronous exports requires a shared store and coordinated worker design.
