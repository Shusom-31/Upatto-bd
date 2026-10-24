# Processing notes

## Import and profile

CSV and XLSX bytes are read in memory; formulas are not executed. XLSX import uses one selected sheet, defaulting to the first sheet. Empty headers become `Column N`; repeated headers receive a numeric suffix. The current parser reads the full file into Pandas for processing, but the browser receives only requested preview pages. Limits are configurable.

The profile reports rows, columns, missing cells/rate, duplicate rows, issue count, per-column missing/unique counts, sample values, a simple inferred type and numeric summary. Inference is heuristic and should not be treated as schema validation.

## Mutation model

Every operation works on a deep copy of the current DataFrame. Preview returns a sample and impact counts without committing it. Apply checks the expected revision, computes the full result, and only then appends the old state and advances the revision. Failed transforms leave the current state intact. Undo restores the last snapshot; Reset copies the original reference. This implementation uses in-memory snapshots rather than recipe replay/checkpoints.

## Export and privacy

CSV is UTF-8 with BOM. Excel is a value-based workbook with Cleaned Data, Summary, and optional Cleaning Log sheets. Text cells with spreadsheet formula prefixes are escaped in XLSX. PDF contains metadata, basic quality counts and operation history; it currently does not render selected charts or embed a Bengali shaping font. These limits are shown in the interface/documentation. Output formatting, macros, formulas and arbitrary workbook layout are not preserved.

The session TTL cleaner drops expired in-memory workspaces. Restarting the process also removes them. Production needs a shared temporary store, coordinated cleanup, request-level resource controls and protected credential transport.
