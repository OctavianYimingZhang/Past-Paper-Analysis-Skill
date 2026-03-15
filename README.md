# Past Paper Knowledge Point Analysis

`past-paper-knowledge-point-analysis` is an open-source Codex skill for converting lecture materials and past papers into an exam-facing knowledge-point map. Instead of treating a course as a loose collection of slides, notes, and old questions, the skill turns those inputs into a structured view of what the course actually tests, how often it tests it, and how consistently specific topics recur across formal paper years.

In practice, the skill gives Codex a repeatable way to move from raw teaching material to revision priorities. Codex extracts lecture structure, proposes knowledge points, maps each question to one primary point, and then computes two separate signals: how often a point is tested and how reliably it returns across years. The result is a clearer study model than either raw slides or raw past papers can provide on their own.

The skill is designed for workflows built around:

- lecture slides or reorganized lecture notes
- past papers
- optional answer keys

It produces:

- lecture-to-topic maps
- one primary knowledge point per question
- topic hotness tables
- year-to-year retention bands
- review queues for weak OCR, weak parsing, or weak mappings

## Why This Skill Exists

Students usually have two useful but incomplete sources of truth.

- Lecture materials describe the syllabus, but they do not say which ideas are repeatedly examined.
- Past papers reveal repetition, but they do not explain how a question fits back into the course structure.

That gap matters. If a learner only reads slides, they often over-revise broad content without knowing which pieces are exam-active. If they only read past papers, they may see repeated question patterns without knowing how those patterns connect to lecture content. What is missing is a stable bridge between “what the course teaches” and “what the papers actually test.”

This skill is built to create that bridge. Codex divides lecture material into candidate knowledge points, validates paper questions against those points, optimizes where one knowledge point should be split from another, and then counts every question against one primary point. That one-question-one-primary-point rule is what makes the later statistics stable enough to act on. Without it, frequency counts become inflated, retention becomes ambiguous, and revision priorities become harder to justify.

## Core Design Rules

- Count exactly **one primary knowledge point per question**. The purpose of the mapping is to create stable statistics. If a single question is fully counted against multiple points, both frequency and retention are distorted. Secondary or supporting topics may still be recorded for context, but they do not drive the main counts.
- Keep **hotness** and **retention** separate. Hotness answers “How often is this topic tested?” Retention answers “How consistently does this topic reappear across formal years?” Those are related but not interchangeable signals. Merging them into one score makes it harder to tell whether a topic is common, durable, or both.
- Use fixed retention bands instead of quartile-based retention stars. Explicit thresholds create clearer revision decisions because they preserve meaningful boundaries such as 50% and 75%. Percentile buckets can be convenient summaries, but they often blur the difference between topics that are truly stable and topics that only appear stable relative to a noisy cohort.

These rules are the statistical contract of the skill: every later summary assumes that the question mapping obeys them.

## Retention Model

Retention is computed after Codex has assigned each question to one primary knowledge point. The numerator is the number of formal paper years in which that primary point appears at least once. The denominator is the number of formal paper years included in the course spec. By default, papers marked as `auxiliary` can still be analyzed for context, but they do not change the default recurrence baseline unless the spec explicitly chooses otherwise.

This matters because recurrence should describe how a topic behaves in the official year-to-year paper sequence, not how often it appears in every revision test, mock, or modified syllabus paper. That is why the skill keeps formal-year retention separate from broader analysis context.

Retention fields are explicit:

- `years_present`
- `retention_fraction`
- `retention_percent`
- `meets_50`
- `meets_75`
- `retention_band`

`years_present` is the exact count of formal years in which the primary knowledge point appears. `retention_fraction` and `retention_percent` make the numerator and denominator visible instead of hiding them inside a label. `meets_50` and `meets_75` exist because explicit thresholds are easier to use for revision decisions than quartile-style retention stars: a learner can immediately see whether a topic clears a meaningful recurrence boundary.

Retention bands are intentionally simple:

- `Anchor`: the topic appears in at least 75% of formal years, so it behaves like a highly stable core topic.
- `Core`: the topic appears in at least 50% but below 75% of formal years, so it recurs often enough to matter but is less stable than an anchor topic.
- `Recurring`: the topic appears in more than one formal year, but not often enough to clear the core threshold.
- `One-off`: the topic appears in exactly one formal year.
- `Not tested`: the topic has no mapped hits in the analyzed formal years.

## Workflow

The full Codex-centered workflow is documented in [docs/workflow.md](./docs/workflow.md).

At a high level, Codex:

1. inspects the course spec and available sources
2. extracts lecture structure from slides or notes
3. derives and optimizes knowledge points
4. validates and segments paper questions
5. uses answer keys when available to strengthen or recover mappings
6. assigns one primary knowledge point per question
7. computes hotness and retention separately
8. exports workbook, JSON, Markdown, and review queue outputs

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
