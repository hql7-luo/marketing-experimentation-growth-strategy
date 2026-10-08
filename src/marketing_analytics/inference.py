"""Unadjusted randomized-arm contrasts with explicit comparison families.

The reported effect is the outcome mean in ``treatment`` minus that in
``reference``. Assignment, rather than observed engagement, defines each arm.
Binary outcomes use a pooled two-proportion z test and an unpooled normal
confidence interval. Continuous outcomes use Welch's unequal-variance t test
and its corresponding t interval. Holm p values and Bonferroni simultaneous
intervals each cover the three arm comparisons *within* one outcome; they do
not cover selection over segments, policies, or all outcomes together.

Methods: SciPy's ``ttest_ind(equal_var=False)`` documents Welch's test:
https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.ttest_ind.html
The pooled proportion test follows:
https://www.statsmodels.org/stable/generated/statsmodels.stats.proportion.proportions_ztest.html
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy import stats


COMPARISONS = ((1, 0), (2, 0), (1, 2))
BINARY_OUTCOMES = frozenset({"conversion", "visit"})
RESULT_COLUMNS = [
    "outcome",
    "treatment",
    "reference",
    "n_t",
    "n_c",
    "mean_t",
    "mean_c",
    "effect",
    "se",
    "ci_low",
    "ci_high",
    "p_value",
    "p_holm",
    "sim_ci_low",
    "sim_ci_high",
]


def _numeric_column(df: pd.DataFrame, name: str) -> np.ndarray:
    """Reject absent, nonnumeric, missing, and infinite observations."""
    if name not in df.columns:
        raise ValueError(f"Missing required column: {name}")
    if not pd.api.types.is_numeric_dtype(df[name]):
        raise ValueError(f"Column {name} must be numeric")
    try:
        values = df[name].to_numpy(dtype=float, na_value=np.nan)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Column {name} must contain finite numeric values") from exc
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError(f"Column {name} must contain finite numeric values")
    return values


def _holm(p_values: np.ndarray) -> np.ndarray:
    """Holm step-down adjusted p values, restored to their input order."""
    p_values = np.asarray(p_values, dtype=float)
    order = np.argsort(p_values, kind="stable")
    adjusted_sorted = np.maximum.accumulate(p_values[order] * np.arange(len(p_values), 0, -1))
    adjusted = np.empty_like(p_values)
    adjusted[order] = np.minimum(adjusted_sorted, 1.0)
    return adjusted


def contrasts(
    df: pd.DataFrame,
    outcomes: Sequence[str] = ("conversion", "visit", "spend"),
) -> pd.DataFrame:
    """Return all three pairwise arm contrasts for each requested outcome.

    ``action`` is 0 (No Email), 1 (Men's Email), or 2 (Women's Email).
    Every arm must have at least two rows. Missing data are errors rather than
    being silently removed. Binary outcome intervals are large-sample Wald
    intervals; sparse segments should not use this routine for confirmation.
    Nominal intervals cover one contrast at 95%; simultaneous intervals use
    alpha/3 for the three comparisons in that outcome.
    """
    if not isinstance(df, pd.DataFrame):
        raise ValueError("df must be a pandas DataFrame")
    if isinstance(outcomes, str) or not outcomes:
        raise ValueError("outcomes must be a nonempty sequence of column names")
    if len(set(outcomes)) != len(outcomes):
        raise ValueError("outcomes must not contain duplicate column names")
    actions = _numeric_column(df, "action")
    if not np.isin(actions, (0, 1, 2)).all():
        raise ValueError("action must contain only integer codes 0, 1, or 2")
    counts = {arm: int(np.sum(actions == arm)) for arm in (0, 1, 2)}
    if any(count < 2 for count in counts.values()):
        raise ValueError("Each action arm must contain at least two observations")

    rows = []
    for outcome in outcomes:
        values = _numeric_column(df, outcome)
        binary = outcome in BINARY_OUTCOMES
        if binary and not np.isin(values, (0, 1)).all():
            raise ValueError(f"Column {outcome} must contain only binary 0/1 outcomes")
        if outcome == "spend" and np.any(values < 0):
            raise ValueError("Column spend must be nonnegative")

        outcome_rows = []
        for treatment, reference in COMPARISONS:
            treated = values[actions == treatment]
            control = values[actions == reference]
            n_t, n_c = len(treated), len(control)
            mean_t, mean_c = float(treated.mean()), float(control.mean())
            effect = mean_t - mean_c

            if binary:
                variance = mean_t * (1.0 - mean_t) / n_t
                variance += mean_c * (1.0 - mean_c) / n_c
                se = float(np.sqrt(variance))
                pooled = (treated.sum() + control.sum()) / (n_t + n_c)
                null_se = float(np.sqrt(pooled * (1 - pooled) * (1 / n_t + 1 / n_c)))
                p_value = (
                    float(2 * stats.norm.sf(abs(effect / null_se)))
                    if null_se > 0
                    else (1.0 if effect == 0 else 0.0)
                )
                critical = float(stats.norm.ppf(0.975))
                simultaneous_critical = float(stats.norm.ppf(1 - 0.05 / 6))
            else:
                var_t = float(treated.var(ddof=1)) / n_t
                var_c = float(control.var(ddof=1)) / n_c
                variance = var_t + var_c
                se = float(np.sqrt(variance))
                if variance > 0:
                    dof = variance**2 / (var_t**2 / (n_t - 1) + var_c**2 / (n_c - 1))
                    p_value = float(2 * stats.t.sf(abs(effect / se), dof))
                    critical = float(stats.t.ppf(0.975, dof))
                    simultaneous_critical = float(stats.t.ppf(1 - 0.05 / 6, dof))
                else:
                    # A deterministic fixture has no estimated sampling spread.
                    p_value = 1.0 if effect == 0 else 0.0
                    critical = simultaneous_critical = 0.0

            outcome_rows.append(
                {
                    "outcome": outcome,
                    "treatment": treatment,
                    "reference": reference,
                    "n_t": n_t,
                    "n_c": n_c,
                    "mean_t": mean_t,
                    "mean_c": mean_c,
                    "effect": effect,
                    "se": se,
                    "ci_low": effect - critical * se,
                    "ci_high": effect + critical * se,
                    "p_value": p_value,
                    "sim_ci_low": effect - simultaneous_critical * se,
                    "sim_ci_high": effect + simultaneous_critical * se,
                }
            )
        adjusted = _holm(np.array([row["p_value"] for row in outcome_rows]))
        for row, p_holm in zip(outcome_rows, adjusted, strict=True):
            row["p_holm"] = float(p_holm)
        rows.extend(outcome_rows)
    return pd.DataFrame(rows, columns=RESULT_COLUMNS)
