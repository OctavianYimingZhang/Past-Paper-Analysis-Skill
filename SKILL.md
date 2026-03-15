---
name: past-paper-knowledge-point-analysis
description: Analyze lecture slide decks, lecture-note PDFs, MCQ past-paper PDFs, and optional image-based DOCX answer keys into reusable lecture/topic maps, question-to-knowledge-point mappings, hotness tables, and fixed-threshold retention bands. Use when Codex needs to identify high-frequency exam topics, recurring year-to-year topics, or review-gated knowledge-point mappings from course materials where slides plus past papers are the minimum available input.
---

# Past Paper Knowledge Point Analysis

## Overview

Use this skill to map lecture materials and past papers into:

- lecture-level topic maps
- one primary knowledge point per question
- hotness statistics
- fixed-threshold retention bands
- review-gated outputs in English

The skill is designed for course specs built from lecture slides or lecture-note PDFs, past papers, and optional answer keys.

## Public Specs

Read the schema first:

- [references/course-spec-schema.md](./references/course-spec-schema.md)

Public example specs:

- [references/specs/example-slides-and-papers.json](./references/specs/example-slides-and-papers.json)
- [references/specs/example-notes-and-papers.json](./references/specs/example-notes-and-papers.json)

## Run

```bash
python3 scripts/analyze_past_papers.py --spec references/specs/example-slides-and-papers.json
```

Replace the example spec with your own local spec containing real paths.

## Rules

- Count exactly one primary knowledge point per question.
- Keep hotness and retention separate.
- Use fixed retention bands:
  - `Anchor`
  - `Core`
  - `Recurring`
  - `One-off`
  - `Not tested`
- Do not convert retention into quartile stars.

## Presets

Preset-first mode is documented in [references/presets.md](./references/presets.md).

For known courses, prefer presets before generic heuristics.

## Outputs

Each run writes:

- Excel workbook
- JSON analysis payload
- Markdown summary

Workbook sheets:

- `Method`
- `Lecture_Knowledge_Map`
- `Question_Mapping`
- `Topic_Frequency`
- `Year_Topic_Matrix`
- `Retention_Bands`
- `Review_Queue`
