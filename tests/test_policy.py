"""Analytic toy fixtures verify policy estimators without real holdout access."""

import math
from itertools import product

import numpy as np
import pandas as pd
import pytest

from marketing_analytics.policy import evaluate_policy, evaluate_policy_difference, policy_scores


@pytest.fixture
def experiment():
    return pd.DataFrame(
        {
            "action": [0, 1, 2, 0, 1, 2],
            "spend": [1, 2, 3, 4, 5, 6],
            "conversion": [0, 1, 1, 1, 0, 0],
        },
        index=[11, 13, 17, 19, 23, 29],
    )


def test_ht_matches_hand_calculation_and_population_denominator(experiment):
    actions = np.array([0, 1, 0, 1, 0, 2])
    # Three emails in a population of six: scores [0,6,0,-12,0,18].
    # Mean=2, sample variance=96, SE=sqrt(96/6)=4.
    assert policy_scores(experiment, actions).tolist() == [0, 6, 0, -12, 0, 18]
    result = evaluate_policy(experiment, actions)
    assert result["incremental_spend"] == 2
    assert result["spend_se"] == 4
    assert result["spend_ci_low"] == pytest.approx(2 - 1.959963984540054 * 4)
    assert result["spend_ci_high"] == pytest.approx(2 + 1.959963984540054 * 4)
    assert result["incremental_conversion"] == 0
    assert result["conversion_se"] == pytest.approx(math.sqrt(0.6))
    assert result["email_fraction"] == 0.5


def test_no_email_baseline_cancels_exactly(experiment):
    result = evaluate_policy(experiment, np.zeros(len(experiment), dtype=int))
    assert all(value == 0 for value in result.values())


def test_known_nonuniform_probabilities_are_used(experiment):
    scores = policy_scores(experiment, [1] * 6, probabilities=(0.5, 0.25, 0.25))
    assert scores.tolist() == [-2, 8, 0, -8, 20, 0]
    assert scores.mean() == 3


def test_exact_randomization_expectation_recovers_fixed_policy_effect():
    # Exhaust all nine equally likely assignments for two hypothetical people.
    # These potential outcomes exist only in a unit test, never in analysis.
    potential_spend = np.array([[5, 9, 7], [1, 4, 6]])
    chosen = np.array([1, 2])
    estimates = []
    for assigned in product((0, 1, 2), repeat=2):
        frame = pd.DataFrame(
            {
                "action": assigned,
                "spend": potential_spend[np.arange(2), assigned],
                "conversion": [0, 0],
            }
        )
        estimates.append(evaluate_policy(frame, chosen)["incremental_spend"])
    # The policy adds 4 and 5 spend units, so its population effect is 4.5.
    assert np.mean(estimates) == 4.5


def test_paired_policy_comparison_uses_shared_rows(experiment):
    result = evaluate_policy_difference(experiment, [1] * 6, [2] * 6)
    # A-B scores [0,6,-9,0,15,-18], mean=-1 and SE=sqrt(22).
    assert result["incremental_spend"] == -1
    assert result["spend_se"] == pytest.approx(math.sqrt(22))
    assert result["spend_ci_high"] == pytest.approx(-1 + 1.959963984540054 * math.sqrt(22))
    assert result["email_fraction_a"] == result["email_fraction_b"] == 1
    assert result["email_fraction_difference"] == 0
    separate_a = evaluate_policy(experiment, [1] * 6)
    separate_b = evaluate_policy(experiment, [2] * 6)
    assert (
        result["incremental_spend"]
        == separate_a["incremental_spend"] - separate_b["incremental_spend"]
    )
    # Independent-SE addition would yield 13.6+17.8, rather than paired 22.
    assert result["spend_se"] ** 2 != pytest.approx(
        separate_a["spend_se"] ** 2 + separate_b["spend_se"] ** 2
    )


def test_identical_policies_have_zero_difference(experiment):
    actions = [0, 1, 0, 1, 0, 2]
    result = evaluate_policy_difference(experiment, actions, actions)
    assert result["incremental_spend"] == result["spend_se"] == 0
    assert result["incremental_conversion"] == result["conversion_se"] == 0
    assert result["email_fraction_difference"] == 0


def test_row_selection_and_order_are_explicit(experiment):
    actions = pd.Series([0, 1, 0, 1, 0, 2], index=experiment.index)
    order = [29, 11, 19, 17, 23, 13]
    original = evaluate_policy(experiment, actions)
    reordered = evaluate_policy(experiment.loc[order], actions.loc[order])
    assert reordered == original
    subset = experiment.loc[[13, 19, 29]]
    assert policy_scores(subset, actions.loc[subset.index]).tolist() == [6, -12, 18]
    assert evaluate_policy(subset, actions.loc[subset.index])["incremental_spend"] == 4
    with pytest.raises(ValueError, match="index must match"):
        evaluate_policy(experiment.loc[order], actions)
    with pytest.raises(ValueError, match="one action per"):
        evaluate_policy(subset, actions.to_numpy())


@pytest.mark.parametrize(
    "probabilities",
    [
        (0, 0.5, 0.5),
        (-0.1, 0.5, 0.6),
        (0.3, 0.3, 0.3),
        (1 / 3, 1 / 3),
        (np.nan, 0.5, 0.5),
        (np.inf, 0.5, 0.5),
        ((1 / 3,), (1 / 3,), (1 / 3,)),
    ],
)
def test_invalid_assignment_probabilities_are_rejected(experiment, probabilities):
    with pytest.raises(ValueError, match="probabilities"):
        evaluate_policy(experiment, [1] * 6, probabilities)


@pytest.mark.parametrize(
    "actions",
    [
        [1] * 5,
        [1] * 7,
        [1, 1, 1, 1, 1, 3],
        [1, 1, 1, 1, 1, -1],
        [1, 1, 1, 1, 1, 0.5],
        [1, 1, 1, 1, 1, np.nan],
        [[1], [1], [1], [1], [1], [1]],
    ],
)
def test_invalid_policy_actions_are_rejected(experiment, actions):
    with pytest.raises(ValueError):
        evaluate_policy(experiment, actions)


@pytest.mark.parametrize(
    "column,value",
    [
        ("action", 3),
        ("action", np.nan),
        ("spend", -1),
        ("spend", np.inf),
        ("spend", np.nan),
        ("conversion", 2),
    ],
)
def test_invalid_outcomes_and_observed_actions_are_rejected(experiment, column, value):
    experiment[column] = experiment[column].astype(float)
    experiment.loc[experiment.index[0], column] = value
    with pytest.raises(ValueError):
        evaluate_policy(experiment, [1] * 6)


def test_missing_columns_or_inadequate_population_is_rejected(experiment):
    with pytest.raises(ValueError, match="numeric column"):
        evaluate_policy(experiment.drop(columns="conversion"), [1] * 6)
    with pytest.raises(ValueError, match="numeric column"):
        evaluate_policy(experiment.assign(action=experiment.action.astype(str)), [1] * 6)
    with pytest.raises(ValueError, match="at least two"):
        evaluate_policy(experiment.iloc[:1], [1])
    with pytest.raises(ValueError, match="nonempty"):
        evaluate_policy(experiment.iloc[:0], [])
