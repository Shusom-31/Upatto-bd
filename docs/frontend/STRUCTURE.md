# Frontend structure

- `src/app`: application entry, provider wrapper and navigation vocabulary.
- `src/layouts`: persistent workspace shell and sidebar.
- `src/features`: welcome/upload, overview, cleaning, charts, exports, and future feature areas.
- `src/components`: shared uploader, table and UI primitives.
- `src/lib/apiClient.ts`: credentialed API calls and download handling.
- `src/types`: shared request and response types.
- `src/styles/globals.css`: responsive visual system.

Feature directories for templates, validation and ML are reserved for later work. The current chart view uses Recharts; tables use server-side 50-row pages.
