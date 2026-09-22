"""
One-parameter-at-a-time sensitivity sweep.

For each sector, all parameters are held at their Moderate-scenario values
except the one being swept, which is set to its low and high bound from
SENSITIVITY_RANGES. Output metric is employment change % (Eq. 2), since
that is the outcome with sign-flip risk (productivity and wage growth are
monotonic in every parameter and never change sign).

Writes outputs/sensitivity.csv with one row per (sector, parameter),
sorted by impact magnitude descending -- the data behind the Chart 3
tornado plot.
"""

import pandas as pd

from model import compute
from parameters import PARAMS, SCENARIOS, SENSITIVITY_RANGES, SECTORS

MODERATE = "Moderate"


def _employment_change_pct(sector: str, **overrides) -> float:
    """Compute employment change % for `sector`, with Moderate-scenario
    baseline values overridden by whatever is passed in `overrides`."""
    p = PARAMS[sector]
    s = SCENARIOS[MODERATE][sector]
    kwargs = {
        "alpha": p["alpha"],
        "A": s["A"],
        "pi": p["pi"],
        "epsilon": p["epsilon"],
        "delta": s["delta"],
        "E_baseline": p["E_baseline"],
    }
    kwargs.update(overrides)
    return compute(**kwargs).employment_change_pct


def run_sweep() -> pd.DataFrame:
    rows = []
    for sector in SECTORS:
        for param, (low, high) in SENSITIVITY_RANGES[sector].items():
            change_at_low = _employment_change_pct(sector, **{param: low})
            change_at_high = _employment_change_pct(sector, **{param: high})
            rows.append({
                "sector": sector,
                "parameter": param,
                "low_value": low,
                "high_value": high,
                "employment_change_pct_at_low": change_at_low,
                "employment_change_pct_at_high": change_at_high,
                "range_pp": abs(change_at_high - change_at_low),
            })

    df = pd.DataFrame(rows)
    df = df.sort_values(["sector", "range_pp"], ascending=[True, False]).reset_index(drop=True)
    return df


if __name__ == "__main__":
    df = run_sweep()
    with pd.option_context("display.float_format", "{:.3f}".format,
                            "display.width", 120):
        print(df.to_string(index=False))
    df.to_csv("outputs/sensitivity.csv", index=False)
    print("\nWrote outputs/sensitivity.csv")
