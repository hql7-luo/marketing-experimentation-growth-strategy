"""Small invented fixtures test mathematics only; they are not project data."""

import math

import numpy as np
import pandas as pd
import pytest
from scipy.stats import t

from marketing_analytics.inference import _holm, contrasts


@pytest.fixture
def experiment():
    return pd.DataFrame(
        {
            "action": np.repeat([0, 1, 2], 4),
            "conversion": [0, 0, 0, 1, 0, 1, 1, 1, 0, 0, 1, 1],
            "visit": [0, 0, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1],
            "spend": [0, 0, 2, 2, 0, 2, 4, 6, 1, 1, 1, 1],
        }
    )


def _row(results, outcome, treatment=1, reference=0):
    return results.loc[
        (results.outcome == outcome)
        & (results.treatment == treatment)
        & (results.reference == reference)
    ].iloc[0]


def test_welch_spend_matches_hand_calculation(experiment):
    row = _row(contrasts(experiment), "spend")
    # Arm means are 3 and 1; sample variances are 20/3 and 4/3.
    # Thus SE=sqrt(2), and Welch degrees of freedom=54/13.
    assert row.effect == 2
    assert row.mean_t == 3
    assert row.mean_c == 1
    assert row.n_t == row.n_c == 4
    assert row.se == pytest.approx(math.sqrt(2))
    assert row.p_value == pytest.approx(2 * t.sf(math.sqrt(2), 54 / 13))
    half_width = t.ppf(0.975, 54 / 13) * math.sqrt(2)
    assert row.ci_low == pytest.approx(2 - half_width)
    assert row.ci_high == pytest.approx(2 + half_width)


def test_binary_pooled_test_and_unpooled_interval(experiment):
    row = _row(contrasts(experiment), "conversion")
    assert row.effect == 0.5
    assert row.se == pytest.approx(math.sqrt(3 / 32))
    # Null pooled rate=.5, null SE=sqrt(1/8), z=sqrt(2).
    assert row.p_value == pytest.approx(math.erfc(1.0))
    assert row.ci_high - row.effect == pytest.approx(1.959963984540054 * math.sqrt(3 / 32))


def test_comparison_family_is_complete_and_oriented(experiment):
    result = contrasts(experiment)
    assert len(result) == 9
    for outcome in ("conversion", "visit", "spend"):
        rows = result[result.outcome == outcome]
        assert list(zip(rows.treatment, rows.reference)) == [(1, 0), (2, 0), (1, 2)]
        assert rows.iloc[2].effect == pytest.approx(rows.iloc[0].effect - rows.iloc[1].effect)


def test_holm_known_values_and_original_order():
    assert _holm(np.array([0.04, 0.01, 0.03])).tolist() == pytest.approx([0.06, 0.03, 0.06])
    assert _holm(np.array([0.2, 0.01, 0.02])).tolist() == pytest.approx([0.2, 0.03, 0.04])
    assert _holm(np.array([0.7, 0.8, 0.9])).tolist() == [1, 1, 1]


def test_multiplicity_is_within_outcome_and_simultaneous_ci_is_wider(experiment):
    all_results = contrasts(experiment)
    binary_only = contrasts(experiment, ["conversion"])
    pd.testing.assert_frame_equal(
        all_results[all_results.outcome == "conversion"].reset_index(drop=True),
        binary_only,
    )
    assert np.all(all_results.p_holm >= all_results.p_value)
    assert np.all(all_results.sim_ci_low <= all_results.ci_low)
    assert np.all(all_results.sim_ci_high >= all_results.ci_high)
    row = _row(all_results, "spend")
    assert row.sim_ci_high - row.effect == pytest.approx(
        t.ppf(1 - 0.05 / 6, 54 / 13) * math.sqrt(2)
    )


def test_zero_outcomes_are_well_defined(experiment):
    experiment[["conversion", "visit", "spend"]] = 0
    result = contrasts(experiment)
    assert np.all(result.effect == 0)
    assert np.all(result.se == 0)
    assert np.all(result.p_value == 1)
    assert np.all(result.p_holm == 1)
    assert np.all(result.ci_low == result.ci_high)


@pytest.mark.parametrize(
    "column,value",
    [
        ("action", 3),
        ("action", 0.5),
        ("action", np.nan),
        ("conversion", 2),
        ("visit", -1),
        ("spend", -1),
        ("spend", np.inf),
        ("spend", np.nan),
    ],
)
def test_invalid_observations_are_rejected(experiment, column, value):
    experiment[column] = experiment[column].astype(float)
    experiment.loc[0, column] = value
    with pytest.raises(ValueError):
        contrasts(experiment)


def test_invalid_shape_or_missing_arm_is_rejected(experiment):
    with pytest.raises(ValueError, match="Missing required"):
        contrasts(experiment.drop(columns="spend"))
    with pytest.raises(ValueError, match="Each action arm"):
        contrasts(experiment[experiment.action != 2])
    with pytest.raises(ValueError, match="Each action arm"):
        contrasts(experiment.drop(index=[9, 10, 11]))
    with pytest.raises(ValueError, match="numeric"):
        contrasts(experiment.assign(spend=experiment.spend.astype(str)))
    for outcomes in ([], "spend", ["spend", "spend"]):
        with pytest.raises(ValueError):
            contrasts(experiment, outcomes)
