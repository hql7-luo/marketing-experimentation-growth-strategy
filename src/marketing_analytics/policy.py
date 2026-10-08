"""Held-out evaluation of fixed targeting rules using randomized assignments.

For row i, the incremental Horvitz-Thompson score against No Email is
``Y_i * (1[A_i = policy(X_i)] - 1[A_i = 0]) / p(A_i)``.
The estimator averages over *all* evaluation rows, including policy-selected
No Email rows whose score is exactly zero. Estimated uncertainty is the sample
standard deviation of the paired scores divided by sqrt(n). Normal intervals
are pointwise large-sample intervals and do not adjust for policy selection.

Rules must be frozen using independent training data before outcomes in this
evaluation frame are inspected. This module evaluates supplied actions; it
does not fit or select a policy. It cannot verify the provenance of an action
array, so the reproducible pipeline must enforce the train/test boundary.
"""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pandas as pd
from scipy.stats import norm


DEFAULT_PROBABILITIES = (1 / 3, 1 / 3, 1 / 3)


def _probabilities(probabilities: Sequence[float]) -> np.ndarray:
    try:
        values = np.asarray(probabilities, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError("probabilities must contain three numeric probabilities") from exc
    if values.shape != (3,) or not np.isfinite(values).all():
        raise ValueError("probabilities must contain three finite probabilities")
    if np.any(values <= 0) or not np.isclose(values.sum(), 1.0, rtol=0, atol=1e-10):
        raise ValueError("probabilities must be positive and sum to one")
    return values


def _actions(values: Sequence[int], n: int, name: str) -> np.ndarray:
    try:
        array = np.asarray(values, dtype=float)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain integer action codes") from exc
    if array.shape != (n,):
        raise ValueError(f"{name} must have one action per evaluation row")
    if not np.isfinite(array).all() or not np.isin(array, (0, 1, 2)).all():
        raise ValueError(f"{name} must contain only integer codes 0, 1, or 2")
    return array.astype(int)


def _outcome(df: pd.DataFrame, name: str) -> np.ndarray:
    if name not in df.columns or not pd.api.types.is_numeric_dtype(df[name]):
        raise ValueError(f"Outcome {name} must be a numeric column")
    try:
        values = df[name].to_numpy(dtype=float, na_value=np.nan)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Outcome {name} must contain finite numeric values") from exc
    if values.ndim != 1 or not np.isfinite(values).all():
        raise ValueError(f"Outcome {name} must contain finite numeric values")
    if name in {"conversion", "visit"} and not np.isin(values, (0, 1)).all():
        raise ValueError(f"Outcome {name} must contain only binary 0/1 values")
    if name == "spend" and np.any(values < 0):
        raise ValueError("Outcome spend must be nonnegative")
    return values


def _validated_inputs(
    df: pd.DataFrame,
    actions: Sequence[int],
    probabilities: Sequence[float],
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not isinstance(df, pd.DataFrame) or len(df) == 0:
        raise ValueError("df must be a nonempty pandas DataFrame")
    if "action" not in df.columns or not pd.api.types.is_numeric_dtype(df["action"]):
        raise ValueError("action must be a numeric column")
    try:
        observed_values = df["action"].to_numpy(dtype=float, na_value=np.nan)
    except (TypeError, ValueError) as exc:
        raise ValueError("action must contain integer codes 0, 1, or 2") from exc
    observed = _actions(observed_values, len(df), "observed action")
    # Series are accepted only with exactly the same index to make alignment
    # mistakes visible; plain arrays explicitly use DataFrame row order.
    if isinstance(actions, pd.Series) and not actions.index.equals(df.index):
        raise ValueError("Action Series index must match evaluation DataFrame index")
    chosen = _actions(actions, len(df), "policy actions")
    probabilities_array = _probabilities(probabilities)
    return observed, chosen, probabilities_array


def policy_scores(
    df: pd.DataFrame,
    actions: Sequence[int],
    outcome: str = "spend",
    probabilities: Sequence[float] = DEFAULT_PROBABILITIES,
) -> np.ndarray:
    """Return per-row incremental scores against No Email in frame row order.

    Probabilities are the design probabilities for codes 0, 1, and 2, not the
    realized arm frequencies or an estimate learned from evaluation outcomes.
    A Series of chosen actions must share the exact frame index. An array is
    interpreted positionally, which the caller must preserve when subsetting.
    """
    observed, chosen, probabilities_array = _validated_inputs(df, actions, probabilities)
    values = _outcome(df, outcome)
    weights = (observed == chosen).astype(float) - (observed == 0).astype(float)
    return values * weights / probabilities_array[observed]


def _summary(scores: np.ndarray, prefix: str) -> dict[str, float]:
    if len(scores) < 2:
        raise ValueError("Evaluation requires at least two observations")
    estimate = float(scores.mean())
    se = float(scores.std(ddof=1) / np.sqrt(len(scores)))
    half_width = float(norm.ppf(0.975)) * se
    return {
        f"incremental_{prefix}": estimate,
        f"{prefix}_se": se,
        f"{prefix}_ci_low": estimate - half_width,
        f"{prefix}_ci_high": estimate + half_width,
    }


def evaluate_policy(
    df: pd.DataFrame,
    actions: Sequence[int],
    probabilities: Sequence[float] = DEFAULT_PROBABILITIES,
) -> dict[str, float]:
    """Estimate a fixed policy's incremental spend/conversion versus No Email.

    Estimates use the full evaluation population as the denominator, not only
    matched or emailed rows. ``email_fraction`` is the actual selected capacity
    fraction; hypothetical cost and margin must be applied separately by the
    scenario layer. Spend is not profit and this function does not estimate ROI.
    """
    _, chosen, _ = _validated_inputs(df, actions, probabilities)
    result = _summary(policy_scores(df, actions, "spend", probabilities), "spend")
    result.update(_summary(policy_scores(df, actions, "conversion", probabilities), "conversion"))
    result["email_fraction"] = float(np.mean(chosen != 0))
    return result


def evaluate_policy_difference(
    df: pd.DataFrame,
    actions_a: Sequence[int],
    actions_b: Sequence[int],
    probabilities: Sequence[float] = DEFAULT_PROBABILITIES,
) -> dict[str, float]:
    """Estimate policy A minus policy B on the same held-out rows.

    The per-row scores are differenced *before* computing uncertainty, retaining
    their shared-outcome covariance. ``incremental_spend`` and
    ``incremental_conversion`` mean A minus B here. CIs are pointwise: selecting
    a winner among many tested policies would require further confirmation or
    a predeclared multiplicity correction.
    """
    _, chosen_a, _ = _validated_inputs(df, actions_a, probabilities)
    _, chosen_b, _ = _validated_inputs(df, actions_b, probabilities)
    result = {}
    for outcome in ("spend", "conversion"):
        scores = policy_scores(df, actions_a, outcome, probabilities)
        scores -= policy_scores(df, actions_b, outcome, probabilities)
        result.update(_summary(scores, outcome))
    result["email_fraction_a"] = float(np.mean(chosen_a != 0))
    result["email_fraction_b"] = float(np.mean(chosen_b != 0))
    result["email_fraction_difference"] = result["email_fraction_a"] - result["email_fraction_b"]
    return result
