# User Stories — Mid-Course Project

Selected features: **Due dates + overdue filter** and **Tags / labels**.

---

## Feature 1: Due dates + overdue filter

### US-D1 — Set a due date when creating a task
**As a** board user  
**I want** to optionally set a due date on a new task  
**So that** I can track when work should be finished.

**Acceptance criteria**
- Modal includes an optional due-date field (`type="date"`).
- Valid ISO date (`YYYY-MM-DD`) is stored and returned by the API.
- Omitting due date stores `null`.
- Invalid date format returns HTTP 422.

**AI assumption corrected:** AI first suggested storing due dates as free-form strings and computing overdue only in the browser. Corrected to `Optional[date]` validated by Pydantic so invalid formats fail at the API boundary.

### US-D2 — See due date and overdue state on cards
**As a** board user  
**I want** each card to show its due date and an overdue indicator  
**So that** late work is visible without opening the modal.

**Acceptance criteria**
- Cards with a due date show a due pill.
- Overdue (past due date, status ≠ Done) shows an “Overdue” pill style.
- Done tasks with a past due date are **not** marked overdue.

### US-D3 — Filter the board to overdue tasks only
**As a** board user  
**I want** an “Overdue only” filter  
**So that** I can focus on late work.

**Acceptance criteria**
- Filter bar checkbox calls `GET /tasks?overdue=true`.
- Response is 200 with only overdue tasks (or `[]`).
- Columns remain visible when the filtered list is empty.

### US-D4 — Update or clear a due date
**As a** board user  
**I want** to change or clear a due date when editing  
**So that** schedules stay accurate.

**Acceptance criteria**
- PATCH with a new `due_date` updates the field and preserves unrelated fields.
- Clearing the date in the modal sends `null` and clears the stored due date.

---

## Feature 2: Tags / labels

### US-T1 — Attach tags when creating a task
**As a** board user  
**I want** to add up to five tags to a task  
**So that** I can group related work.

**Acceptance criteria**
- Modal accepts comma-separated tags.
- API stores a trimmed `list[str]`.
- Blank/whitespace-only tags are rejected with 422.
- More than 5 tags or tags longer than 30 characters are rejected with 422.

**AI assumption corrected:** AI suggested a normalized `Tag` table with many-to-many relations and a separate tags API. Rejected as out of scope; kept an in-memory `tags: list[str]` on the task model.

### US-T2 — See tag chips on cards
**As a** board user  
**I want** tags rendered as chips on each card  
**So that** labels are visible on the board.

**Acceptance criteria**
- Each tag appears as a chip under the description.
- Empty tag lists show no chip row.

### US-T3 — Filter tasks by tag
**As a** board user  
**I want** to filter the board by one tag  
**So that** I can find related tasks quickly.

**Acceptance criteria**
- Filter input calls `GET /tasks?tag=<value>`.
- Match is case-insensitive exact match against one of the task’s tags.
- No matches returns 200 with `[]`.

### US-T4 — Update tags without losing them on unrelated edits
**As a** board user  
**I want** tag updates to stick, and unrelated patches to leave tags alone  
**So that** labels are not silently wiped.

**Acceptance criteria**
- PATCH with `tags` replaces the tag list.
- PATCH that omits `tags` (e.g. description-only) preserves existing tags.
