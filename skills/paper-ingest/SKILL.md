---
name: paper-ingest
description: >
  First spoke of the past-paper-analysis suite. Ingests course materials —
  past papers (PDF), lecture slides / notes (PDF), textbook (PDF, optional),
  and answer keys (DOCX, optional) — and emits structured JSON ready for KP
  derivation. Wraps Anthropic's official PDF skill where vision-aware
  extraction wins, falls back to local regex-based parsers (relaxed for
  short-answer + Warwick-style structured papers) when format is uniform.
  Mechanical, deterministic, no semantic judgement.
triggers:
  - extract past papers
  - paper ingest
  - paper extraction
  - extract lectures
  - extract textbook
  - extract answer keys
  - past-paper material ingest
---

# Paper Ingest — Material Extraction

## Output Language
English only.

## Purpose
Produce four JSON artefacts that downstream spokes consume:

| Output file | Source | Notes |
|-------------|--------|-------|
| `extracted-papers.json` | papers[] (PDF) | preserves question / part / marks structure for MCQ, short-answer, structured |
| `extracted-lectures.json` | lectures (PDF) | candidate topic list + per-topic coverage share |
| `extracted-textbook.json` | textbook (PDF, optional) | chapter index + worked-example index |
| `answer-key-ocr.json` | answer-keys (DOCX, optional) | OCR'd answer text + image dumps |

This skill is mechanical. Do not hand it to a judgment-heavy model — Haiku 4.5 is the right fit. The agent prompt is at `agents/ocr-extractor.md`.

## When to use

- **Standalone**: user wants to extract structured JSON from PDFs / DOCX without running the rest of the suite. Returns the four JSONs + a warning summary.
- **Embedded** (called by `past-paper-orchestrator`): same outputs, returns paths only so the orchestrator can hand them to `kp-pattern-mapper`.

## Inputs

```json
{
  "course_id": "<string>",
  "papers": [{"path": "...", "year": "2024", "session": "Jun"}, ...],
  "lectures": "/path/to/lecture-notes.pdf",
  "textbook": "/path/to/textbook.pdf",     // optional
  "answer_keys": ["/path/to/key.docx"],    // optional
  "output_dir": "/path/to/output"
}
```

## Outputs

Files written to `output_dir/`:
- `extracted-papers.json` (always)
- `extracted-lectures.json` (always)
- `extracted-textbook.json` (when textbook supplied)
- `answer-key-ocr.json` (when answer_keys supplied)

Plus a returned summary:
```json
{
  "ok": true,
  "n_papers": 11,
  "n_questions": 327,
  "n_topics": 64,
  "warnings": ["paper 2019.4 has no marks markers", ...]
}
```

## Implementation

The skill currently delegates to the existing CLI:

```bash
python3 -m scripts.analyze_past_papers extract-papers   --spec <spec>
python3 -m scripts.analyze_past_papers extract-lectures --spec <spec>
python3 -m scripts.analyze_past_papers extract-textbook --spec <spec>      # if textbook present
python3 -m scripts.analyze_past_papers extract-answer-keys --spec <spec>   # if keys present
```

Phase C will replace the primary PDF read path with a wrapped invocation of `anthropics-skills:pdf` for vision-aware extraction (multi-column physics papers and embedded LaTeX), and keep `scripts/extract_papers.py` as the post-processor that segments questions / parts / marks. The fallback survives because `anthropics-skills:pdf` does not segment exam papers by question number.

## Required reading

- `agents/ocr-extractor.md` — the Haiku 4.5 system prompt for the mechanical OCR runner.
- `references/extraction-schemas.md` — the schema each output JSON must satisfy. (Authored in Phase C; until then, the tests in `tests/test_extract_papers.py` and `tests/test_extract_textbook.py` are the de-facto contract.)

## Quality bar

- Parser tolerates MCQ (Edexcel IAL), short-answer (Manchester biology), and structured (Warwick-style PX275) formats. Regression suite at `tests/test_extract_papers.py` (27 tests) must stay green.
- Every paper has at least one extracted question or a `warning` field explaining why it didn't.
- Marks notation captures both `[4]` and `{4}` styles.
