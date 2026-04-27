---
name: drill-curator
description: >
  Synthesis spoke 2 of 3 (parallel-dispatch tier) of the past-paper-analysis
  suite. Picks 5–8 recommended drill questions per anchor / core KP plus
  1–2 fresh-pattern construction prompts (textbook-seeded patterns the
  examiner hasn't used recently). Balances coverage across the dominant +
  saturated patterns the examiner is recycling, while seeding asymmetric
  upside on fresh patterns. Powered by Opus 4.7.
triggers:
  - drill curator
  - drill set
  - past paper drill
  - recommended practice
  - revision drill
  - fresh pattern challenge
---

# Drill Curator — Recommended Practice Set

## Output Language
Per `--lang` flag from the orchestrator. Default: English only.

## Purpose
For each anchor / core KP, pick a small drill set (5–8 past-paper questions) that:

1. Covers the dominant pattern at the right multiplicity (more drills on the saturated patterns the examiner recycles).
2. Includes at least one drill on each `saturated` pattern.
3. Adds 1–2 **fresh-pattern construction prompts** — patterns seeded by textbook / lecture but unseen recently. These are short, hand-written stems (50–120 words) since no past-paper question exists for them yet.
4. Excludes drills the user has presumably already done (the most recent paper is held out — the "leave-one-out" sample).

For `emerging` / `oneoff` / `legacy` KPs (when surfaced via thin-data fallback in the orchestrator), pick 3–5 drills focused on the dominant pattern.

## When to use

- **Standalone**: user wants a drill plan from existing analysis + mapping JSONs. Returns the drill JSON + a markdown bullet list.
- **Embedded** (parallel-dispatched by `past-paper-orchestrator`): returns structured drill cards for the renderer.

## Inputs

```json
{
  "analysis":         "/path/to/<course_id>-analysis.json",
  "mapping":          "/path/to/mapping.json",
  "pattern_coverage": "/path/to/pattern-coverage.json",
  "patterns":         "/path/to/patterns.json",
  "papers":           "/path/to/extracted-papers.json",
  "lang":             "en",
  "mode":             "analyst",
  "exclude_year":     null              // optional: e.g. 2024.4 to leave most recent paper out
}
```

## Outputs

```json
{
  "ok": true,
  "drill_sets": [
    {
      "kp_id": "L03.02",
      "kp_label": "Implicit differentiation",
      "drills": [
        {"year": 2022.4, "question_number": 6, "pattern_id": "L03.02.P02", "rationale": "tangent-line variant; dominant pattern, asked twice in last 4 years"},
        ...
      ],
      "fresh_challenges": [
        {"pattern_id": "L03.02.P05", "stem": "...50-120 word custom prompt...",
         "rationale": "textbook §5.4 worked-ex 12; unseen since 2018"}
      ]
    },
    ...
  ],
  "n_drills_total": 287,
  "n_fresh_challenges": 14
}
```

When `lang=both`, every `rationale` and `stem` is emitted twice (`rationale_zh`, `stem_zh`).

## Implementation

The Opus 4.7 subagent at `agents/drill-curator.md` does the curation. The deterministic precompute (per-KP candidate-question pool, fresh-pattern slot list) is built by `core.kp_cheatsheet.build_all_cheatsheets()`'s drill-set helper; Opus's job is to pick + rationalise.

## Mode contract

- `analyst`: drill rationales reference posterior + saturation index ("dominant pattern, P(appearing) = 0.81, saturation 0.62").
- `student`: drill rationales are friendlier ("appears every year on the recent papers; this is the bread-and-butter version"). The actual drill list is identical.

## Required reading

- `agents/drill-curator.md` — Opus 4.7 prompt (authored in Phase C — until then, the agent uses the existing `agents/statistical-interpreter.md` prompt's drill-set section as a fallback).
- `references/drill-strategy.md` — strategy for balancing recycled vs fresh patterns. Authored in Phase C.

## Quality bar

- Every anchor / core KP gets ≥ 5 drills + ≥ 1 fresh challenge.
- Every drill cites a real (year, question_number) from `mapping.json`. No hallucinated questions.
- Every fresh challenge cites a textbook section or lecture slide for the pattern source.
- No drill is older than 8 years (the recency lambda decays older papers; older drills are out of distribution).
