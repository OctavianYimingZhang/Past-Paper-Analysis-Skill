# External Borrowings — Provenance Log

Every code or pattern lift from outside this repo lives in this log, with license, last verification date, what was lifted, and which file in this repo carries it. Lifts without a row here are unauthorised; CI should reject them.

The plan that introduced this log: `~/.claude/plans/users-octavianzhang-desktop-ngal-m1-md-sorted-teapot.md` §3.

## Active borrowings

| Source repo | License | Verified on | Last commit (upstream) | What was lifted | Carrier file in this repo | Notes |
|-------------|---------|-------------|------------------------|-----------------|---------------------------|-------|
| `deusyu/translate-book` | MIT | 2026-04-27 (pending verification — see Pending below) | (TBD) | Glossary persistence pattern: JSON-backed term map keyed by lower-cased English term, looked up by every translator. **Pattern only**, no code. | `core/bilingual_glossary.py` | The implementation is fully ours; only the high-level shape (term map + persistent JSON + canonical key normalisation) was inspired. No code copied verbatim. |

## Pending borrowings (must be verified before they ship)

| Source repo | Stage | What we want to lift | Verification still required |
|-------------|-------|----------------------|------------------------------|
| `deusyu/translate-book` | C/D | (already lifted; see Active) | Run `gh repo view deusyu/translate-book` to confirm MIT + last commit ≤ 6 months. If verification fails, the carrier file rewrites cite "in-house" and this row moves to Rejected. |
| `K-Dense-AI/scientific-agent-skills` | D | Posterior-summary phrasing patterns from their Bayesian narrative scaffolding | `gh repo view`, license check, license must be MIT/Apache, lift only prose not code |
| `anthropics-skills:pdf` (installed) | C/D | Wrapper invocation only — no code lift | Confirm the skill is currently installed before relying on it. Already installed per available-skills list 2026-04-27. |
| `anthropics-skills:docx` (installed) | C/D | Wrapper invocation only — no code lift | Same. |
| `anthropics-skills:xlsx` (installed) | C/D | Wrapper invocation only — no code lift | Same. |
| `anthropics-skills:skill-creator` (installed) | B (already used as scaffolding reference) | Frontmatter + directory conventions only | Already aligned during Phase B SKILL.md authoring. |

## Rejected borrowings (with rationale)

| Source repo | Why rejected |
|-------------|--------------|
| (none yet) | |

## Verification protocol

Before any row moves from Pending to Active:

1. `gh repo view <owner>/<repo>` — must succeed; license must be MIT or Apache 2.0.
2. `gh repo view <owner>/<repo> --json updatedAt` — last commit must be within 6 months of today.
3. The actual lift must be reviewed by a human or a subagent with explicit instructions to flag any line not licence-compatible.
4. If any of (1)–(3) fail, the lift is REJECTED. Carrier files revert to in-house implementation and the row moves to Rejected with a one-line rationale.

## Why this exists

Past iterations of the suite shipped silent dependencies on tools that later became unavailable, were re-licensed, or contained vulnerabilities only discovered after weeks of integration. This log makes the dependency surface explicit so future maintainers can audit it in seconds.

When in doubt: write it ourselves. The cost of a fresh implementation is almost always less than the cost of a surprise lift later.
