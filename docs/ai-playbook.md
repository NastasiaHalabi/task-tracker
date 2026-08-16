# My Personal AI Coding Playbook

## When I reach for AI first

I use AI first for repository surveys, turning acceptance criteria into focused
tests, comparing implementation options, reviewing diffs, and drafting factual
documentation. It helped most when the task was constrained, such as adding due
dates and tags without changing storage architecture or API conventions.

## When I do not reach for AI first

I do not start with AI when I am learning a core concept, handling secrets or
personal data, or making a decision whose risks and context are not visible in
the repository. I inspect the code, reproduce the behavior, or ask the relevant
person before delegating those decisions.

## My non-negotiables

- Never paste credentials, tokens, `.env` values, production logs, or real
  personal/customer data into an AI tool.
- Never accept a change I cannot explain in my own words.
- Preserve the documented status values, priority values, API shapes, and
  project scope unless a deliberate decision changes them.
- Treat AI output as a proposal until the diff and verification evidence agree.

## My review rules

I read the relevant files before prompting, inspect every diff, and grade review
comments as useful, noise, or wrong. I run the narrowest useful check first and
then the full test suite. For infrastructure and documentation, I verify commands
and claims against the repository or a running system. I reject suggestions that
add scope, hide failures, weaken tests, or introduce a dependency without need.

## What I am still figuring out

I am still learning when a team should require AI contribution logs and how much
verification evidence belongs in a small pull request. I would agree on those
norms with teammates and revisit them after seeing what improves reviews without
creating paperwork that nobody uses.

## Decision Card

- New feature: acceptance criteria, repository survey, and a small ADR before code.
- Code review: diff plus targeted tests; AI comments are graded, not assumed true.
- Debugging: reproduce first, then ask AI to explain evidence and propose checks.
- Infrastructure: verify commands locally and in CI; never hide a failing command.
- Planning/governance: use repository evidence and record rejected alternatives.
- Never paste: secrets, customer data, private logs, or unredacted configuration.
- One rule: if I cannot explain and verify it, I do not submit it.
