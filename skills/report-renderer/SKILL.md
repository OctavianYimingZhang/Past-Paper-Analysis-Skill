---
name: report-renderer
description: >
  Final spoke of the past-paper-analysis suite. Renders the merged
  cheatsheet + drill + coaching payload into multi-format deliverables
  (Markdown, DOCX, XLSX, JSON). Wraps Anthropic's official docx + xlsx
  skills where they win on file fidelity, and uses the local
  scripts/report_writer/ package for report-specific layout (executive
  summary, per-KP cheat-sheet section, sensitivity appendix). Honours
  analyst vs student mode and the `--lang` flag.
triggers:
  - report renderer
  - report assembly
  - render report
  - render docx
  - render xlsx
  - past paper report renderer
---

# Report Renderer — Multi-Format Deliverables

## Output Language
Per `--lang` flag from the orchestrator. Default: English only. Bilingual blocks on `--lang both`.

## Purpose
Take the structured payloads from `stat-engine` + `cheatsheet-writer` + `drill-curator` + `technique-coach` and produce four files in `output_dir/`:

| Format | Purpose | Audience |
|--------|---------|----------|
| `<course_id>-analysis.docx` | Headline revision-plan deliverable | Student |
| `<course_id>-analysis.xlsx` | Drill-down audit table (every posterior, every sweep cell) | Power user / re-runner |
| `<course_id>-analysis.md` | Git-friendly diff format | Maintainer |
| `<course_id>-analysis.json` | Machine-readable; reproduces the other three deterministically | Pipeline re-runs |

## When to use

- **Standalone**: user already has all the JSON payloads and wants the four files.
- **Embedded** (called last by `past-paper-orchestrator`): same output, paths only.

## Inputs

```json
{
  "analysis":         "/path/to/<course_id>-analysis.json",
  "pattern_coverage": "/path/to/pattern-coverage.json",
  "patterns":         "/path/to/patterns.json",
  "mapping":          "/path/to/mapping.json",
  "cards":            [/* cheatsheet cards from cheatsheet-writer */],
  "drills":           [/* drill sets from drill-curator */],
  "coaching":         [/* coaching entries from technique-coach */],
  "course_meta":      {/* course_id, course_name, reference_year, n_papers, ... */},
  "lang":             "en",
  "mode":             "analyst",
  "output_dir":       "/path/to/output"
}
```

## Outputs

Files written to `output_dir/`:
- `<course_id>-analysis.md`
- `<course_id>-analysis.docx`
- `<course_id>-analysis.xlsx`
- `<course_id>-analysis.json`

Returned summary:
```json
{
  "ok": true,
  "files": {
    "md":   "/.../course-analysis.md",
    "docx": "/.../course-analysis.docx",
    "xlsx": "/.../course-analysis.xlsx",
    "json": "/.../course-analysis.json"
  },
  "executive_headline": "...",
  "n_paragraphs": 219,
  "n_tables": 23
}
```

## Implementation

Today the renderer calls into `scripts/report_writer/`:
- `write_markdown(...)` — `_markdown.py`
- `write_docx(...)` — `_docx.py`
- `write_excel(...)` — `__init__.py` (openpyxl)
- `write_json(...)` — `__init__.py` (json)

Phase C will refactor `_docx.py` and the xlsx writer to delegate the file-format-specific work to `anthropics-skills:docx` and `anthropics-skills:xlsx` respectively. The local `report_writer/_common.py` keeps the report-specific layout logic (executive summary derivation, top-focus-KP selection, fallback behaviour) since no installed skill knows what a past-paper analysis section structure looks like.

## Layout contract (analyst mode)

1. Cover (course_id, generated_at, n_papers, n_kps, n_patterns).
2. Compact executive summary (headline, top focus KPs, fresh-pattern targets, caveat bullets).
3. KP predictions table (label, tier, posterior, n_papers, sensitivity).
4. **How It Will Be Tested** — per-KP cheat-sheet cards + drill set + coaching prose stitched into one section per KP.
5. Sensitivity & warnings.
6. Appendix A — full audit table.
7. Appendix B — pattern catalogue.
8. Appendix C — methodology.

## Layout contract (student mode)

1. Cover.
2. Top focus KPs (with drills front-loaded).
3. **How It Will Be Tested** — same structure as analyst, but with the student-mode prose from each spoke.
4. Sensitivity & warnings (compact one-paragraph version).
5. Appendix — full audit table only.
6. (Methodology appendix dropped.)

## Required reading

- `references/render-format.md` — analyst vs student layout spec (authored in Phase C; until then, `scripts/report_writer/_common.py` is the de-facto contract).
- `scripts/report_writer/_docx.py`, `_markdown.py`, `_common.py` — the implementation.
- `tests/test_report_writer_docx.py` — 8 tests verifying section order, fallback behaviour, label resolution.

## Quality bar

- DOCX has the same structural fingerprint (≥ heading hierarchy, ≥ table count) as the v0.1 monolithic skill, plus populated `drill-set` and `technique-prose` sections.
- Bilingual rendering uses stacked CN-then-EN blocks. Never side-by-side columns (regression contract from v0.1).
- All 8 DOCX renderer tests stay green.
