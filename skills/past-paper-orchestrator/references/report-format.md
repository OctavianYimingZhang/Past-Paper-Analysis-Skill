# Report Format — Analyst vs Student Mode

Both modes share a common spine. The differences are in front-matter density, whether the methodology appendix appears, and which prose register the spokes write in.

## Common spine (all modes)

```
1. Cover
   ├── Course title + course_id
   ├── Generated date + reference_year
   ├── n_papers, n_kps, n_patterns
   └── (analyst only) hyperparameter callout: lambda, tau, alpha, ref_year
2. Executive Summary  — one page max
3. KP Predictions Table
4. How It Will Be Tested (per-KP cheat-sheets)
5. Sensitivity & Warnings
6. Appendix A — Full KP Audit Table
7. Appendix B — Pattern Catalogue
```

## Analyst mode adds

```
8. Appendix C — Methodology
   ├── Recency-weighted hits
   ├── Moment-matched Beta posterior
   ├── Tier rules
   ├── Pattern-layer statistics
   └── Sensitivity sweep + leave-one-out
```

## Student mode drops / shrinks

- Cover: drops the hyperparameter callout (relegated to a single closing footnote).
- Executive summary: same content, friendlier prose register; jargon-free body.
- KP Predictions Table: same columns. Tier badges with one-word labels (`anchor`, `core`, etc.) plus a one-sentence "what this means" explanation column.
- How It Will Be Tested: SAME structure, but each spoke writes in student-mode register (see `voice-and-conviction.md`).
- Sensitivity & Warnings: compact — one paragraph instead of a table.
- Appendix A: kept (drill-down audit table).
- Appendix B: kept (pattern catalogue).
- Appendix C: **dropped**. Methodology stays in `references/methodology.md` for the curious user; the report no longer carries it.

## Per-KP cheat-sheet sub-section structure

Every cheat-sheet block (analyst and student) carries:

```
H2: <KP label> — <tier> (<posterior summary>)
  • Headline (one sentence, from cheatsheet-writer)
  • Narrative (4-7 sentences, from cheatsheet-writer)
  • How It Will Be Tested (3-5 sentences, from cheatsheet-writer)
  • Pattern Decomposition Table
      | pattern | tier | weighted hits | last seen | saturation | freshness |
  • Already Tested
      | year | Q# | pattern | complications used |
  • Still Possible
      | pattern | source | last seen | notes |
  • Approach (analyst: 2-3 sentences; from technique-coach)
  • Marks Walk (numbered list; from technique-coach)
  • Common Traps (bullets; from technique-coach)
  • Recommended Drills (5-8; from drill-curator)
  • Fresh-Pattern Challenges (1-2; from drill-curator)
  • Open Caveats (when posterior is wide / data is thin)
```

In **student mode**, the headers shift slightly:
- `How It Will Be Tested` → `What the question will look like`
- `Approach` → `How to attack it`
- `Marks Walk` → `Step-by-step (matches the mark scheme)`
- `Common Traps` → `Watch out for`
- `Recommended Drills` → `Drill these next`
- `Fresh-Pattern Challenges` → `Try one of these too`

## Length budgets

| Mode | Target page count | Word budget |
|------|-------------------|-------------|
| analyst, n_kp ≤ 30 | 25–35 pages | 8,000–11,000 |
| analyst, n_kp > 30 | 40–60 pages | 12,000–18,000 |
| student, n_kp ≤ 30 | 18–25 pages | 5,500–7,500 |
| student, n_kp > 30 | 30–45 pages | 9,000–13,000 |

If a generated DOCX falls outside these bounds, surface it as a quality warning.

## Bilingual blocks

- Stacked CN-then-EN, never side-by-side. The DOCX writer enforces this in `report_writer/_docx.py`.
- Bilingual blocks appear ONLY in the cheat-sheet section (per-KP narratives). Cover, executive summary, tables, and appendices stay English-only even when `--lang both`. Rationale: bilingual tables become unreadable; bilingual prose is the value-add.

## What never changes between modes

- The KP tiers and tier reasons.
- The pattern tiers and their rationales.
- The drill set IDs.
- The sensitivity sweep numbers.

Mode is a prose-register knob, not a data knob. Two reports for the same course — one analyst, one student — must be identical at the data level.
