# Final AI Review and Ownership Evidence

## AGENTS.md guardrails

- Repo-specific stack and commands included: yes.
- Docs-first/read-first guardrail included: yes.
- Unexpected `app/` or `frontend/` edits rule included: yes.
- Scope protection included: yes; authentication and a database remain out of scope.

## AI code review mini-log

Reviewed diff: documentation additions in `app/models.py`, `app/storage.py`, and
`app/routers/health.py`, followed by the final security corrections.

| AI comment | Grade | Reason | Verification or decision |
|---|---|---|---|
| Reject explicit `null` for PATCH fields whose stored response fields cannot be null | Useful | The update model accepted values that failed later while rebuilding `TaskResponse`, causing HTTP 500 | Added field validation and regression tests expecting 422 |
| Add full parameter/return docstrings to every small in-memory storage helper | Noise | The text is accurate but repetitive and does not change behavior | Preserved existing documentation work; did not expand it further |
| Keep `"null"` in CORS because `allow_credentials=False` makes it safe | Wrong | Null-origin pages can still read and mutate this unauthenticated local API | Removed the origin and documented serving the frontend on localhost:5500 |

## AI security mini-review

Source review: `docs/security-review.md`.

| Finding | File evidence | Grade | Reason | Next action |
|---|---|---|---|---|
| Explicit null PATCH values can cause HTTP 500 | `app/models.py`, `app/storage.py` | Valid | Reproduced in the read-only review; model/storage contracts disagreed | Corrected in final project and covered by tests |
| Null-origin CORS access broadens the local trust boundary | `app/main.py`, former README direct-file instructions | Valid | A downloaded or sandboxed document can have a null origin | Removed null origin; use localhost:5500 |
| Missing authentication is a release vulnerability for this course submission | `AGENTS.md`, task routes | False Positive | Authentication is intentionally excluded and the app is documented as local-only | Keep local/private; reconsider only in a later approved scope |
| Unbounded fields and in-memory task count create resource-exhaustion risk | `app/models.py`, `app/storage.py` | Valid | Limits are incomplete if the service is exposed publicly | Document local scope; design limits/pagination later |

## Manual security check

I checked that `.env` is ignored by Git, excluded by Docker, and absent from the
tracked-file list. I also checked that no test, CI, or Docker command hides a
failure with `continue-on-error`, `|| true`, or a skipped pytest step. This
matters because a green release must not depend on leaked configuration or a
command that reports success without performing verification.

## One AI output I rejected or corrected

For tags, AI proposed a normalized Tag entity, separate endpoints, and a
many-to-many database design. I rejected that design because this project uses
in-memory storage and the feature needed only a small validated `list[str]`.
The final implementation stayed inside scope and preserved task response behavior.

## Three AI usage rules

1. Never paste secrets, `.env` values, production logs, or personal/customer data.
2. Always verify suggestions through repository evidence, diff review, and the relevant command or manual check.
3. Record AI contributions by naming the affected file, the accepted or rejected suggestion, and the verification result.

## Ownership statement

I am comfortable submitting this repository as my work because I can explain
the application flow, validation rules, tests, CI workflow, Docker choices, and
the final security corrections. I reviewed AI suggestions rather than accepting
them automatically, including rejecting database-backed tags and correcting
unsafe null handling and CORS guidance. I checked the diffs and verification
evidence against the real repository. The final decisions and responsibility
for this submission are mine.
