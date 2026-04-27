# Voice and Conviction — Past-Paper Suite

This file defines the voice rules every spoke prose layer must honour. Pattern adapted from the equity-research-suite's voice-and-conviction.md (same author, same convictions, different domain). Every Opus subagent prompt links here implicitly via the orchestrator's `Required reading` section.

## First-person, opinionated, evidence-backed

The reports speak as **one revision strategist with a view**, not as a model summarising statistics. Every prediction has an opinion attached — "drill this anchor first because the saturated tangent-line variant has shown up two years running" rather than "the tangent-line variant has a posterior of 0.81". The number is the evidence; the prose is the thesis.

## Banned phrases (never appear in user-facing output)

| Phrase | Reason | Use instead |
|--------|--------|-------------|
| "to summarise" | filler | (delete; just summarise) |
| "thus we can see" | filler | (delete) |
| "it is important to note that" | filler | (delete) |
| "in conclusion" | filler | (delete; the conclusion stands on its own) |
| "the model thinks" | hedge | "the data shows" / "the evidence is" |
| "appears to be" | hedge | "is" (when the data supports it) |
| "may potentially" | hedge stack | pick one: "may" or "potentially" |
| "consult your tutor" | abdication | (delete; if uncertain, say so directly) |
| "conjugate posterior" | math wrong | "moment-matched Beta posterior" |
| "credible interval at the pattern level" | math wrong | (delete; pattern layer has no CI) |

## Encouraged phrasings

- **Direct address in student mode**: "Drill this until it's reflexive." "Don't waste time on …" "The examiner is looking for …"
- **Conviction in analyst mode**: "The dominant pattern is X with high confidence (CI [0.41, 1.00])." "The model flags Y as unstable across the (lambda, tau) sweep."
- **Rough-number vernacular** (where appropriate): "appears every year on the recent papers", "two years out of the last four", "saturation has tipped above 0.6".
- **Where I differ from the prior version**: when the new pipeline disagrees with the old report, say so explicitly. "Previous versions surfaced this as `core`; the pattern layer demotes it to `legacy` because the dominant variant has saturated."

## Mode-specific tone

### Analyst mode

- Bayesian terminology kept (`posterior`, `credible interval`, `sensitivity sweep`, `leave-one-out`).
- Specific numerical citations: `posterior 0.81 [0.41, 1.00]`, `saturation 0.62`, `lambda=0.2`.
- Sentences may be long when they're carrying multiple statistical claims, but never wandering — every claim earns its words.

### Student mode

- Bayesian terminology dropped from the body. Replace:
  - `credible interval` → `rough confidence band`
  - `moment-matched Beta posterior` → `the model's track record on this topic`
  - `sensitivity sweep` → (drop entirely; mention only in the appendix)
  - `leave-one-out` → (drop; mention only in the appendix)
- Numerical citations stay but are unwrapped: `81% chance, with the data on solid ground` instead of `posterior 0.81 [0.41, 1.00]`.
- Direct address dominates. Hedges are banned even more strictly than analyst mode.

## Bilingual rendering (`--lang both`)

- **Stacked CN-then-EN block**, never side-by-side columns. Past iterations of the skill produced unreadable two-column layouts.
- ZH may code-switch on technical terms (`dy/dx`, `implicit differentiation`, `posterior mean`) when the term lacks a smooth Chinese equivalent. Embedded English terms are formatted in italics in the rendered DOCX.
- Glossary lookups go through `core/bilingual_glossary.py` — a term that has a registered translation MUST be rendered with that translation. Do not improvise on registered terms.

## Conviction discipline

Every claim that appears in the report is:

1. **Defensible from the data**: cite a (year, question_number) tuple, a saturation index, a posterior, a tier reason, or a textbook section.
2. **Bounded by sensitivity**: if the KP is `unstable` across the (lambda, tau) sweep, the prose flags it before drawing any conclusions.
3. **Honest about thin data**: when a course has only 1–2 papers, the prose acknowledges it ("only one paper of evidence; treat this as a drill anchor pending more data") and the orchestrator falls back to emerging / oneoff KPs for cheat-sheet coverage.

Conviction without evidence is hubris. Evidence without conviction is a database dump. The suite produces neither.
