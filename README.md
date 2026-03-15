# Past Paper Knowledge Point Analysis

`past-paper-knowledge-point-analysis` is an open-source Codex skill that turns lecture materials and past papers into an exam-oriented knowledge-point map. Instead of treating a course as a loose set of slides, notes, and old questions, the skill gives Codex a structured way to identify what the course actually tests, how often it tests it, and how reliably specific topics return across formal paper years.

In practice, the skill is built for a study workflow where a user has lecture slides or lecture-note PDFs, one or more past papers, and optionally answer keys. Codex uses those materials to reconstruct lecture structure, divide the course into optimized knowledge points, map each question to one primary point, and then compute hotness and retention from that stable mapping. The result is a more actionable revision model than either raw slides or raw papers can provide on their own.

The skill produces:

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

After the skill is invoked, Codex does not jump straight to counting. It follows a staged analysis loop that turns raw course materials into a stable question-to-topic model.

1. **Codex inspects the course spec and available sources.** Codex first checks whether the run has slide decks, note PDFs, papers, and answer keys, and decides what evidence is strong enough to trust.
2. **Codex chooses slide-first or notes-first extraction.** If a known preset exists and usable slide decks are available, Codex prefers slide extraction. If slides are missing, incomplete, or weak, Codex falls back to note-PDF extraction and may use OCR when needed.
3. **Codex segments the lecture material.** Codex reconstructs lecture boundaries so later knowledge points can still be traced back to real course structure instead of being treated as isolated text fragments.
4. **Codex divides each lecture into candidate knowledge points.** This is the first explicit “split the lecture into knowledge points” step. Codex looks for lines or fragments that behave like examinable units rather than boilerplate.
5. **Codex validates and segments the paper questions.** Depending on the paper format, Codex parses standard MCQ numbering, grouped/shared-context questions, explicit `question_numbers` sequences, and auxiliary papers such as revision tests. This is a validation step, not just preprocessing: if question segmentation is weak, later mapping becomes unstable.
6. **Codex uses answer keys, when available, to validate or recover question blocks.** Codex extracts embedded images from DOCX files, OCRs them, parses answer and explanation blocks, and uses that evidence to confirm question structure, strengthen topic mapping, or recover placeholder question records when paper OCR is weak.
7. **Codex optimizes knowledge-point separation.** Codex normalizes, merges, and refines candidate lines into optimized knowledge points. This is the explicit “optimize knowledge-point boundaries” step. The goal is to avoid splitting one topic too finely or merging multiple distinct topics into one vague bucket.
8. **Codex assigns one primary knowledge point per question.** Secondary or supporting points may still be recorded, but only the primary point drives the statistics. This preserves stable counting.
9. **Codex computes hotness.** Hotness measures how often a knowledge point is tested, how much of the question set it occupies, and how it ranks relative to other tested topics.
10. **Codex computes retention.** Retention measures how consistently a knowledge point reappears across formal paper years, and whether it crosses the 50% or 75% recurrence boundaries.
11. **Codex records uncertainty when the evidence is weak.** If OCR confidence is low, question numbering is irregular, or lecture/topic mapping is weak, Codex emits review items instead of pretending the result is clean.
12. **Codex exports the final analysis package.** The final outputs are a workbook, a JSON payload, and a Markdown summary built from the same primary-point mapping.

In short, Codex uses the skill to divide lecture material into knowledge points, validate and segment questions, optimize where those knowledge-point boundaries should sit, and then compute hotness plus retention from one stable question-to-point assignment.

## Use Cases

Typical use cases:

- **Known course with a preset and a slide deck.** Codex uses the preset-backed defaults to recover lecture structure and paper parsing more reliably.
- **Unknown course with only note PDFs and papers.** Codex falls back to generic extraction and relies more heavily on review gating because the lecture structure is weaker.
- **Slides plus papers, without answer keys.** The skill still runs, but Codex must rely more on lecture content and question stems, so uncertainty is higher.
- **Slides plus papers, with answer keys.** Answer-key OCR can validate paper segmentation and recover mappings when the paper itself is OCR-noisy or image-heavy.
- **Formal papers plus auxiliary revision tests.** Codex can analyze both, but default retention still uses formal papers unless the spec says otherwise.
- **Exam prioritization.** The output helps separate topics that are frequent, topics that are durable across years, and topics that are low-priority one-offs.

Hotness helps identify what is tested often. Retention helps identify what persists across years. They should be interpreted together, but they should not be collapsed into one score. Each question is still counted against one primary knowledge point only.

## What To Download And Use

This repository is already shaped as a runnable skill package. The files that matter for running the skill in Codex CLI or the Codex App are:

- `SKILL.md`
- `agents/openai.yaml`
- `scripts/analyze_past_papers.py`
- `scripts/vision_ocr.swift`
- `references/course-spec-schema.md`
- `references/presets.md`
- `references/specs/example-slides-and-papers.json`
- `references/specs/example-notes-and-papers.json`

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
