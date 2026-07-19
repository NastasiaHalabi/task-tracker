# Mini-ADR — Due dates & Tags

## Context
Mid-course project for the Task Tracker. Need two scoped features that are visible in the Kanban UI, backed by API validation/filters, and covered by pytest — without overbuilding persistence.

## Decision

### Feature 1: Due dates + overdue filter
- Store optional `due_date` as a Pydantic `date` (ISO `YYYY-MM-DD`).
- Compute `is_overdue` on the response (`computed_field`): due date before **UTC today** and status ≠ `Done`.
- Expose `GET /tasks?overdue=true|false` for server-side filtering.
- Frontend: date input in the modal, due/overdue pill on cards, “Overdue only” checkbox in the filter bar.

### Feature 2: Tags / labels
- Store `tags` as `list[str]` on the task (max 5 tags, max 30 chars each, trimmed, non-blank).
- Expose `GET /tasks?tag=<name>` with case-insensitive exact match.
- Frontend: comma-separated tags field in the modal, chips on cards, tag filter input above the board.

## Alternatives considered (and rejected)
| Suggestion | Why rejected |
|---|---|
| Client-only overdue calculation | Diverges from API truth; harder to test consistently; filter would be client-side only. |
| Separate `Tag` entity + join table | Too heavy for in-memory storage and course scope. |
| Free-text search across title/description as a third feature | Would expand scope; tags + due dates already cover visible board UX. |
| Storing `is_overdue` as a persisted boolean | Becomes stale at midnight; computed field stays correct. |
| Bulk tag rename / autocomplete | Polish beyond Modules 1–3. |

## Consequences
- Overdue depends on UTC calendar date — tests and UI must use the same clock basis (`utc_today()`).
- Tag filter is exact-match, not substring search — keeps behavior simple and testable.
- Existing create/list/patch/delete contracts remain intact; new fields default safely (`due_date=null`, `tags=[]`).
