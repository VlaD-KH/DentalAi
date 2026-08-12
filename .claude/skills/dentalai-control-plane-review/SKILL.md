---
name: dentalai-control-plane-review
description: Use when reviewing, comparing, or integrating control-plane artifacts (protected_paths.yaml, risk_classification.yaml, CODEOWNERS, .github/workflows, evolution/policy/*, evolution/mutation_api.py, evolution/evaluator.py) for the DentalAi repo, or when asked to verify a self-evolution-kernel policy change before it's merged.
---

# DentalAi Control-Plane Review

Use this workflow whenever asked to review, compare duplicates of, or integrate
control-plane files for the DentalAi repo, or to verify a proposed change to
the self-evolution kernel's policy layer.

## Project model (source of truth: root DentalAi_MASTER_TZ_v2.md, Reviewer.md, bible.md)

DentalAi is an MDR EU 2017/745 dental-lab platform building toward a supervised
self-evolution kernel. Five zones gate what an AI agent may touch:

- **Zone R (Regulated Core)** — clinical logic (geometry, crown_gen, margin,
  segmentation, cam, qa, mdr, ingestion, order_service.py, mcp/server.py,
  orders_router.py, models/schemas.py, db/, shared/constants/, simulations/,
  bible.md). Autonomous mutation forbidden, always.
- **Zone P (Policy Plane)** — evolution/policy/*, CODEOWNERS, .github/,
  evolution/evaluator.py, evolution/mutation_api.py, evolution/metrics/,
  evolution/ledger.jsonl. The mechanism that constrains the agent; the agent
  must never be able to edit what constrains it (Reviewer.md section 5).
- **Zone I (Infrastructure)** — Dockerfiles, docker-compose*.yml,
  pyproject.toml, package.json/lock, scripts/, .gitignore, .env.example.
  Dependency additions = arbitrary code execution risk.
- **Zone T (Tests)** — backend/tests/. Editing a test alongside product code
  in the same diff must escalate risk (bypasses verification).
- **Zone E (Evolvable Product)** — explicit allowlist only (specific frontend
  components, evolution/experience|backlog|proposals, future
  backend/app/mcp/orchestration/, prompts/agents/*.md). Everything not
  explicitly listed defaults to PROTECTED/CRITICAL — never assume an
  unlisted path is safe.

Enforcement authority is `git diff --name-only`, never a model's self-reported
zone/risk field (`diff_is_authoritative: true`). Mixed diffs take the max
risk (`MAX_RISK_WINS`). Unmatched paths fail closed (`default_risk_for_unmatched:
CRITICAL`).

## When comparing a "new" policy file against what's in the repo

1. Read both versions fully — do not just diff line counts. A full-file
   rewrite (e.g. 22 lines to 200+ lines) is often a legitimate v1->v2 overhaul,
   not noise; identify which specific gaps the new version closes (missing
   catch-all in CODEOWNERS, unprotected mcp/server.py or .github/, undefined
   behavior for unmatched paths, contradictory autonomous_mutation +
   human_approval_required flags, etc.).
2. Cross-check every path referenced in the new policy against the actual
   repo tree (`test -e <path>`) — flag any path that doesn't exist yet vs.
   paths planned for a later phase (that's fine if explicitly noted as
   "not yet created").
3. If a bundled .zip accompanies loose files, unzip and diff each pair —
   in practice these are often byte-identical repackaging with no unique
   content, in which case drop the zip rather than committing it.
4. Never trust a claimed test-pass count in a document. Re-run it yourself:
   copy only the minimal subset needed (backend/, evolution/, shared/,
   relevant frontend/components/, CODEOWNERS, bible.md) into a scratch dir —
   do not cp -r the whole repo if frontend/node_modules or .git exist, that
   will hang. Install pyyaml pytest, then run pytest -v and read the actual
   pass/fail count.
5. Independently grep the actual source for any claims about code state
   before repeating them (e.g. "AuditLog is in-memory" — verify by reading
   order_service.py, don't just relay the claim).

## Before applying changes

Always show a real diff (diff -u old new) per file before overwriting
anything, even when the change was pre-approved in principle — policy files
are Zone P/R and mistakes here are hard to notice later.

## Applying + git checkpoint

- Copy each file to its documented target path (installer docs like
  INSTALL.md in a review bundle usually list exact target paths).
- Fill reviewed_by / reviewed_at immediately; leave baseline_commit as a
  placeholder, commit, capture the resulting hash, then do a small follow-up
  commit setting baseline_commit to that real hash (can't know your own
  commit's hash before it exists).
- Delete superseded artifacts (redundant zips, weak tests being replaced).
- git push requires the human's own GitHub credentials — never accept a
  token/PAT from the user to do this yourself; tell them to run git push
  themselves.

## Merging loose unsystematized docs into the master TZ

When asked to fold a standalone doc (e.g. a new subsystem proposal) into the
canonical DentalAi_MASTER_TZ_v2.md: check it against the zone model first
(does it try to grant Zone E-level autonomy to something touching Zone R?),
resolve any terminology collisions explicitly (e.g. an LLM "reviewer" role is
not the same thing as the deterministic evolution/evaluator.py, which must
never call an LLM), append as a new numbered Part, and move the source file to
docs/sources/ rather than deleting it.
