---
name: past-paper-orchestrator
description: >
  Orchestrates a multi-skill past-paper analysis suite end-to-end. Reads a
  course spec, dispatches material ingestion, KP + pattern derivation, and
  statistical analysis sequentially, then fans out cheat-sheet writing,
  drill curation, and exam-technique coaching in parallel before assembling
  the final report. Produces analyst-grade or student-friendly DOCX, XLSX,
  and Markdown deliverables. Mirrors the hub-and-spokes shape of the
  equity-research-suite.
triggers:
  - past paper analysis
  - past-paper analysis
  - past paper report
  - exam paper analysis
  - revision report
  - knowledge point analysis
  - kp analysis
  - past-paper-knowledge-point-analysis
---

# Past-Paper Orchestrator — Suite Hub

## Output Language
Default: **English**. Switch to bilingual via `--lang both` (English + Chinese, stacked CN-then-EN block, never side-by-side). Skill internals (this file, sub-skill SKILL.md files, agent prompts, references) are English-only. Generated reports honour the `--lang` flag.

## Purpose
Produce one cohesive past-paper analysis report that reads like a single revision strategist wrote it — not seven sub-skills concatenated. The orchestrator is the only entry point. It reads the course spec, runs the ingest → mapping → statistics chain, fans out the synthesis specialists in parallel, then hands the merged payload to the renderer.

The suite is built on these locked design choices (see `~/.claude/plans/users-octavianzhang-desktop-ngal-m1-md-sorted-teapot.md` §9):

1. **Hub-and-spokes**: this orchestrator dispatches every other skill; spokes never call each other directly.
2. **File-based handoff between sequential stages, return-value handoff between parallel stages.** Stages 1–4 (ingest → mapper → stat-engine) write JSON to `spec.output_dir`; stages 5a/5b/5c (cheatsheet / drill / technique) and stage 6 (renderer) pass payloads via Skill-tool returns.
3. **Pure-Python statistical core in `core/`**, never duplicated per skill.
4. **English internals; bilingual reports gated behind `--lang both`.**
5. **Two output modes**: `analyst` (dense bilingual revision deliverable) and `student` (friendlier; drops methodology appendix; front-loads drill links).

## When to invoke this skill

The user has:
- Lecture slides and / or a consolidated lecture-notes PDF.
- A textbook PDF aligned to the syllabus (strongly recommended — seeds the pattern taxonomy). When absent, the suite still produces patterns from lectures only and marks each pattern's source accordingly.
- Three or more past papers of the same course. MCQ, short-answer, and structured papers are all supported.
- Optional DOCX answer keys.

They want:
- Predictions naming **what** topics will appear AND **how** they will be tested (which pattern, what setup, what solution path).
- Saturated-vs-fresh pattern decomposition.
- Auditable uncertainty quantification at the KP level.
- A drill set of past-paper questions to practice against.
- Per-KP exam-technique coaching prose.

If any required input is absent, pause and ask the user — never guess.

## Pipeline (8 stages across 7 spokes)

| # | Stage | Spoke | Mode | Notes |
|---|-------|-------|------|-------|
| 1 | Spec audit | (this orchestrator) | sync | validate `spec.json`, list missing sources |
| 2 | Material ingest | `paper-ingest` | sequential, file-handoff | extract papers / lectures / textbook / answer-keys |
| 3 | KP + pattern + mapping | `kp-pattern-mapper` | sequential, file-handoff | runs three Sonnet subagents in turn: topic-mapper → pattern-architect → pattern-classifier |
| 4 | Statistical analysis | `stat-engine` | sequential, pure Python, no LLM | KP-level Beta posteriors + pattern-level coverage |
| 5a | Per-KP cheat-sheets | `cheatsheet-writer` | **parallel** | Opus 4.7 |
| 5b | Drill curation | `drill-curator` | **parallel** | Opus 4.7 |
| 5c | Exam-technique coaching | `technique-coach` | **parallel** | Opus 4.7 |
| 6 | Multi-format render | `report-renderer` | sequential | wraps `anthropics-skills:docx` + `anthropics-skills:xlsx` |

Stages 5a, 5b, 5c **must** be dispatched in a single message with three `Skill` tool calls so they run concurrently. Sequencing them through the same Opus subagent is the bottleneck the suite is designed to eliminate.

## Orchestration contract

```
Input:  spec.json with {course_id, papers[], lectures, textbook?, output_dir, hyperparameters?, lang?, mode?}
Output: <output_dir>/<course_id>-analysis.{md, docx, xlsx, json}
        + suite-summary message with file paths and the executive headline
```

Pseudocode:

```
1. validate spec.json against skills/past-paper-orchestrator/references/course-spec-schema.md
2. extraction = Skill(skill="paper-ingest", args=spec)
3. mapping    = Skill(skill="kp-pattern-mapper", args={extraction, output_dir})
4. stats      = Skill(skill="stat-engine", args={extraction, mapping, output_dir, hyperparameters})
5. PARALLEL (single message, three tool calls):
     cards    = Skill(skill="cheatsheet-writer", args={stats, lang, mode})
     drills   = Skill(skill="drill-curator",     args={stats, mapping, lang, mode})
     coaching = Skill(skill="technique-coach",   args={cards, drills, lang, mode})
6. files = Skill(skill="report-renderer",
                 args={stats, cards, drills, coaching, lang, mode, output_dir})
7. return executive summary + file paths
```

(`technique-coach` reads `cards` + `drills`, but it can run concurrently with them because it operates on the latest in-memory snapshot — see `skills/technique-coach/SKILL.md` for the dependency contract.)

## Mode contract

- **`analyst`** (default): full report. Compact executive summary on top, per-KP cheat-sheet middle, methodology appendix at bottom. Bilingual blocks honour `--lang both`.
- **`student`**: friendlier rendering. Drops the methodology appendix, drops Bayesian jargon from the body, front-loads the recommended drill set, replaces "credible interval" with "rough confidence band" in the prose layer (the underlying numbers stay identical). Bilingual blocks still honour `--lang both`.

The mode is passed through every spoke; spokes that don't change behaviour by mode (`paper-ingest`, `kp-pattern-mapper`, `stat-engine`) ignore it.

## Statistical contract (every user-facing summary must honour)

- Attach a credible interval to every KP-level probability.
- Quote `lambda`, `tau`, `alpha`, `reference_year` up front (analyst mode) or in a single closing footnote (student mode).
- Surface unstable KPs **before** the tier tables.
- Use **moment-matched Beta posterior** wording for the KP layer. Never say "conjugate posterior".
- Use **frequency + saturation + freshness** wording for the pattern layer. Never claim a credible interval at the pattern level — pattern data is too sparse.
- Preserve `tier_reasons` lists verbatim (do not paraphrase them away).
- For every anchor / core KP, the narrative MUST decompose into pattern language: dominant pattern, saturated pattern(s), fresh pattern(s) when any are flagged.

## Required reading

All references live under `skills/past-paper-orchestrator/references/`:

- `methodology.md` — statistical source of truth.
- `tier-definitions.md` — every KP tier rule + the parallel pattern tier (`saturated`, `hot`, `fresh`, `dormant`).
- `course-spec-schema.md` — input JSON shape.
- `presets.md` — known courses (Manchester Y1 biology, Edexcel IAL Maths units, Manchester Y2/Y3 placeholders).
- `subagent-orchestration.md` — historical prompt templates per stage. Superseded by the per-spoke `SKILL.md` files but kept for reference.

## How to run end-to-end

1. Ask the user for or confirm the spec; resolve any missing sources. Ask for the textbook PDF if the syllabus has one.
2. Validate spec → call `paper-ingest`. Wait for completion.
3. Call `kp-pattern-mapper`. Wait for completion.
4. Call `stat-engine`. Wait for completion.
5. **In one message**, dispatch three Skill tool calls in parallel: `cheatsheet-writer`, `drill-curator`, `technique-coach`.
6. Once all three return, call `report-renderer` with the merged payload + mode.
7. Hand the user the produced files (DOCX as the headline deliverable; XLSX for drill-down; MD for git-friendly diff; JSON for re-runs).

## Quality bar

- Every anchor / core KP gets pattern decomposition + drill set + technique prose.
- The DOCX must have ≥ the structural fingerprint of the previous monolithic skill (same heading hierarchy, ≥ same paragraph count) and additionally populate `drill-set` and `technique-prose` sections.
- No regressions on the cheat-sheet section vs the v0.1 layout.
- Wall-clock for the synthesis stage (5a/5b/5c) is ≥ 2.5× faster than serial dispatch.

## Companion skills (optional, dispatched on user request)

See `references/companion-skills.md` for the full matrix. High-signal candidates already installed:
- `data:statistical-analysis` — for deeper Bayesian diagnostics.
- `anthropics-skills:doc-coauthoring` — when the user wants to co-edit the rendered DOCX section by section.
- `anthropics-skills:skill-creator` — when extending the suite with a new specialist.
