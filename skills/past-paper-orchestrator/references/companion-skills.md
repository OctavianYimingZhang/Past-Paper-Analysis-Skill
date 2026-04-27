# Companion Skills — When to Invoke

The seven core spokes (paper-ingest, kp-pattern-mapper, stat-engine, cheatsheet-writer, drill-curator, technique-coach, report-renderer) cover the canonical pipeline. Several installed Anthropic skills can extend the suite when the user wants more depth on a specific stage. Invoke them on user request OR when the orchestrator detects a clear signal — never silently.

## High-signal companions (installed, verified)

| Skill | When to invoke | What it adds |
|-------|----------------|--------------|
| `anthropics-skills:pdf` | Material ingest fails on a multi-column physics paper or LaTeX-heavy short-answer exam | Vision-aware PDF extraction. Handles equations, figure captions, and mixed-column layouts the local regex parser misses. |
| `anthropics-skills:docx` | The user wants a polished DOCX with Anthropic-grade formatting fidelity | Replaces the local `report_writer/_docx.py` body. Local writer keeps the executive-summary + cheat-sheet section logic; the official skill handles the DOCX serialisation. |
| `anthropics-skills:xlsx` | The user wants an audit XLSX with Anthropic-grade formatting | Replaces local openpyxl code. |
| `anthropics-skills:skill-creator` | The user wants to extend the suite with a new specialist | Scaffolds frontmatter + folder structure that matches Anthropic conventions. |
| `anthropics-skills:doc-coauthoring` | The user wants to co-edit the rendered DOCX section by section | Structured Q&A flow over the generated report. |
| `data:statistical-analysis` | The user asks for deeper diagnostics on the posteriors (calibration, posterior predictive checks, MCMC diagnostics) | Goes beyond the moment-matched Beta into PyMC territory. Use only when the user explicitly wants this. |
| `eval-harness` | The user wants regression coverage on the suite itself | Sandboxed regression tests against PX275 / M1 / P4 fixtures. |

## When NOT to invoke

- Don't invoke `data:statistical-analysis` for routine runs — it's slower and produces output the cheat-sheet writer doesn't consume.
- Don't invoke `anthropics-skills:pdf` when the local parser already produces a clean `extracted-papers.json`. The wrap exists for failure cases, not as the default.
- Don't invoke `anthropics-skills:doc-coauthoring` until the user has actually read the first generated DOCX. Co-authoring without a baseline wastes context.

## How to invoke

Companions are dispatched via the `Skill` tool, exactly like a core spoke. Pass the relevant input payload; expect a return value the orchestrator can splice into the merged document.

```
Skill(skill="anthropics-skills:docx", args={"cards": ..., "format_spec": ...})
```

When a companion replaces a core spoke's output (e.g. the DOCX writer), the orchestrator dispatches the companion BEFORE `report-renderer` and passes the companion's output as part of the renderer's input. The renderer then becomes a thin merger.

## Verification before any companion lift

If a companion is invoked AND its output ships in the final report, the suite owes a row in `references/external-borrowings.md` documenting:

- Companion skill name and version
- License (must be MIT / Apache / explicitly permissive)
- Last-known-good test (e.g. "smoke test against PX275 fixture passed on 2026-04-27")
- Which output of the companion was actually used

This is governance, not bureaucracy — past iterations of the suite shipped silent dependencies on tools that later became unavailable. The borrowings log prevents that.
