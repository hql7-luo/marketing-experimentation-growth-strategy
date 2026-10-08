"""Small synthetic unit fixtures are not analysis data."""

import numpy as np
import pandas as pd
import pytest
from marketing_analytics.models import incremental_policy, segment_from_features, _select
from marketing_analytics.data import split


def test_capacity_ties_and_threshold_use_no_outcomes():
    x = pd.DataFrame({"recency": [1, 1, 6, 6], "mens": [1, 1, 0, 0], "womens": [0, 0, 1, 1]})
    values = pd.DataFrame(
        [[1.0, 2.0, 1.1], [1.0, 0.8, 1.01]],
        index=["Recent | Men only", "Lapsed | Women only"],
        columns=[0, 1, 2],
    )
    result = incremental_policy(values, x, capacity=0.25, margin=0.4, cost=0.02)
    assert result.tolist() == [1, 0, 0, 0]
    poisoned = x.assign(spend=[10000] * 4, conversion=[1] * 4, action=[2] * 4)
    assert np.array_equal(result, incremental_policy(values, poisoned, capacity=0.25))
    assert incremental_policy(values, x, cost=10).tolist() == [0] * 4


def test_segment_uses_only_historical_features():
    x = pd.DataFrame({"recency": [4, 5], "mens": [1, 0], "womens": [1, 0]})
    assert segment_from_features(x).tolist() == ["Recent | Both", "Lapsed | Neither"]


def test_split_is_disjoint_reproducible_and_outcome_independent():
    data = pd.DataFrame({"action": np.repeat([0, 1, 2], 20), "spend": np.arange(60)})
    train, test = split(data)
    a, b = split(data.assign(spend=100000))
    assert set(train.index).isdisjoint(test.index)
    assert len(train) + len(test) == len(data)
    assert train.index.equals(a.index) and test.index.equals(b.index)
    assert train.action.value_counts().to_dict() == {0: 10, 1: 10, 2: 10}


def test_invalid_capacity():
    with pytest.raises(ValueError):
        _select([1, 2], 1.1)
