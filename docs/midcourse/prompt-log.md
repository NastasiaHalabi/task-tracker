# Prompt Log — Mid-Course Project

AI tools used: Cursor Agent (Composer) for planning, implementation, tests, and docs review.

---

## Feature 1: Due dates + overdue filter

### Prompt 1 (weak → rewritten)

**Weak prompt:**  
> Add due dates to tasks.

**Stronger prompt:**  
> Add optional `due_date` (ISO date) to TaskCreate/TaskUpdate/TaskResponse. Validate invalid formats with 422. Compute `is_overdue` when due_date is before today UTC and status is not Done. Support `GET /tasks?overdue=true`. Keep the change small — no new tables.

**AI returned:** Model field sketches, filter query param, and a suggestion to store overdue as a boolean column.  
**Accepted:** Optional `date` fields + query filter + computed `is_overdue`.  
**Rejected:** Persisted overdue boolean; free-form string dates.

### Prompt 2
> Write pytest coverage for valid due date, invalid format, overdue detection including Done exclusion, update due date, and overdue filter returning only matches.

**AI returned:** A consolidated test module covering those cases.  
**Accepted:** Structure and assertions.  
**Edited:** Switched `date.today()` to `utc_today()` after a timezone mismatch showed up during manual checks (local UTC+3 vs UTC date).

### Prompt 3
> Wire due date into the existing modal and cards: date input, due/overdue pill, overdue filter checkbox that hits the API. Do not redesign the board layout.

**AI returned:** Modal field + filter bar + card pill markup/JS.  
**Accepted:** Integration approach and escapeHtml usage for text.  
**Edited:** Kept existing card/meta layout; avoided extra dashboard chrome.

---

## Feature 2: Tags / labels

### Prompt 1 (weak → rewritten)

**Weak prompt:**  
> Can you add tags somehow?

**Stronger prompt:**  
> Add `tags: list[str]` to create/update/response. Validate: trim each tag, reject blank tags, max 5 tags, max 30 chars each. Support `GET /tasks?tag=` with case-insensitive exact match. Preserve tags when PATCH omits the field. No separate Tag model.

**AI returned:** List field + validators + filter logic; also offered a Tag table design.  
**Accepted:** In-memory list + validators + filter.  
**Rejected:** Normalized Tag entity / dedicated tag CRUD endpoints.

### Prompt 2
> Add frontend tags as comma-separated modal input, chip row on cards, and a tag filter input that calls `GET /tasks?tag=`. Keep columns visible on empty filter results.

**AI returned:** `parseTagsInput`, chips, filter wiring.  
**Accepted:** Most of the JS.  
**Edited:** Ensured knownFields includes `tags` for 422 mapping; empty client-side tokens are dropped before POST (API still rejects blank tags if sent).

### Prompt 3
> After implementation, extract shared overdue helpers and confirm PATCH without tags leaves tags unchanged. Add tests for create/trim, reject empty tag, update+filter, and preserve-on-unrelated-update.

**AI returned:** `utc_today` / `compute_is_overdue` helpers and preserve-tags test.  
**Accepted:** Refactor and tests as written.  
**Rejected:** Extra endpoints for listing all distinct tags (out of scope).
