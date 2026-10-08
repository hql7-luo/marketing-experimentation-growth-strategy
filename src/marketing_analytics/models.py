"""Train-only transparent rules. Prediction accepts only pre-experiment features."""

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from .data import FEATURES, SEED

PRIOR_WEIGHT = 1000


def segment_from_features(features):
    pref = np.select(
        [features.mens.eq(1) & features.womens.eq(1), features.mens.eq(1), features.womens.eq(1)],
        ["Both", "Men only", "Women only"],
        default="Neither",
    )
    return pd.Series(
        np.where(features.recency.le(4), "Recent", "Lapsed") + " | " + pref, index=features.index
    )


def feature_frame(data):
    x = data[FEATURES].copy()
    x["log_history"] = np.log1p(x.pop("history"))
    return x


def fit_propensity(train):
    control = train.loc[train.action.eq(0)]
    numeric = ["recency", "log_history", "mens", "womens", "newbie"]
    categorical = ["channel", "zip_code"]
    prep = ColumnTransformer(
        [
            ("numeric", StandardScaler(), numeric),
            ("categorical", OneHotEncoder(drop="first", handle_unknown="error"), categorical),
        ]
    )
    model = make_pipeline(prep, LogisticRegression(C=1.0, max_iter=1000, random_state=SEED))
    model.fit(feature_frame(control), control.conversion)
    return model


def fit_segment_values(train):
    """Shrink sparse arm-cell means toward overall arm mean using fixed prior weight."""
    means = train.groupby("action").spend.mean()
    estimates = (
        train.groupby(["customer_segment", "action"]).spend.agg(["mean", "count"]).reset_index()
    )
    estimates["shrunk_mean"] = (
        estimates["mean"] * estimates["count"] + PRIOR_WEIGHT * estimates.action.map(means)
    ) / (estimates["count"] + PRIOR_WEIGHT)
    lookup = estimates.pivot(index="customer_segment", columns="action", values="shrunk_mean")
    lookup = lookup.reindex(columns=[0, 1, 2]).fillna(means)
    return lookup, estimates


def _select(score, capacity, eligible=None):
    if not 0 <= capacity <= 1:
        raise ValueError("Capacity must be a fraction between 0 and 1")
    score = np.asarray(score, dtype=float)
    if not np.isfinite(score).all():
        raise ValueError("Scores must be finite")
    # Stable input-position ties are outcome-independent. No row identifier is published.
    indices = np.argsort(-score, kind="stable")
    if eligible is not None:
        indices = indices[np.asarray(eligible)[indices]]
    selected = np.zeros(len(score), dtype=bool)
    selected[indices[: int(np.floor(capacity * len(score)))]] = True
    return selected


def random_policy(features, arm, capacity):
    priority = np.random.default_rng(SEED).random(len(features))
    return np.where(_select(priority, capacity), arm, 0)


def propensity_policy(model, features, capacity):
    score = model.predict_proba(feature_frame(features))[:, 1]
    return np.where(_select(score, capacity), 1, 0)


def incremental_policy(lookup, features, capacity=0.5, margin=0.4, cost=0.02, threshold=0.0):
    if not 0 <= margin <= 1 or cost < 0 or threshold < 0:
        raise ValueError("Invalid financial assumption")
    segments = segment_from_features(features)
    if not segments.isin(lookup.index).all():
        raise ValueError("Unseen segment: review training population")
    values = lookup.loc[segments].to_numpy()
    gains = margin * (values[:, 1:] - values[:, [0]]) - cost
    chosen = np.argmax(gains, axis=1) + 1
    score = gains.max(axis=1)
    return np.where(_select(score, capacity, score > threshold), chosen, 0)
