"""
Publication-ready charts for the Agentic AI Impact Model.

Style: clean academic (no gridlines, minimal chrome, readable axis labels).
Saved as both PNG (300 dpi) and PDF into outputs/.

Colors follow a fixed categorical/status split, not eyeballed values:
  - Categorical (series identity: productivity / employment / wage):
    blue #2a78d6, orange #eb6834, aqua #1baf7a
  - Status (job gains vs. losses -- a good/bad signal, not "series 4"):
    good (gains) #0ca30c, critical (losses) #d03b3b
  - Ink: primary #0b0b0b, secondary #52514e, muted axis #898781,
    baseline/axis #c3c2b7
Every bar carries a direct value label, so the sub-3:1-contrast aqua slot
(used for wage growth) has the required relief channel.
"""

import os

import matplotlib.pyplot as plt
import pandas as pd

from run_scenarios import run_all
from sensitivity import run_sweep
from parameters import SECTORS, SCENARIO_NAMES

OUT_DIR = "outputs"

COLOR_PRODUCTIVITY = "#2a78d6"
COLOR_EMPLOYMENT = "#eb6834"
COLOR_WAGE = "#1baf7a"
COLOR_GAIN = "#0ca30c"
COLOR_LOSS = "#d03b3b"
INK_PRIMARY = "#0b0b0b"
INK_SECONDARY = "#52514e"
INK_MUTED = "#898781"
INK_BASELINE = "#c3c2b7"

SECTOR_LABEL = {"IT": "IT Services", "Agriculture": "Agriculture"}

plt.rcParams.update({
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.edgecolor": INK_BASELINE,
    "axes.labelcolor": INK_PRIMARY,
    "text.color": INK_PRIMARY,
    "xtick.color": INK_SECONDARY,
    "ytick.color": INK_SECONDARY,
    "axes.grid": False,
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
})


def _strip_chrome(ax, keep_bottom=True, keep_left=True):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if not keep_bottom:
        ax.spines["bottom"].set_visible(False)
    if not keep_left:
        ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color(INK_BASELINE)
    ax.spines["left"].set_color(INK_BASELINE)
    ax.tick_params(length=3, color=INK_BASELINE)


def _save(fig, name):
    fig.savefig(os.path.join(OUT_DIR, f"{name}.png"), dpi=300, bbox_inches="tight")
    fig.savefig(os.path.join(OUT_DIR, f"{name}.pdf"), bbox_inches="tight")
    plt.close(fig)


# ---------------------------------------------------------------------------
# Chart 1: Scenario comparison -- grouped bar chart (one per sector)
# ---------------------------------------------------------------------------
def chart1_scenario_comparison(df: pd.DataFrame):
    primary = df[df["variant"] == "primary"]

    for sector in SECTORS:
        sub = primary[primary["sector"] == sector].set_index("scenario").loc[list(SCENARIO_NAMES)]

        fig, ax = plt.subplots(figsize=(7, 4.5))
        x = range(len(SCENARIO_NAMES))
        width = 0.25

        ax.bar([i - width for i in x], sub["productivity_growth_pct"], width,
               label="Productivity growth", color=COLOR_PRODUCTIVITY)
        ax.bar(x, sub["employment_change_pct"], width,
               label="Employment change", color=COLOR_EMPLOYMENT)
        ax.bar([i + width for i in x], sub["wage_growth_pct"], width,
               label="Wage growth", color=COLOR_WAGE)

        ax.axhline(0, color=INK_BASELINE, linewidth=1, zorder=0)
        ax.set_xticks(list(x))
        ax.set_xticklabels(SCENARIO_NAMES)
        ax.set_ylabel("% change")
        ax.set_title(f"{SECTOR_LABEL[sector]}: Projected Impact by Scenario (2030)")
        ax.legend(frameon=False, loc="upper left", fontsize=9)
        _strip_chrome(ax)

        suffix = "IT" if sector == "IT" else "Agri"
        _save(fig, f"fig1_scenarios_{suffix}")


# ---------------------------------------------------------------------------
# Chart 2: Absolute employment impact -- horizontal bar chart
# ---------------------------------------------------------------------------
def chart2_employment_absolute(df: pd.DataFrame):
    primary = df[df["variant"] == "primary"].copy()
    # Order: sector, then scenario severity, top-to-bottom = Conservative first.
    order = [f"{SECTOR_LABEL[s]} -- {sc}" for s in SECTORS for sc in SCENARIO_NAMES]
    primary["label"] = pd.Categorical(primary["sector"].map(SECTOR_LABEL) + " -- " + primary["scenario"],
                                       categories=order, ordered=True)
    primary = primary.sort_values("label")

    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    y = range(len(primary))
    colors = [COLOR_GAIN if v >= 0 else COLOR_LOSS for v in primary["employment_change_abs"]]
    bars = ax.barh(list(y), primary["employment_change_abs"] / 1000, color=colors)

    ax.set_yticks(list(y))
    ax.set_yticklabels(primary["label"])
    ax.invert_yaxis()
    ax.axvline(0, color=INK_BASELINE, linewidth=1)
    ax.set_xlabel("Net employment change (thousands of jobs)")
    ax.set_title("Absolute Employment Impact by Sector and Scenario (2030)")
    ax.margins(x=0.18)  # headroom so bar-tip labels don't collide with y-axis tick text
    _strip_chrome(ax, keep_left=False)

    for bar, val in zip(bars, primary["employment_change_abs"]):
        label = f"{val/1000:+.0f}K"
        x_pos = bar.get_width()
        ha = "left" if x_pos >= 0 else "right"
        offset = 3 if x_pos >= 0 else -3
        ax.annotate(label, (x_pos, bar.get_y() + bar.get_height() / 2),
                    xytext=(offset, 0), textcoords="offset points",
                    va="center", ha=ha, fontsize=9, color=INK_PRIMARY)

    _save(fig, "fig2_employment_abs")


# ---------------------------------------------------------------------------
# Chart 3: Sensitivity tornado chart (one per sector)
# ---------------------------------------------------------------------------
PARAM_DISPLAY = {"alpha": "alpha", "pi": "pi", "epsilon": "epsilon", "A": "A", "delta": "delta"}


def chart3_tornado(sens_df: pd.DataFrame):
    for sector in SECTORS:
        sub = sens_df[sens_df["sector"] == sector].sort_values("range_pp")

        fig, ax = plt.subplots(figsize=(7, 3.5))
        y = range(len(sub))
        low = sub["employment_change_pct_at_low"].values
        high = sub["employment_change_pct_at_high"].values
        left = [min(a, b) for a, b in zip(low, high)]
        width = [abs(b - a) for a, b in zip(low, high)]

        ax.barh(list(y), width, left=left, color=COLOR_PRODUCTIVITY, height=0.6)
        ax.set_yticks(list(y))
        ax.set_yticklabels([PARAM_DISPLAY[p] for p in sub["parameter"]])
        ax.axvline(0, color=INK_BASELINE, linewidth=1)
        ax.set_xlabel("Employment change % (Moderate scenario, one parameter swept)")
        ax.set_title(f"{SECTOR_LABEL[sector]}: Sensitivity of Employment Change")
        right = [l + w for l, w in zip(left, width)]

        # barh sets a sticky edge at each bar's own left value, which
        # silently suppresses ax.margins() padding on that side -- set
        # xlim explicitly instead so left-edge labels get clear headroom.
        pad = 0.30 * (max(right) - min(left))
        ax.set_xlim(min(left) - pad, max(right) + pad)
        _strip_chrome(ax, keep_left=False)

        # Label each bar's left and right edge outward (away from the bar),
        # not by sweep-low/sweep-high identity -- those can land on either
        # side depending on whether the parameter's effect is monotonic in
        # the expected direction, and labeling by raw low/high would anchor
        # both texts inward and collide on narrow bars.
        for i, (a, b) in enumerate(zip(left, right)):
            ax.annotate(f"{a:.2f}", (a, i), xytext=(-4, 0), textcoords="offset points",
                        va="center", ha="right", fontsize=8, color=INK_SECONDARY)
            ax.annotate(f"{b:.2f}", (b, i), xytext=(4, 0), textcoords="offset points",
                        va="center", ha="left", fontsize=8, color=INK_SECONDARY)

        suffix = "IT" if sector == "IT" else "Agri"
        _save(fig, f"fig3_tornado_{suffix}")


# ---------------------------------------------------------------------------
# Chart 4: IT vs Agriculture divergence -- side-by-side panel
# ---------------------------------------------------------------------------
def chart4_divergence(df: pd.DataFrame):
    primary = df[df["variant"] == "primary"]

    fig, axes = plt.subplots(1, 2, figsize=(11, 4.5), sharey=True)
    width = 0.25
    x = range(len(SCENARIO_NAMES))

    for ax, sector in zip(axes, SECTORS):
        sub = primary[primary["sector"] == sector].set_index("scenario").loc[list(SCENARIO_NAMES)]
        ax.bar([i - width for i in x], sub["productivity_growth_pct"], width,
               label="Productivity growth", color=COLOR_PRODUCTIVITY)
        ax.bar(x, sub["employment_change_pct"], width,
               label="Employment change", color=COLOR_EMPLOYMENT)
        ax.bar([i + width for i in x], sub["wage_growth_pct"], width,
               label="Wage growth", color=COLOR_WAGE)
        ax.axhline(0, color=INK_BASELINE, linewidth=1, zorder=0)
        ax.set_xticks(list(x))
        ax.set_xticklabels(SCENARIO_NAMES)
        ax.set_title(SECTOR_LABEL[sector])
        _strip_chrome(ax)

    axes[0].set_ylabel("% change")
    axes[0].legend(frameon=False, loc="upper left", fontsize=9)
    fig.suptitle("IT vs. Agriculture: Structural Divergence Across Scenarios (2030)", y=1.02)

    _save(fig, "fig4_divergence")


if __name__ == "__main__":
    os.makedirs(OUT_DIR, exist_ok=True)
    results = run_all()
    sens = run_sweep()

    chart1_scenario_comparison(results)
    chart2_employment_absolute(results)
    chart3_tornado(sens)
    chart4_divergence(results)

    print(f"Wrote 6 figures (PNG + PDF) to {OUT_DIR}/")
