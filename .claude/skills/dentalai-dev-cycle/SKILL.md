---
name: dentalai-dev-cycle
description: Use when starting, planning, or working through any DentalAi development task (Phase 0 Задачи, bugfixes, new endpoints, policy changes) — routes each stage of the task to the right installed agent-skills skill based on the DEFINE→PLAN→BUILD→VERIFY→REVIEW→SHIP pattern found in this repo's own history.
---

# DentalAi Dev Cycle Router

This repo's own git log, CHANGELOG, audit reports, test-batch naming
(test_batchNN_*) and .pytest_cache history show a consistent implicit
six-stage cycle every real change goes through, whether or not anyone wrote
it down. This skill makes that cycle explicit and maps each stage to one of
the 24 installed `.claude/skills/` (from addyosmani/agent-skills) so the
right skill gets pulled into context at the right time instead of relying on
constant description-matching.

## The six stages

1. **DEFINE** — what is the actual requirement, and which Zone (R/P/I/T/E,
   see `evolution/policy/protected_paths.yaml`) does it touch? Never start
   writing code before this is answered — Zone R/P changes need more
   scrutiny than Zone E.
   - Skill: `spec-driven-development`
2. **PLAN** — break the Задача into ordered sub-steps; identify what can be
   verified in this sandbox (no Docker/Postgres/root) vs. what needs the
   user's own machine.
   - Skill: `planning-and-task-breakdown`
3. **BUILD** — implement in small increments, one behavior at a time. For
   Zone R (clinical/geometry) code: write the failing test FIRST (see
   test_batch25_qa_inspector_fails_on_thin_geometry for the pattern used in
   this repo — construct a deliberately-defective fixture, assert it fails).
   - Skills: `test-driven-development` (RED before GREEN, Zone R/T especially)
     → `incremental-implementation`
4. **VERIFY** — never trust a written claim (CHANGELOG entry, docstring
   comment, "fixed" commit message) about test status. Re-run the actual
   tests yourself. In this sandbox: no fastapi/prisma installed by default,
   no Docker/Postgres — scope verification honestly to what's actually
   runnable here and say so explicitly rather than claiming full coverage.
   - Skills: `test-driven-development` → `security-and-hardening` (for
     anything touching auth, input validation, or Zone P)
5. **REVIEW** — for Zone P (policy/control-plane) or Zone R changes, show a
   real diff before applying; check the change against
   `evolution/policy/protected_paths.yaml` zone rules and the IMMUNE
   principles (see DentalAi_MASTER_TZ_v2.md Part IX) before considering it
   done.
   - Skills: `code-review-and-quality` → `doubt-driven-development` (actively
     look for the reason this change is wrong before shipping it)
6. **SHIP** — commit with an unambiguous message (careful with backticks —
   they trigger shell command substitution in `git commit -m`; use
   `git commit -F /tmp/msg.txt` with a quoted heredoc for anything containing
   backticks or `$`). Push requires the human's own GitHub credentials —
   never accept a token from the user and push on their behalf.
   - Skill: `git-workflow-and-versioning`

## Per-task skill line convention

DentalAi_MASTER_TZ_v2.md Part IV lists, inline under each Задача, a
`**Skills:** skill-a (reason) → skill-b (reason) → ...` line — these are
margin notes so the sequence above doesn't have to be re-derived by
attention/description-matching every time; the TZ file is always loaded for
implementation work, so the routing travels with the task definition itself
rather than depending on the model noticing a skill's one-line description
matches.

## Known sandbox verification gaps (update as they're resolved)

- No Docker, no root/sudo, no live Postgres — Задачи 0.1 (Prisma
  persistence), 0.2 (AuditLog append-only), 0.3 (JWT auth) cannot be fully
  end-to-end verified in a Cowork sandbox session; they need either the
  user's own machine or a CI run.
- `fastapi`/`prisma` are not installed by default — `pytest backend/tests/`
  will fail to even collect test_batch10/12/24 unless
  `pip install fastapi prisma --break-system-packages` is run first.
