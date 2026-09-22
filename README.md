# Agentic AI Impact Model — India IT & Agriculture Sectors

A calibrated economic model estimating the impact of agentic AI on India's IT
services and Agriculture sectors by 2030, across three outcomes: sector
productivity growth, net employment change, and average wage growth.

Adapted from Acemoglu (2024), "The Simple Macroeconomics of AI." Every
non-scenario parameter is independently sourced or computed (see below);
adoption rate (`A`) and displacement fraction (`delta`) have no reliable
empirical values for 2030 and are run as explicit assumptions across three
scenarios (Conservative, Moderate, Aggressive).

## The three equations

All outputs are fractional changes (`x 100` for %). Subscript `s` = sector.

- **Eq. 1 — Productivity growth:** `dP/P = alpha * A * pi`
- **Eq. 2 — Net employment change:** `dE/E = -(alpha * A * delta) + epsilon * (alpha * A * pi)`
- **Eq. 3 — Average wage growth:** `dW/W = (alpha * A * pi) * (1 - delta)`

## Parameters

| Parameter | IT | Agriculture | Source |
|---|---|---|---|
| alpha (task exposure) | 0.5152 | 0.1640 | Computed: PLFS(CWS) x ILO GenAI exposure, matched via NCO-2015/ISCO-08 crosswalk |
| pi (productivity gain) | 0.15 | 0.21 | NITI Aayog (2025) SDLC study; WEF Saagu Baagu pilot (2025) |
| epsilon (employment elasticity) | 0.79 | 0.41 | NITI Aayog (2025), Table 5.2 (IT sub-sector) / Table 3.1 (Agriculture) |
| E_baseline (workforce) | 5,950,000 | 265,000,000 | NASSCOM Strategic Review FY2025/26; MoSPI FY25-26 1st advance estimate (61.6cr total employed x 43.0% agri share) |

`alpha` is a computed input, treated as fixed data — it is **not** re-derived
inside this codebase. It was produced by a separate, already-completed
pipeline: survey-weighted mean of ILO (Gmyrek, Berg & Pizzinelli 2025) GenAI
occupational-exposure scores, matched to PLFS Q2-Q4 2025 (Current Weekly
Status) worker records, filtered to NIC-2008 divisions 62+63 (IT) and
01+02+03 (Agriculture).

`epsilon_IT` is a stated methodological choice between two valid NITI Aayog
table figures (0.79 sub-sector vs. 0.43 all-services); both are reported —
see the robustness variant in `run_scenarios.py` output.

Scenario parameters (`A`, `delta`) are explicit assumptions bounded by cited
floor/ceiling arguments — see `parameters.py` for the full bounding logic.

## Running

```bash
source ../venv/bin/activate   # from inside agentic_ai_india_model/
cd agentic_ai_india_model      # if not already there
python run_scenarios.py        # prints + writes outputs/results.csv
python sensitivity.py          # prints + writes outputs/sensitivity.csv
python visualize.py            # writes 6 figures (PNG + PDF) to outputs/
python latex_tables.py         # writes outputs/tables.tex
```

## File structure

```
agentic_ai_india_model/
├── model.py            # Core computation functions (the 3 equations)
├── parameters.py        # All parameter values, sources, scenario definitions
├── run_scenarios.py      # Runs all 6 computations + IT robustness variant
├── sensitivity.py        # One-parameter-at-a-time sensitivity sweep
├── visualize.py          # All charts (matplotlib, publication style)
├── latex_tables.py       # Generates LaTeX table code
├── outputs/               # results.csv, sensitivity.csv, figures, tables.tex
└── README.md
```

## Design decisions

- **No Monte Carlo / stochastic simulation.** Deterministic calibration with
  scenario analysis — standard for applied economics papers at this level.
- **No optimization or fitting.** Parameters are sourced (or, for alpha,
  computed once from external data), not estimated against a target.
- **Ranges are for sensitivity analysis only**, not confidence intervals —
  the model has no statistical error term.
- **All fractions stored as fractions** (0.15, not 15%) internally; converted
  to % only for display/output.

## Model limitations

1. Partial equilibrium — no cross-sector labor flows modeled.
2. Wage equation assumes full productivity-to-wage pass-through for augmented
   workers; likely overestimates agricultural wage gains.
3. Static alpha — task exposure treated as fixed at its 2025 computed value
   but empirically expanding over time.
4. Historical employment elasticities may not hold under a structural break
   as large as widespread agentic AI adoption.
5. Within-sector heterogeneity (Tier-1 IT vs. BPO, commercial farms vs.
   subsistence) not captured by sector averages.
6. alpha is computed from Current Weekly Status (7-day recall) PLFS
   employment, not usual-status (365-day) employment, because the available
   extract lacked usual-status fields. This doesn't bias alpha's internal
   consistency (it's a weighted mean) but is a genuine data-availability
   limitation worth stating in the paper.
7. The occupation-title-to-ISCO-08-code mapping underlying alpha was built
   from the classification's documented structure, not independently
   verified line-by-line against ILO's own crosswalk table (unreachable from
   the working environment) — a residual, low-probability source of error in
   a small number of the 127 occupation groups.
8. epsilon_IT is a stated choice between two valid NITI Aayog table figures
   (sub-sector 0.79 vs. all-services 0.43); the paper should report both
   rather than presenting 0.79 as uncontested.

## Dependencies

Python 3.10+, numpy, pandas, matplotlib. No other dependencies.
