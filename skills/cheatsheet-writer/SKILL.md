---
name: cheatsheet-writer
description: >
  Synthesis spoke 1 of 3 (parallel-dispatch tier) of the past-paper-analysis
  suite. Turns the statistical-engine output into per-KP cheat-sheet cards —
  tier rationale, dominant pattern, already-tested-vs-still-possible
  decomposition, and the "how it will be tested" prose. Powered by Opus 4.7
  for high-judgment narrative under hard schema constraints. Honours
  analyst vs student mode and the `--lang` flag.
triggers:
  - cheatsheet writer
  - kp cheatsheet
  - per-kp narrative
  - tier interpretation
  - statistical interpreter
  - cheat sheet
---

# Cheatsheet Writer — Per-KP Narrative

## Output Language
Per `--lang` flag from the orchestrator. Default: English only. `--lang both` triggers stacked CN-then-EN blocks. CN may code-switch on technical terms.

## Purpose
For each KP in the analysis, write a cheat-sheet card. The card is the meat of the report's middle section. Card schema (one row per KP):

```json
{
  "kp_id": "L03.02",
  "kp_label": "Implicit differentiation",
  "tier": "anchor",
  "tier_reasons": [...],
  "posterior_summary": "0.81 [0.41, 1.00], 11/11 years",
  "headline": "Highest-density anchor; saturated on tangent-line variant.",
  "narrative": "...",                       // 4-7 sentences
  "how_it_will_be_tested": "...",           // 3-5 sentences: setup, asked operation, dominant solution path, fresh variant to prep against
  "exam_scope_notes": "...",                // 1-2 sentences citing past-paper Q numbers
  "dominant_pattern": {...},                // CheatSheetVariant
  "saturated_patterns": [...],
  "fresh_patterns": [...],
  "hot_patterns": [...],
  "dormant_patterns": [...],
  "already_tested": [...],                  // (year, question_number, pattern, complications) tuples
  "still_possible": [...],
  "open_caveats": [...]
}
```

When `lang=both`, also emit `headline_zh`, `narrative_zh`, `how_it_will_be_tested_zh`, `exam_scope_notes_zh`. ZH prose may code-switch on technical terms.

## When to use

- **Standalone**: user wants per-KP narratives for an existing analysis. Returns the cards + a markdown rendering.
- **Embedded** (parallel-dispatched by `past-paper-orchestrator`): returns structured cards for the renderer.

## Inputs

```json
{
  "analysis":         "/path/to/<course_id>-analysis.json",
  "patterns":         "/path/to/patterns.json",
  "pattern_coverage": "/path/to/pattern-coverage.json",
  "mapping":          "/path/to/mapping.json",
  "lang":             "en",         // "en" | "zh" | "both"
  "mode":             "analyst"     // "analyst" | "student"
}
```

## Outputs

```json
{
  "ok": true,
  "cards": [/* one CheatSheetCard per KP */],
  "n_cards": 64,
  "n_with_pattern_data": 58,
  "n_thin_data_fallback": 6        // KPs surfaced via emerging/oneoff fallback (no anchor/core)
}
```

## Implementation

The Opus 4.7 subagent at `agents/statistical-interpreter.md` does the writing. Deterministic structure (tier reasons, dominant pattern selection, already-tested rows) is precomputed by `core.kp_cheatsheet.build_all_cheatsheets()` and handed to Opus as scaffolding; the model only fills the four prose fields (`headline`, `narrative`, `how_it_will_be_tested`, `exam_scope_notes`) plus their `_zh` siblings when `lang=both`.

## Mode contract

- `analyst`: full prose, includes Bayesian terminology, explicit `(lambda=…, tau=…, ref_year=…)` callout in the headline of unstable KPs.
- `student`: same data, friendlier language. "Credible interval" → "rough confidence band". Hedge phrases ("the model thinks") are banned. Direct address ("you should drill…") is encouraged.

## Required reading

- `agents/statistical-interpreter.md` — Opus 4.7 prompt. Already updated to emit `how_it_will_be_tested` + `exam_scope_notes` + bilingual variants.
- `references/cheatsheet-format.md` — final card schema (authored in Phase C; until then, `core/kp_cheatsheet.py::KPCheatSheet` is the contract).
- `core/kp_cheatsheet.py` — the deterministic scaffold; tests in `tests/test_kp_cheatsheet.py` (22 tests, all green).

## Quality bar

- Every anchor / core KP card has all four prose fields populated.
- Bilingual cards have all four `_zh` siblings populated.
- `headline` ≤ 24 words. `narrative` 4–7 sentences. `how_it_will_be_tested` 3–5 sentences.
- `exam_scope_notes` cites at least one (year, Q-number) tuple drawn from `mapping.json`.
- The card structure is exactly what `core.kp_cheatsheet.KPCheatSheet` expects so the renderer can ingest it without translation.
