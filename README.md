# Past Paper Knowledge Point Analysis

`past-paper-knowledge-point-analysis` is an open-source Codex skill for turning course materials into exam-oriented topic maps.

It is designed for the study workflow where a user has:

- lecture slides or reorganized lecture notes
- past papers
- optional answer keys

The skill analyzes those inputs and produces:

- lecture-to-topic maps
- one primary knowledge point per question
- topic hotness tables
- year-to-year retention bands
- review queues for weak OCR, weak parsing, or weak mappings

## What Problem It Solves

Students often have two separate assets:

- lecture materials that define the syllabus
- past papers that reveal what is repeatedly tested

This skill connects those assets. It helps answer questions such as:

- Which knowledge points are tested most often?
- Which topics recur across formal paper years?
- Which topics are one-off or auxiliary?
- Which question mappings are uncertain and require review?

## Minimum Input

Minimum usable input:

- `Lecture Slides + Past Papers`

Preferred input:

- `Lecture Slides + Past Papers + Answer Keys`

Fallback input:

- `Lecture Notes PDF + Past Papers`

## Core Design Rules

- Count exactly **one primary knowledge point per question**.
- Keep **hotness** and **retention** separate.
- Use fixed retention bands instead of quartile-based retention stars.
- Keep generated outputs in **English only**.
- Surface weak cases in a **Review Queue** instead of hiding them.

## Retention Model

Retention fields are explicit:

- `years_present`
- `retention_fraction`
- `retention_percent`
- `meets_50`
- `meets_75`
- `retention_band`

Retention bands:

- `Anchor`: at least 75%
- `Core`: at least 50% and below 75%
- `Recurring`: more than one formal year but below 50%
- `One-off`: exactly one formal year
- `Not tested`: zero mapped hits

## Workflow

High-level workflow:

1. Read the course spec.
2. Prefer preset-backed slide extraction when a known preset exists.
3. Fall back to note-PDF extraction when slides are missing or weak.
4. Segment questions from papers.
5. Optionally OCR answer keys to validate or recover question mappings.
6. Merge candidate lines into optimized knowledge points.
7. Map each question to one primary knowledge point.
8. Compute hotness and retention statistics.
9. Export workbook, JSON, Markdown, and review queue.

Detailed workflow documentation is in [docs/workflow.md](./docs/workflow.md).

## Use Cases

Examples are documented in [docs/use-cases.md](./docs/use-cases.md).

Typical use cases:

- Known course with a preset and a slide deck
- Unknown course with only note PDFs and papers
- Formal papers plus auxiliary revision tests
- Partial answer-key coverage

## Repository Layout

- [SKILL.md](./SKILL.md): Codex skill instructions
- [agents/openai.yaml](./agents/openai.yaml): skill UI metadata
- [scripts/analyze_past_papers.py](./scripts/analyze_past_papers.py): main analyzer
- [scripts/vision_ocr.swift](./scripts/vision_ocr.swift): macOS Vision OCR helper
- [references/course-spec-schema.md](./references/course-spec-schema.md): public schema
- [references/presets.md](./references/presets.md): preset overview
- [references/specs/example-slides-and-papers.json](./references/specs/example-slides-and-papers.json): public example spec
- [references/specs/example-notes-and-papers.json](./references/specs/example-notes-and-papers.json): public example spec
- [tests/test_public_contract.py](./tests/test_public_contract.py): public tests

## Install

This repository is the public source-of-truth package. Use it directly or copy it into your local Codex skills directory.

Basic Python dependencies:

- `PyMuPDF`
- `python-pptx`
- `openpyxl`

The optional OCR helper requires:

- macOS
- `swiftc`
- Vision / PDFKit frameworks

## Run

Example:

```bash
python3 scripts/analyze_past_papers.py --spec references/specs/example-slides-and-papers.json
```

Replace the example spec with your own local runnable spec that contains real file paths.

## Public Tests

Run:

```bash
python3 -m unittest tests/test_public_contract.py
```

These tests are public-safe and do not depend on private course materials.

## Notes on Public vs Private Data

This repository does **not** include:

- private absolute file paths
- private benchmark outputs
- copyrighted course materials
- local-only helper scripts for one personal environment

You should create your own local runnable spec files outside this repository.
