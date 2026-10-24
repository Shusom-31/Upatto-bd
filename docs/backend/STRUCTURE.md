# Backend structure

- `app/main.py`: FastAPI app, CORS and router registration.
- `app/core`: environment settings, API error helpers and workspace credential dependency.
- `app/modules/sessions`: temporary guest session lifecycle.
- `app/modules/datasets`: upload parsing, header normalization, profiling and row paging.
- `app/modules/cleaning`: request schema, operation preview/apply, revision history, undo and reset.
- `app/modules/charts`: revision-scoped aggregate endpoints.
- `app/modules/exports`: CSV, XLSX and PDF response generation.
- `app/modules/templates`, `validation`, `ml`: future extension points from the product blueprint.
- `app/infrastructure`: process-local dataset registry, temporary path helper and TTL cleanup loop.
- `app/shared`: reusable pagination schema and dependencies.
- `tests`: reserved for dataset, cleaning, template and ML test suites.

The process-local registry is an MVP implementation, not multi-worker storage.
