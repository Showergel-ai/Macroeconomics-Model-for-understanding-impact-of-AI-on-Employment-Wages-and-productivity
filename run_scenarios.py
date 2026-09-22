"""
Runs the model for every sector x scenario combination (6 runs), plus the
IT robustness variant using the broad-IT (alpha, epsilon) pairing.

Prints a results table to stdout and writes outputs/results.csv.
"""

import pandas as pd

from model import compute
from parameters import PARAMS, SCENARIOS, ALT_IT_BROAD, SECTORS, SCENARIO_NAMES


def run_all() -> pd.DataFrame:
    rows = []
    for sector in SECTORS:
        p = PARAMS[sector]
        for scenario_name in SCENARIO_NAMES:
            s = SCENARIOS[scenario_name][sector]
            result = compute(
                alpha=p["alpha"], A=s["A"], pi=p["pi"],
                epsilon=p["epsilon"], delta=s["delta"],
                E_baseline=p["E_baseline"],
            )
            rows.append({
                "sector": sector,
                "scenario": scenario_name,
                "alpha": p["alpha"],
                "A": s["A"],
                "pi": p["pi"],
                "epsilon": p["epsilon"],
                "delta": s["delta"],
                "E_baseline": p["E_baseline"],
                "productivity_growth_pct": result.productivity_growth_pct,
                "employment_change_pct": result.employment_change_pct,
                "employment_change_abs": result.employment_change_abs,
                "wage_growth_pct": result.wage_growth_pct,
                "variant": "primary",
            })

    # Robustness check: IT Moderate scenario, broad NIC 61+62+63 alpha paired
    # with the all-services (Table 3.1) epsilon, instead of the sub-sector
    # pairing used above.
    s = SCENARIOS["Moderate"]["IT"]
    result = compute(
        alpha=ALT_IT_BROAD["alpha"], A=s["A"], pi=PARAMS["IT"]["pi"],
        epsilon=ALT_IT_BROAD["epsilon"], delta=s["delta"],
        E_baseline=PARAMS["IT"]["E_baseline"],
    )
    rows.append({
        "sector": "IT",
        "scenario": "Moderate",
        "alpha": ALT_IT_BROAD["alpha"],
        "A": s["A"],
        "pi": PARAMS["IT"]["pi"],
        "epsilon": ALT_IT_BROAD["epsilon"],
        "delta": s["delta"],
        "E_baseline": PARAMS["IT"]["E_baseline"],
        "productivity_growth_pct": result.productivity_growth_pct,
        "employment_change_pct": result.employment_change_pct,
        "employment_change_abs": result.employment_change_abs,
        "wage_growth_pct": result.wage_growth_pct,
        "variant": "robustness_broad_alpha_epsilon",
    })

    return pd.DataFrame(rows)


def print_table(df: pd.DataFrame) -> None:
    display_cols = [
        "sector", "scenario", "variant",
        "productivity_growth_pct", "employment_change_pct",
        "employment_change_abs", "wage_growth_pct",
    ]
    with pd.option_context("display.float_format", "{:.3f}".format,
                            "display.width", 120):
        print(df[display_cols].to_string(index=False))


if __name__ == "__main__":
    results = run_all()
    print_table(results)
    results.to_csv("outputs/results.csv", index=False)
    print("\nWrote outputs/results.csv")
