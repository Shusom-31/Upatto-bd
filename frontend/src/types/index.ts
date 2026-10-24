export type Session = { session_id: string; display_name: string; token: string; expires_in_minutes: number }
export type Dataset = { dataset_id: string; dataset_name: string; revision: number; rows: number; columns: number; sheets: string[] }
export type ColumnProfile = { name: string; inferred_type: string; missing: number; missing_rate: number; unique: number; samples: unknown[]; statistics?: Record<string, unknown> }
export type Profile = { dataset_id: string; dataset_name: string; revision: number; rows: number; columns: number; missing_cells: number; missing_rate: number; duplicate_rows: number; columns_with_issues: number; column_profiles: ColumnProfile[] }
export type RowPage = { revision: number; page: number; page_size: number; total_rows: number; columns: string[]; rows: Record<string, unknown>[] }
export type Operation = { operation: string; columns: string[]; parameters: Record<string, unknown>; expected_revision: number }
export type OperationResult = { revision: number; affected_rows: number; affected_cells: number; warnings: string[]; preview: Record<string, unknown>[] }
