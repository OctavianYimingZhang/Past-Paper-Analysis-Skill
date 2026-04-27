---
name: stat-engine
description: >
  Third spoke of the past-paper-analysis suite. Pure-Python statistical
  layer: KP-level moment-matched Beta posteriors, sensitivity sweeps,
  leave-one-out stability, and pattern-level frequency + saturation +
  freshness statistics. NO LLM calls. All logic delegates to the shared
  core/ package (statistical_model.py, sensitivity.py, pattern_coverage.py)
  so the math is auditable and unit-tested in isolation.
triggers:
  - statistical analysis
  - bayesian analysis
  - posterior analysis
  - pattern coverage
  - tier assignment
  - past paper statistics
---

# Stat Engine — Pure-Python Statistical Layer

## Output Language
English only.

## Purpose
Turn `extracted-papers.json` + `mapping.json` + `patterns.json` into:

- **`pattern-coverage.json`** — per (kp_id, pattern_id) cell: `raw_hits`, `weighted_hits`, `last_seen_year`, `first_seen_year`, `inter_arrival_years_*`, `variation_diversity`, `saturation_index`, `freshness_flag`, `predicted_score`, `complications_seen`, `complications_unseen`, `pattern_tier` (`saturated` / `hot` / `fresh` / `dormant`).
- **`<course_id>-analysis.json`** — per KP: `posterior_mean`, `ci_lower_95`, `ci_upper_95`, `tier`, `tier_reasons`, `sensitivity_band`, `warnings`, `trend`, `hotness[year]`, `pattern_coverage[]`. Plus the suite-level (lambda, tau) sensitivity sweep and leave-one-out table.

**Critical invariant**: this skill MUST NOT delegate to an LLM. KP-level Bayesian math and pattern-level coverage math are pure Python. If the orchestrator catches itself asking a subagent to do statistics, stop and run the CLI instead.

## When to use

- **Standalone**: user already has `patterns.json` + `mapping.json` + `extracted-papers.json` and wants the analysis JSONs. Returns the two output files + an executive table summarising tier distribution.
- **Embedded** (called by `past-paper-orchestrator`): same output, paths only.

## Inputs

```json
{
  "extracted_papers": "/path/to/extracted-papers.json",
  "kps":              "/path/to/kps.json",
  "patterns":         "/path/to/patterns.json",
  "mapping":          "/path/to/mapping.json",
  "output_dir":       "/path/to/output",
  "hyperparameters": {
    "lambda": 0.2,                  // recency decay, default 0.2
    "tau":    1.0,                  // prior strength, default 1.0
    "alpha":  0.3,                  // examiner-novelty bias, default 0.3
    "reference_year": 2026
  }
}
```

## Outputs

Files in `output_dir/`:
- `pattern-coverage.json`
- `<course_id>-analysis.json`

Returned summary:
```json
{
  "ok": true,
  "n_kps": 64,
  "tier_distribution": {"anchor": 8, "core": 22, "emerging": 10, "legacy": 6, "oneoff": 4, "not_tested": 14},
  "n_unstable": 3,
  "n_fresh_patterns": 11,
  "n_saturated_patterns": 22,
  "lambda": 0.2, "tau": 1.0, "alpha": 0.3, "reference_year": 2026
}
```

## Implementation

```bash
python3 -m scripts.analyze_past_papers pattern-coverage --spec <spec>
python3 -m scripts.analyze_past_papers analyze --spec <spec>
```

Both subcommands import directly from `core/`:
- `core.statistical_model.weighted_beta_posterior`, `assign_tier`, `analyze_kp`, `with_sensitivity_band`
- `core.pattern_coverage.compute_kp_pattern_coverage`, `coverage_to_jsonable`
- `core.sensitivity.sensitivity_sweep`, `leave_one_out`, `summarize_loo_for_report`, `summarize_sweep_for_report`

## Statistical contract

Lifted verbatim from `skills/past-paper-orchestrator/references/methodology.md`:

- **KP layer**: moment-matched Beta posterior under recency-weighted hits. Always carries a credible interval. Word "conjugate" is banned in user-facing output (it is an approximation, not a strict conjugate update).
- **Pattern layer**: weighted hit count + saturation index + freshness flag + predicted score. NO credible interval. With ≤ 5 hits per cell, a Beta posterior is uselessly wide; the suite is honest about that.
- **Tier rules**: `tier_reasons` list is authoritative. Tiers are computed deterministically from the rules in `skills/past-paper-orchestrator/references/tier-definitions.md`.
- **Sensitivity sweep**: lambda ∈ {0, 0.2, 0.4} × tau ∈ {0.5, 1.0, 2.0} (9 cells) by default. KPs that flip tiers across the sweep are tagged `unstable` and surfaced first.
- **Leave-one-out**: re-runs the analysis with each paper removed in turn. Cells flagged where any single paper flips the tier.

## Required reading

- `skills/past-paper-orchestrator/references/methodology.md` — full math.
- `skills/past-paper-orchestrator/references/tier-definitions.md` — KP + pattern tier rules.
- `core/statistical_model.py`, `core/pattern_coverage.py`, `core/sensitivity.py` — the actual implementations. Unit tests at `tests/test_statistical_model.py`, `tests/test_pattern_coverage.py`, `tests/test_sensitivity.py` (≥ 60 tests collectively, all green).

## Quality bar

- All 60+ statistical tests in `tests/` stay green at every commit.
- No LLM call in this skill. If the user's prompt makes you reach for one, stop.
- Every KP in the output JSON has a non-empty `tier_reasons` list.
- Every (KP, pattern) cell has a `pattern_tier`.
