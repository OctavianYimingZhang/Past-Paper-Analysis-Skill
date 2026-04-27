---
name: kp-pattern-mapper
description: >
  Second spoke of the past-paper-analysis suite. Reads extracted material
  and emits the canonical knowledge-point list, the question-pattern
  taxonomy, and a per-question (KP, pattern) mapping. Runs three Sonnet 4.6
  subagents in sequence — topic-mapper → pattern-architect →
  pattern-classifier — each with a fixed schema contract. This is the
  semantic layer: every pattern must cite a textbook section or lecture
  slide; every classification carries a confidence score.
triggers:
  - kp mapping
  - knowledge point mapping
  - pattern taxonomy
  - question classification
  - pattern classification
  - kp pattern mapper
---

# KP + Pattern Mapper — Semantic Layer

## Output Language
English only.

## Purpose
Bridge raw extracted material to the statistical layer. Three sequential Sonnet 4.6 sub-stages, all in this single skill so the orchestrator only sees one Skill call:

| Sub-stage | Agent prompt | Input | Output |
|-----------|--------------|-------|--------|
| 5 — KP boundary optimisation | `agents/topic-mapper.md` | `extracted-lectures.json` (+ `extracted-textbook.json` if present) | `kps.json` (schema_version 2: `id`, `label`, `description`, `prerequisite_kps`, `textbook_chapter_refs`, `lecture_refs`) |
| 5b — Pattern taxonomy derivation | `agents/pattern-architect.md` | `kps.json` + extraction JSONs | `patterns.json` (schema_version 1: `pattern_id`, `label`, `description`, `given_objects`, `asked_operation`, `answer_type`, `solution_sketch`, `common_complications`, `source`) |
| 6 — Question-to-(KP, pattern) classification | `agents/pattern-classifier.md` | `extracted-papers.json` + `kps.json` + `patterns.json` (+ `answer-key-ocr.json` if present) | `mapping.json` (schema_version 2: per-question `primary_kp`, `secondary_kps`, `pattern_id`, `alt_pattern_ids[{pattern_id, confidence}]`, `prompt_summary`, `asked_operation`, `complications`, `marks`, `confidence`) |

## When to use

- **Standalone**: user already has extracted JSONs and just wants the taxonomy. Returns the three files + a per-question confidence histogram.
- **Embedded** (called by `past-paper-orchestrator`): same output, but the orchestrator hands the paths to `stat-engine`.

## Inputs

```json
{
  "extracted_papers":   "/path/to/extracted-papers.json",
  "extracted_lectures": "/path/to/extracted-lectures.json",
  "extracted_textbook": "/path/to/extracted-textbook.json",   // optional
  "answer_key_ocr":     "/path/to/answer-key-ocr.json",       // optional
  "output_dir":         "/path/to/output"
}
```

## Outputs

Files in `output_dir/`:
- `kps.json` (always)
- `patterns.json` (always)
- `mapping.json` (always)

Returned summary:
```json
{
  "ok": true,
  "n_kps": 64,
  "n_patterns": 173,
  "n_mappings": 327,
  "low_confidence_count": 4,        // questions with confidence < 0.7
  "ambiguous_count": 12              // questions with non-empty alt_pattern_ids
}
```

## Implementation rules

1. **Hard requirement**: every entry in `patterns.json` MUST cite a source — a textbook chapter / section, a lecture slide, or both. Patterns without sources are rejected at validation time.
2. **Confidence floor**: `pattern-classifier` flags any question with `confidence < 0.7` for review. Such questions land in the `Review_Queue` worksheet of the eventual XLSX.
3. **Up to two `alt_pattern_ids` per question**, each with its own confidence. The pattern-coverage statistics count primary at full weight and alternates at `0.5 × confidence` to honestly record overlap without double-counting.
4. **No silent secondary KPs**: if a question genuinely spans two KPs, list both in `secondary_kps` (max 2 entries). Never collapse to "miscellaneous".
5. **Single primary `pattern_id`**: even when the question is ambiguous; ambiguity goes into `alt_pattern_ids`, not into the primary slot.

## Required reading

- `agents/topic-mapper.md` — Sonnet 4.6 prompt for KP boundary optimisation.
- `agents/pattern-architect.md` — Sonnet 4.6 prompt for pattern taxonomy. Hard rule: every pattern cites a source.
- `agents/pattern-classifier.md` — Sonnet 4.6 prompt for the per-question mapping.
- `references/kp-schema.md` — JSON-schema contract for `kps.json` (authored in Phase C; until then, the example specs under `skills/past-paper-orchestrator/references/specs/` are the de-facto contract).
- `references/pattern-schema.md` — same for `patterns.json`.

## Quality bar

- 100 % of patterns cite a source.
- ≥ 90 % of questions have `confidence ≥ 0.7`.
- No KP has more than 12 patterns (above that, split the KP).
- No pattern has 0 questions tagged AND 0 textbook seeds (such patterns are noise — drop them).
