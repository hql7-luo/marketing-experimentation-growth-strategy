"""Run the complete analysis. No customer-level artifacts leave ignored data directories."""

from pathlib import Path
import argparse
import hashlib
import json
import sqlite3
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from sklearn.metrics import roc_auc_score, brier_score_loss, log_loss
from .data import load, fetch, split, ARM_NAMES, FEATURES, SHA256, SEED
from .models import (
    fit_propensity,
    fit_segment_values,
    feature_frame,
    random_policy,
    propensity_policy,
    incremental_policy,
)
from .inference import contrasts
from .policy import evaluate_policy, evaluate_policy_difference


def balance(data):
    x = pd.DataFrame(
        {
            "recency": data.recency,
            "log_history": np.log1p(data.history),
            "mens": data.mens,
            "womens": data.womens,
            "newbie": data.newbie,
        }
    )
    x = pd.concat([x, pd.get_dummies(data[["channel", "zip_code"]], dtype=float)], axis=1)
    rows = []
    for col in x:
        for a, b in [(1, 0), (2, 0), (1, 2)]:
            xa, xb = x.loc[data.action.eq(a), col], x.loc[data.action.eq(b), col]
            denom = np.sqrt((xa.var(ddof=1) + xb.var(ddof=1)) / 2)
            rows.append(
                {
                    "feature": col,
                    "treatment": a,
                    "reference": b,
                    "smd": (xa.mean() - xb.mean()) / denom,
                }
            )
    tests = []
    for col in ["recency", "history"]:
        groups = [data.loc[data.action.eq(a), col] for a in [0, 1, 2]]
        result = stats.f_oneway(*groups)
        tests.append({"feature": col, "method": "ANOVA", "p_value": result.pvalue})
    for col in ["mens", "womens", "newbie", "channel", "zip_code", "history_segment"]:
        result = stats.chi2_contingency(pd.crosstab(data.action, data[col]))
        tests.append({"feature": col, "method": "chi-square", "p_value": result.pvalue})
    return pd.DataFrame(rows), pd.DataFrame(tests)


def run(root):
    table_dir = root / "reports/tables"
    table_dir.mkdir(parents=True, exist_ok=True)
    source = root / "data/raw/hillstrom.csv"
    data = load(source)
    raw = pd.read_csv(source)
    audit = {
        "source_sha256": SHA256,
        "field_profile": {
            col: {
                "dtype": str(raw[col].dtype),
                "unique_values": int(raw[col].nunique()),
                "missing": int(raw[col].isna().sum()),
                **(
                    {"minimum": float(raw[col].min()), "maximum": float(raw[col].max())}
                    if pd.api.types.is_numeric_dtype(raw[col])
                    else {"categories": sorted(raw[col].unique().tolist())}
                ),
            }
            for col in raw.columns
        },
        "records": len(data),
        "columns": len(raw.columns),
        "missing_cells": int(raw.isna().sum().sum()),
        "identical_full_records_beyond_first": int(raw.duplicated().sum()),
        "rows_removed": 0,
        "arm_counts": {ARM_NAMES[int(k)]: int(v) for k, v in data.action.value_counts().items()},
        "spend_positive_rows": int(data.spend.gt(0).sum()),
        "max_spend": float(data.spend.max()),
        "spend_quantiles": {
            str(k): float(v) for k, v in data.spend.quantile([0.5, 0.95, 0.99, 0.999]).items()
        },
        "category_correction": {"Surburban": "Suburban"},
        "identifier_available": False,
    }
    (root / "reports/data_audit.json").write_text(json.dumps(audit, indent=2) + "\n")
    with sqlite3.connect(":memory:") as db:
        data.to_sql("customers", db, index=False)
        for file in sorted((root / "sql").glob("*.sql")):
            pd.read_sql_query(file.read_text(), db).to_csv(
                table_dir / f"{file.stem}.csv", index=False
            )
    # Independently reconcile SQL means with pandas, fail rather than silently diverge.
    summary = pd.read_csv(table_dir / "01_campaign_summary.csv")
    expected = data.groupby("action")[["conversion", "visit", "spend"]].mean()
    np.testing.assert_allclose(
        summary[["conversion_rate", "visit_rate", "spend_per_assigned_customer"]],
        expected[["conversion", "visit", "spend"]],
        rtol=1e-12,
        atol=1e-12,
    )
    effects = contrasts(data)
    effects.to_csv(table_dir / "campaign_contrasts.csv", index=False)
    smds, bal_tests = balance(data)
    smds.to_csv(table_dir / "balance_smd.csv", index=False)
    bal_tests.to_csv(table_dir / "balance_tests.csv", index=False)
    train, test = split(data)
    assert set(train.index).isdisjoint(test.index)
    # All rules below are fit only on training rows; predictions get historical X only.
    propensity = fit_propensity(train)
    lookup, cell_train = fit_segment_values(train)
    cell_train.to_csv(table_dir / "training_segment_values.csv", index=False)
    x_test = test[FEATURES].copy()
    x_test.index = test.index  # Positional output remains aligned to this evaluation frame.
    control_test = test.loc[test.action.eq(0)]
    probabilities = propensity.predict_proba(feature_frame(control_test))[:, 1]
    model_metrics = {
        "control_test_n": len(control_test),
        "auroc": float(roc_auc_score(control_test.conversion, probabilities)),
        "brier": float(brier_score_loss(control_test.conversion, probabilities)),
        "log_loss": float(log_loss(control_test.conversion, probabilities)),
        "train_control_rate": float(train.loc[train.action.eq(0)].conversion.mean()),
        "constant_brier": float(
            brier_score_loss(
                control_test.conversion,
                np.repeat(train.loc[train.action.eq(0)].conversion.mean(), len(control_test)),
            )
        ),
    }
    bins = pd.qcut(probabilities, 10, labels=False, duplicates="drop")
    pd.DataFrame(
        {"decile": bins, "predicted": probabilities, "observed": control_test.conversion.to_numpy()}
    ).groupby("decile").agg(
        customers=("observed", "size"),
        predicted=("predicted", "mean"),
        observed=("observed", "mean"),
    ).to_csv(table_dir / "propensity_calibration.csv")
    names = propensity[0].get_feature_names_out()
    pd.DataFrame(
        {
            "feature": names,
            "coefficient": propensity[1].coef_[0],
            "odds_ratio": np.exp(propensity[1].coef_[0]),
        }
    ).to_csv(table_dir / "propensity_coefficients.csv", index=False)
    policies = {
        "No Email": np.zeros(len(test), dtype=int),
        "Blanket Men": np.ones(len(test), dtype=int),
        "Blanket Women": np.full(len(test), 2),
        "Random Men (50%)": random_policy(x_test, 1, 0.5),
        "Random Women (50%)": random_policy(x_test, 2, 0.5),
        "Purchase propensity Men (50%)": propensity_policy(propensity, x_test, 0.5),
        "Segment incremental (50%)": incremental_policy(lookup, x_test),
    }
    rows = []
    for name, actions in policies.items():
        result = evaluate_policy(test, actions)
        result.update(
            policy=name,
            men_fraction=float(np.mean(actions == 1)),
            women_fraction=float(np.mean(actions == 2)),
        )
        result["assumed_contribution_per_10000"] = 10000 * (
            0.4 * result["incremental_spend"] - 0.02 * result["email_fraction"]
        )
        result["contribution_ci_low_per_10000"] = 10000 * (
            0.4 * result["spend_ci_low"] - 0.02 * result["email_fraction"]
        )
        result["contribution_ci_high_per_10000"] = 10000 * (
            0.4 * result["spend_ci_high"] - 0.02 * result["email_fraction"]
        )
        rows.append(result)
    pd.DataFrame(rows).to_csv(table_dir / "policies_holdout.csv", index=False)
    differences = []
    for other in ["Random Men (50%)", "Purchase propensity Men (50%)", "Blanket Men"]:
        result = evaluate_policy_difference(
            test, policies["Segment incremental (50%)"], policies[other]
        )
        result.update(policy_a="Segment incremental (50%)", policy_b=other)
        differences.append(result)
    pd.DataFrame(differences).to_csv(table_dir / "policy_paired_differences.csv", index=False)
    scenario = []
    for capacity in [0.25, 0.5, 1.0]:
        for margin in [0.2, 0.4, 0.6]:
            for cost in [0, 0.02, 0.10, 0.50]:
                for threshold in [0, 0.05, 0.10]:
                    actions = incremental_policy(lookup, x_test, capacity, margin, cost, threshold)
                    result = evaluate_policy(test, actions)
                    scenario.append(
                        {
                            "capacity": capacity,
                            "margin": margin,
                            "cost": cost,
                            "minimum_net_contribution": threshold,
                            "maximum_email_budget_per_10000": 10000 * capacity * cost,
                            "email_cost_per_10000": 10000 * result["email_fraction"] * cost,
                            **result,
                            "expected_contribution_per_10000": 10000
                            * (
                                margin * result["incremental_spend"]
                                - cost * result["email_fraction"]
                            ),
                            "contribution_ci_low_per_10000": 10000
                            * (margin * result["spend_ci_low"] - cost * result["email_fraction"]),
                            "contribution_ci_high_per_10000": 10000
                            * (margin * result["spend_ci_high"] - cost * result["email_fraction"]),
                        }
                    )
    pd.DataFrame(scenario).to_csv(table_dir / "scenario_grid.csv", index=False)
    segment_rows = []
    for label, group in data.groupby("customer_segment"):
        result = contrasts(group)
        result = result.loc[result.reference.eq(0)].copy()
        result["customer_segment"] = label
        segment_rows.append(result)
    segments = pd.concat(segment_rows, ignore_index=True)
    from statsmodels.stats.multitest import multipletests

    for outcome in segments.outcome.unique():
        mask = segments.outcome.eq(outcome)
        observed_p = segments.loc[mask, "p_value"].to_numpy()
        padded = np.r_[observed_p, np.ones(16 - len(observed_p))]
        segments.loc[mask, "p_holm_segments"] = multipletests(padded, method="holm")[1][
            : len(observed_p)
        ]
    segments.to_csv(table_dir / "exploratory_segments.csv", index=False)
    # Robust omnibus interactions: mean differences on additive scales, HC3 for heteroskedasticity.
    interactions = []
    for outcome in ["conversion", "spend"]:
        fit = smf.ols(f"{outcome} ~ C(action)*C(customer_segment)", data=data).fit(cov_type="HC3")
        terms = [name for name in fit.params.index if ":" in name]
        restriction = np.zeros((len(terms), len(fit.params)))
        for i, name in enumerate(terms):
            restriction[i, fit.params.index.get_loc(name)] = 1
        wald = fit.wald_test(restriction, scalar=True)
        interactions.append(
            {
                "outcome": outcome,
                "method": "OLS additive interaction joint Wald, HC3 covariance",
                "statistic": float(wald.statistic),
                "df": len(terms),
                "p_value": float(wald.pvalue),
            }
        )
    pd.DataFrame(interactions).to_csv(table_dir / "heterogeneity_omnibus.csv", index=False)
    split_info = {
        "seed": SEED,
        "train_n": len(train),
        "test_n": len(test),
        "train_index_sha256": hashlib.sha256(
            train.index.to_numpy(dtype="int64").tobytes()
        ).hexdigest(),
        "test_index_sha256": hashlib.sha256(
            test.index.to_numpy(dtype="int64").tobytes()
        ).hexdigest(),
        "train_arm_counts": train.action.value_counts().to_dict(),
        "test_arm_counts": test.action.value_counts().to_dict(),
        "policy_prior_weight": 1000,
        "observed_segments": int(data.customer_segment.nunique()),
        "known_assignment_probabilities": [1 / 3] * 3,
    }
    result = {
        "audit": audit,
        "split": split_info,
        "model": model_metrics,
        "max_absolute_smd": float(smds.smd.abs().max()),
        "heterogeneity": interactions,
        "policies": rows,
    }
    (root / "reports/results.json").write_text(json.dumps(result, indent=2) + "\n")
    from .visuals import render

    render(root)
    print(json.dumps(result, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["download", "run"])
    parser.add_argument("--root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    if args.command == "download":
        fetch(args.root / "data/raw/hillstrom.csv")
    else:
        run(args.root)


if __name__ == "__main__":
    main()
