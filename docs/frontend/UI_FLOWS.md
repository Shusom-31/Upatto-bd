# UI flows

1. **Welcome:** collect a display name and create a guest session.
2. **Upload:** choose or drop CSV/XLSX. The workbook's sheet list is presented for selection; the API validates file size, shape and readable content.
3. **Overview:** show quality cards, inferred column profiles and a 50-row paginated table.
4. **Clean data:** select an operation and column, request a preview, then Apply. The API returns a new revision. History supports Undo and Reset.
5. **Charts:** choose a basic category count, numeric histogram or scatter plot and view server-produced aggregates for the current revision.
6. **Export:** download CSV, value-based Excel with summary/log sheets, or a compact PDF summary.
7. **End workspace:** remove temporary session state from the API and clear the browser credential.

The upload does not expose the full dataset to the browser. The guest credential is held in browser session storage for this MVP; deployments should prefer an appropriately protected HttpOnly cookie or equivalent transport and serve over HTTPS.
