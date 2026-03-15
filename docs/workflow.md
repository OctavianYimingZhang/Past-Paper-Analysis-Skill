# Workflow

This document describes how Codex works after the `past-paper-knowledge-point-analysis` skill is invoked. The workflow is not just a generic pipeline; it is a sequence for turning lecture materials and papers into a stable knowledge-point model that can support hotness and retention analysis.

## 1. Codex inspects the course spec and available sources

Codex first reads the course spec and determines which source types are available:

- `slides_dir`
- `notes_pdf`
- `papers[]`
- optional `answer_keys[]`

At this point, Codex is deciding what evidence it can trust, what is missing, and whether the run should behave like a preset-backed analysis or a generic one.

## 2. Codex chooses the lecture source strategy

Codex then chooses how to recover lecture structure.

- If a known preset exists and a usable `slides_dir` is present, Codex prefers slide extraction.
- If slide decks are missing, incomplete, or weak, Codex falls back to note-PDF extraction.
- If note text extraction is weak, Codex may use OCR as a fallback.

This decision matters because the lecture source determines how well the later knowledge-point split reflects the actual teaching structure.

## 3. Codex segments the lecture material

Codex next turns the lecture material into lecture-level units.

- With raw `.pptx` slide decks, Codex infers lecture order, lecture titles, and slide text directly.
- With note PDFs, Codex detects lecture boundaries from note structure and heading patterns.

The goal of this step is not yet to count topics. The goal is to recover the teaching structure well enough that each later knowledge point can still be traced back to a lecture context.

## 4. Codex divides each lecture into candidate knowledge points

Once the lecture structure is available, Codex scans the lecture content for candidate examinable statements. This is the first explicit “divide the lecture into knowledge points” step.

Codex looks for lines or fragments that behave like teachable units rather than boilerplate. It does not assume the lecture already contains clean topic labels. Instead, it proposes candidate knowledge points from the lecture material itself.

At this stage, the candidate set is intentionally broad. It is designed to capture the syllabus surface before question validation starts narrowing it.

## 5. Codex validates paper questions and segments the paper

Codex then moves to the past papers and segments them into question blocks.

Depending on the paper format, Codex may use:

- standard MCQ numbering
- grouped or shared-context question parsing
- explicit `question_numbers` sequences when printed numbering is irregular
- auxiliary-paper handling for revision tests or modified syllabus papers

This is the first validation step. If Codex cannot reliably recover the question blocks, every later mapping becomes unstable, so paper segmentation quality is treated as a core dependency rather than a cosmetic preprocessing step.

## 6. Codex uses answer keys to validate or recover question blocks

If answer keys are available, Codex extracts embedded images from the DOCX files and runs OCR over them. Codex then parses answer and explanation blocks.

Codex uses answer keys for three purposes:

- to validate that paper segmentation is consistent with the expected question sequence
- to strengthen topic mapping with answer and explanation text
- to recover placeholder question records when the paper OCR is too weak to segment a question directly

This means answer keys are optional, but when they exist they improve the reliability of both question validation and topic assignment.

## 7. Codex optimizes the knowledge-point split

At this point Codex has:

- lecture-derived candidate knowledge points
- question blocks from papers
- optional answer/explanation evidence from answer keys

Codex then normalizes, merges, and refines the candidate set into optimized knowledge points. This is the explicit “optimize knowledge-point separation” step.

The purpose is to avoid two common failure modes:

- one topic being split too finely and fragmenting the counts
- multiple distinct topics being merged into one vague label and blurring the statistics

Codex keeps the optimized set close enough to the lecture structure to remain explainable, but distinct enough to support stable counting.

## 8. Codex assigns one primary knowledge point per question

After the optimized point set is ready, Codex assigns each question to one primary knowledge point.

Codex may also record secondary or supporting points for context, but only the primary point drives the statistics. This rule is critical because it prevents the same question from inflating multiple frequency and retention counts.

This is the bridge between syllabus structure and exam behavior: every question becomes one counted vote for one optimized point.

## 9. Codex computes hotness

With the primary mappings in place, Codex computes hotness.

Hotness answers:

- How often is this topic tested?
- How much of the question set does it occupy?
- How does it rank relative to other tested topics?

Typical hotness outputs include:

- raw question hits
- yearly counts
- question-share percentage
- rank

## 10. Codex computes retention

Codex then computes retention separately from hotness.

Retention answers:

- In how many formal paper years does this topic appear?
- Does it cross the 50% recurrence boundary?
- Does it cross the 75% recurrence boundary?
- Is it an anchor topic, a core topic, a recurring topic, or a one-off topic?

By default, Codex computes retention against `formal` papers only. Auxiliary papers can still be analyzed, but they do not silently redefine recurrence.

## 11. Codex records uncertainty instead of hiding it

When Codex encounters weak or incomplete evidence, it does not quietly force a clean answer. Instead, it emits review items.

Codex records uncertainty when it sees problems such as:

- weak OCR confidence
- weak lecture extraction
- weak question segmentation
- missing or irregular question numbering
- weak lecture or knowledge-point mapping
- answer-key parse failures

This keeps the statistical outputs honest and makes the workflow easier to audit.

## 12. Codex exports the final analysis package

Finally, Codex exports three coordinated outputs:

- Excel workbook
- JSON analysis payload
- Markdown summary

Together, these outputs give the user:

- a readable revision summary
- a machine-readable analysis artifact
- a traceable review queue for anything that still needs human checking

In short, after the skill is invoked, Codex follows a full analysis loop: it divides lecture material into knowledge points, validates and segments the paper, optimizes where knowledge-point boundaries should sit, maps each question to one primary point, and then computes exam frequency and retention from that stable mapping.
