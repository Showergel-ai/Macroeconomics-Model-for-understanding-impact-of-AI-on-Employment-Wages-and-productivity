"""
Core computation module for the Agentic AI Impact Model.

Implements the three equations adapted from Acemoglu (2024), "The Simple
Macroeconomics of AI":

    Eq. 1 -- Productivity growth:    dP/P = alpha * A * pi
    Eq. 2 -- Net employment change:  dE/E = -(alpha * A * delta) + epsilon * (alpha * A * pi)
    Eq. 3 -- Average wage growth:    dW/W = (alpha * A * pi) * (1 - delta)

where, for a given sector:
    alpha    fraction of tasks AI can technically handle (task exposure)
    A        fraction of exposed tasks actually adopted
    pi       productivity gain per automated task
    delta    fraction of automated tasks that eliminate a job (displacement)
    epsilon  employment elasticity of output (reinstatement channel)

All inputs and internal outputs are fractions (0.15, not 15%); conversion
to percent happens only in the returned *_pct fields.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelResult:
    productivity_growth_pct: float
    employment_change_pct: float
    employment_change_abs: float
    wage_growth_pct: float


def compute(alpha: float, A: float, pi: float, epsilon: float, delta: float,
            E_baseline: float) -> ModelResult:
    """Compute the three model outcomes for one sector under one scenario.

    Parameters
    ----------
    alpha : task exposure (fraction)
    A : adoption rate (fraction of exposed tasks actually automated)
    pi : productivity gain per automated task (fraction)
    epsilon : employment elasticity of output (fraction)
    delta : displacement fraction (fraction of automated tasks that eliminate jobs)
    E_baseline : baseline sector employment (headcount)

    Returns
    -------
    ModelResult with productivity growth %, employment change % and absolute
    headcount, and average wage growth %.
    """
    productivity_growth = alpha * A * pi
    employment_change = -(alpha * A * delta) + epsilon * (alpha * A * pi)
    wage_growth = (alpha * A * pi) * (1 - delta)

    return ModelResult(
        productivity_growth_pct=productivity_growth * 100,
        employment_change_pct=employment_change * 100,
        employment_change_abs=employment_change * E_baseline,
        wage_growth_pct=wage_growth * 100,
    )
