"""
All parameter values, sources, scenario definitions, and sensitivity sweep
ranges for the Agentic AI Impact Model (India IT & Agriculture sectors).

All fractions are stored as fractions (0.15, not 15%); conversion to percent
happens only at display/output time.

alpha is a computed input, not re-derived in this codebase. alpha_IT and
alpha_Agriculture were produced by a separate, already-completed pipeline:
survey-weighted mean of ILO (Gmyrek, Berg & Pizzinelli 2025) GenAI
occupational-exposure scores, matched to PLFS Q2-Q4 2025 (CWS) worker
records via the NCO-2015 <-> ISCO-08 crosswalk, filtered to NIC-2008
divisions 62+63 (IT) and 01+02+03 (Agriculture). See build spec / README
for full methodology and known limitations.
"""

# ---------------------------------------------------------------------------
# Fixed/sourced parameters -- same across all scenarios.
# ---------------------------------------------------------------------------
PARAMS = {
    "IT": {
        "alpha": 0.5152,          # Computed: PLFS(CWS) x ILO GenAI exposure, NIC 62+63
        "pi": 0.15,                # NITI Aayog (2025), "AI Economy": SDLC productivity +10-20%, midpoint
        "epsilon": 0.79,           # NITI Aayog (2025) Table 5.2: Computer & Info Services elasticity
        "E_baseline": 5_950_000,   # NASSCOM Strategic Review FY2025/26: tech-industry headcount
    },
    "Agriculture": {
        "alpha": 0.1640,           # Computed: PLFS(CWS) x ILO GenAI exposure, NIC 01+02+03
        "pi": 0.21,                 # WEF (2025) Saagu Baagu pilot: 21% avg yield improvement
        "epsilon": 0.41,            # NITI Aayog (2025) Table 3.1: Agriculture elasticity
        "E_baseline": 265_000_000,  # MoSPI FY25-26 1st advance estimate: 61.6cr total employed x 43.0% agri share [16][35]
    },
}

# Robustness-check alternate pairing for IT: broad NIC 61+62+63 alpha paired
# with the all-services (Table 3.1) elasticity, instead of the sub-sector
# pairing above (NIC 62+63 alpha with Table 5.2 elasticity). This is a
# genuine open methodological choice, not a correction -- report both.
ALT_IT_BROAD = {
    "alpha": 0.5011,
    "epsilon": 0.43,
}

# ---------------------------------------------------------------------------
# Scenario parameters (assumed) -- the two genuine 2030 unknowns. No source
# claims to know 2030 AI adoption depth (A) or displacement severity (delta)
# in advance; each is bounded by cited floor/ceiling arguments (see README).
# ---------------------------------------------------------------------------
SCENARIOS = {
    "Conservative": {
        "IT": {"A": 0.30, "delta": 0.10},
        "Agriculture": {"A": 0.05, "delta": 0.02},
    },
    "Moderate": {
        "IT": {"A": 0.50, "delta": 0.25},
        "Agriculture": {"A": 0.15, "delta": 0.05},
    },
    "Aggressive": {
        "IT": {"A": 0.70, "delta": 0.40},
        "Agriculture": {"A": 0.30, "delta": 0.10},
    },
}

# ---------------------------------------------------------------------------
# Sensitivity sweep ranges (one-parameter-at-a-time, all others held at
# Moderate-scenario values). alpha, pi, epsilon are point estimates (a
# computed figure, or a single reported figure/table), not literature
# ranges -- swept at +/-15% of their point value as an explicit artificial
# robustness band, not a sourced range. A and delta keep their full
# scenario-derived floor/ceiling bounds, since those are genuinely bounded
# by cited arguments.
# ---------------------------------------------------------------------------
SENSITIVITY_RANGES = {
    "IT": {
        "alpha":   (0.4379, 0.5925),  # +/-15% of 0.5152
        "pi":      (0.1275, 0.1725),  # +/-15% of 0.15
        "epsilon": (0.6715, 0.9085),  # +/-15% of 0.79
        "A":       (0.10, 0.90),
        "delta":   (0.05, 0.60),
    },
    "Agriculture": {
        "alpha":   (0.1394, 0.1886),  # +/-15% of 0.1640
        "pi":      (0.1785, 0.2415),  # +/-15% of 0.21
        "epsilon": (0.3485, 0.4715),  # +/-15% of 0.41
        "A":       (0.01, 0.50),
        "delta":   (0.01, 0.20),
    },
}

SECTORS = ("IT", "Agriculture")
SCENARIO_NAMES = ("Conservative", "Moderate", "Aggressive")
