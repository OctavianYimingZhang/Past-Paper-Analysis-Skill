---
name: technique-coach
description: >
  Synthesis spoke 3 of 3 (parallel-dispatch tier) of the past-paper-analysis
  suite. Writes per-KP exam-technique prose: how to set up the problem,
  marks-allocation cues, common traps, what an examiner is looking for at
  each part-mark threshold, and a short "before you read the question"
  checklist. Powered by Opus 4.7. Honours analyst vs student mode and the
  `--lang` flag.
triggers:
  - technique coach
  - exam technique
  - exam strategy
  - how to answer
  - marks allocation
  - common traps
---

# Technique Coach — Exam-Strategy Prose

## Output Language
Per `--lang` flag from the orchestrator. Default: English only. Bilingual blocks on `--lang both` use stacked CN-then-EN format.

## Purpose
For each anchor / core KP, produce structured coaching prose that turns the cheat-sheet cards + drill set into a study plan a student can actually execute under exam conditions. Output schema (one entry per KP):

```json
{
  "kp_id": "L03.02",
  "kp_label": "Implicit differentiation",
  "approach":         "...",      // 2-3 sentences: the canonical attack on the dominant pattern
  "marks_walk":       [...],      // ordered list: "Mark 1: differentiate both sides...", "Mark 2: substitute..."
  "common_traps":     [...],      // bullet list: "Forgets to apply chain rule on y^2", "...
  "examiner_signal":  "...",      // 1-2 sentences: what an examiner is looking for above 80% mark
  "pre_read_checklist": [...],    // ≤4 items the student does BEFORE reading any question on this KP
  "fresh_pattern_warning": "...", // 1 sentence per fresh pattern flagged in cheat-sheet
  "approach_zh":         "...",   // emitted only when lang in {"zh", "both"}
  "marks_walk_zh":       [...],
  "common_traps_zh":     [...],
  "examiner_signal_zh":  "...",
  "pre_read_checklist_zh": [...]
}
```

## Dependency contract

`technique-coach` reads the `cheatsheet-writer` cards + `drill-curator` drill set in addition to the raw analysis. To preserve parallel dispatch, the orchestrator runs all three with the **same `analysis` + `mapping` snapshot**: `technique-coach` does not wait for the other two to return; instead it independently rebuilds the cheat-sheet scaffold via `core.kp_cheatsheet.build_all_cheatsheets()` so it has the same dominant-pattern + saturated-pattern view the others see. The orchestrator merges all three outputs in stage 6.

This is intentional. If `technique-coach` blocked on the other two, the synthesis stage would be sequential again.

## When to use

- **Standalone**: user wants exam-technique coaching for an existing analysis. Returns the prose JSON + a markdown coaching doc.
- **Embedded** (parallel-dispatched by `past-paper-orchestrator`): returns structured coaching cards for the renderer.

## Inputs

```json
{
  "analysis":         "/path/to/<course_id>-analysis.json",
  "patterns":         "/path/to/patterns.json",
  "pattern_coverage": "/path/to/pattern-coverage.json",
  "mapping":          "/path/to/mapping.json",
  "lang":             "en",
  "mode":             "analyst"
}
```

## Outputs

```json
{
  "ok": true,
  "coaching": [/* one entry per anchor / core KP, plus thin-data fallbacks */],
  "n_entries": 30
}
```

## Implementation

The Opus 4.7 subagent at `agents/technique-coach.md` produces all prose. The deterministic scaffold (which patterns to address, which complications to call out as traps) is precomputed by `core.kp_cheatsheet.build_all_cheatsheets()` — Opus only writes the prose, never invents the structure.

## Mode contract

- `analyst`: marks-walk references the official mark scheme structure; examiner-signal prose may use technical terms ("rigour gate", "rate-limiting step").
- `student`: marks-walk uses plain-English numbered steps; examiner-signal prose is direct address ("the examiner is looking for…"); pre-read checklist is ≤4 items max in plain language.

## Required reading

- `agents/technique-coach.md` — Opus 4.7 prompt (authored in Phase C).
- `references/technique-playbook.md` — the canonical structure of marks_walk + common_traps. Authored in Phase C.

## Quality bar

- Every anchor / core KP gets all five prose fields populated.
- `marks_walk` length matches the typical question's mark count for that KP ± 1 step.
- `common_traps` lists at least one trap drawn from `pattern_coverage[*].complications_seen` (real traps from real papers, not hallucinated).
- `pre_read_checklist` is ≤ 4 items.
