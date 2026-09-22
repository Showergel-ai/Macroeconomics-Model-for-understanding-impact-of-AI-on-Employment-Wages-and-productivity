"""
Generates LaTeX-formatted tables for direct inclusion in the paper:

  1. Parameter table    -- all 6 parameters, values, abbreviated sources
  2. Scenario definitions table -- A and delta per scenario
  3. Results table       -- all outputs, per sector x scenario
  4. Sensitivity ranking -- parameters ranked by impact on employment change

Writes outputs/tables.tex.
"""

import os

from run_scenarios import run_all
from sensitivity import run_sweep
from parameters import PARAMS, SCENARIOS, SECTORS, SCENARIO_NAMES

OUT_DIR = "outputs"
OUT_PATH = os.path.join(OUT_DIR, "tables.tex")

SECTOR_LABEL = {"IT": "IT Services", "Agriculture": "Agriculture"}


def table_parameters() -> str:
    rows = [
        ("$\\alpha$ (task exposure)", f"{PARAMS['IT']['alpha']:.4f}", f"{PARAMS['Agriculture']['alpha']:.4f}",
         "Computed: PLFS(CWS) $\\times$ ILO GenAI exposure\\footnotemark[1]"),
        ("$\\pi$ (productivity gain)", f"{PARAMS['IT']['pi']:.2f}", f"{PARAMS['Agriculture']['pi']:.2f}",
         "NITI Aayog (2025); WEF Saagu Baagu (2025)"),
        ("$\\varepsilon$ (employment elasticity)", f"{PARAMS['IT']['epsilon']:.2f}",
         f"{PARAMS['Agriculture']['epsilon']:.2f}",
         "NITI Aayog (2025), Table 5.2 / 3.1\\footnotemark[2]"),
        ("$E_{\\text{baseline}}$ (workforce)", f"{PARAMS['IT']['E_baseline']:,}",
         f"{PARAMS['Agriculture']['E_baseline']:,}",
         "NASSCOM FY2025/26; NITI Aayog (PLFS 2023-24)"),
    ]

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Model parameters: IT services and Agriculture}",
        "\\label{tab:parameters}",
        "\\begin{tabular}{lrrl}",
        "\\toprule",
        "Parameter & IT & Agriculture & Source \\\\",
        "\\midrule",
    ]
    for name, it_val, agri_val, source in rows:
        lines.append(f"{name} & {it_val} & {agri_val} & {source} \\\\")
    lines += [
        "\\bottomrule",
        "\\end{tabular}",
        "\\footnotetext[1]{$\\alpha$ is a computed point estimate (survey-weighted PLFS/ILO "
        "occupational-exposure match), not a literature-sourced range; see Methodology.}",
        "\\footnotetext[2]{$\\varepsilon_{\\text{IT}}=0.79$ uses NITI Aayog's Computer \\& "
        "Information Services sub-sector elasticity (Table 5.2); the all-services aggregate "
        "(Table 3.1) gives $\\varepsilon_{\\text{IT}}=0.43$. Both are reported (see robustness check).}",
        "\\end{table}",
    ]
    return "\n".join(lines)


def table_scenarios() -> str:
    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Scenario definitions: adoption rate ($A$) and displacement fraction ($\\delta$)}",
        "\\label{tab:scenarios}",
        "\\begin{tabular}{lrrrr}",
        "\\toprule",
        " & \\multicolumn{2}{c}{IT} & \\multicolumn{2}{c}{Agriculture} \\\\",
        "Scenario & $A$ & $\\delta$ & $A$ & $\\delta$ \\\\",
        "\\midrule",
    ]
    for name in SCENARIO_NAMES:
        it = SCENARIOS[name]["IT"]
        agri = SCENARIOS[name]["Agriculture"]
        lines.append(f"{name} & {it['A']:.2f} & {it['delta']:.2f} & {agri['A']:.2f} & {agri['delta']:.2f} \\\\")
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    return "\n".join(lines)


def table_results(df) -> str:
    primary = df[df["variant"] == "primary"]

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Projected sector outcomes by scenario (2030)}",
        "\\label{tab:results}",
        "\\begin{tabular}{llrrrr}",
        "\\toprule",
        "Sector & Scenario & Productivity (\\%) & Employment (\\%) & Employment (abs.) & Wage (\\%) \\\\",
        "\\midrule",
    ]
    for sector in SECTORS:
        for scenario in SCENARIO_NAMES:
            row = primary[(primary["sector"] == sector) & (primary["scenario"] == scenario)].iloc[0]
            lines.append(
                f"{SECTOR_LABEL[sector]} & {scenario} & "
                f"{row['productivity_growth_pct']:.3f} & {row['employment_change_pct']:.3f} & "
                f"{row['employment_change_abs']:+,.0f} & {row['wage_growth_pct']:.3f} \\\\"
            )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    return "\n".join(lines)


def table_sensitivity_ranking(sens_df) -> str:
    sens_sorted = sens_df.sort_values(["sector", "range_pp"], ascending=[True, False])

    lines = [
        "\\begin{table}[htbp]",
        "\\centering",
        "\\caption{Sensitivity ranking: impact of each parameter on employment change (\\%), "
        "Moderate scenario, one parameter swept at a time}",
        "\\label{tab:sensitivity}",
        "\\begin{tabular}{llrrr}",
        "\\toprule",
        "Sector & Parameter & Low value & High value & Range (pp) \\\\",
        "\\midrule",
    ]
    for _, row in sens_sorted.iterrows():
        lines.append(
            f"{SECTOR_LABEL[row['sector']]} & {row['parameter']} & "
            f"{row['low_value']:.3f} & {row['high_value']:.3f} & {row['range_pp']:.3f} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}"]
    return "\n".join(lines)


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    results = run_all()
    sens = run_sweep()

    tex = "\n\n".join([
        table_parameters(),
        table_scenarios(),
        table_results(results),
        table_sensitivity_ranking(sens),
    ])

    with open(OUT_PATH, "w") as f:
        f.write(tex + "\n")

    print(f"Wrote {OUT_PATH}")
