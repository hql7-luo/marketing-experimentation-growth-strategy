"""Six decision figures, each built exclusively from exported aggregate calculations."""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .data import ARM_NAMES

COLORS = {1: "#087f8c", 2: "#c86b45"}


def render(root: Path):
    tables = root / "reports/tables"
    figures = root / "reports/figures"
    figures.mkdir(exist_ok=True, parents=True)
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "font.size": 11,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.labelcolor": "#344054",
            "text.color": "#142c38",
            "axes.titleweight": "bold",
            "figure.facecolor": "#faf9f5",
            "axes.facecolor": "#faf9f5",
            "savefig.facecolor": "#faf9f5",
            "svg.hashsalt": "hillstrom-20080320",
        }
    )

    def finish(fig, name, caption):
        fig.text(0.04, 0.02, caption, fontsize=9, color="#56646e", wrap=True)
        fig.tight_layout(rect=(0, 0.09, 1, 0.96))
        fig.savefig(figures / f"{name}.png", dpi=170)
        fig.savefig(figures / f"{name}.svg", metadata={"Date": None})
        svg = figures / f"{name}.svg"
        svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")
        plt.close(fig)

    effects = pd.read_csv(tables / "campaign_contrasts.csv")
    conversion = effects.loc[effects.outcome.eq("conversion") & effects.reference.eq(0)]
    fig, ax = plt.subplots(figsize=(9, 4.7))
    for i, row in enumerate(conversion.itertuples()):
        ax.errorbar(
            row.effect * 100,
            i,
            xerr=[[100 * (row.effect - row.ci_low)], [100 * (row.ci_high - row.effect)]],
            fmt="o",
            color=COLORS[row.treatment],
            capsize=5,
            markersize=9,
        )
        ax.annotate(
            f"+{row.effect * 100:.2f} pp  |  Holm p={row.p_holm:.3g}",
            (row.effect * 100, i),
            xytext=(0, 18),
            textcoords="offset points",
            ha="center",
            fontsize=10,
        )
    ax.axvline(0, color="#8d9498", ls="--")
    ax.set_yticks([0, 1], ["Men's Email", "Women's Email"])
    ax.set_ylim(-0.5, 1.6)
    ax.set_xlabel("Purchase conversion lift vs no email (percentage points)")
    ax.set_title("Email increased purchases in this historical experiment", loc="left", pad=20)
    finish(
        fig,
        "01_conversion_lift",
        "64,000 assigned customers • two-week outcomes • pointwise 95% CI • three conversion contrasts adjusted by Holm",
    )
    spend = effects.loc[effects.outcome.eq("spend")]
    fig, ax = plt.subplots(figsize=(9, 4.8))
    for i, row in enumerate(spend.itertuples()):
        ax.errorbar(
            row.effect,
            i,
            xerr=[[row.effect - row.ci_low], [row.ci_high - row.effect]],
            fmt="o",
            color="#087f8c" if i < 2 else "#c86b45",
            capsize=5,
            markersize=8,
        )
        ax.annotate(
            f"${row.effect:.3f}; Holm p={row.p_holm:.3g}",
            (row.effect, i),
            xytext=(8, 10),
            textcoords="offset points",
            fontsize=10,
        )
    ax.axvline(0, color="#8d9498", ls="--")
    ax.set_yticks(range(3), ["Men − Control", "Women − Control", "Men − Women"])
    ax.set_ylim(-0.5, 2.6)
    ax.set_xlabel("Incremental purchase spend per assigned customer ($)")
    ax.set_title("Incremental spend is uncertain; campaign ranking needs care", loc="left", pad=20)
    finish(
        fig,
        "02_incremental_spend",
        "Welch pointwise 95% CI • sparse purchase spend • secondary outcome • spend is not profit",
    )
    seg = pd.read_csv(tables / "exploratory_segments.csv")
    seg = seg.loc[seg.outcome.eq("conversion")]
    labels = sorted(seg.customer_segment.unique())
    fig, ax = plt.subplots(figsize=(10, 6))
    for a, delta in [(1, -0.13), (2, 0.13)]:
        rows = seg.loc[seg.treatment.eq(a)].set_index("customer_segment").loc[labels]
        ax.errorbar(
            rows.effect * 100,
            np.arange(len(labels)) + delta,
            xerr=np.vstack([(rows.effect - rows.ci_low) * 100, (rows.ci_high - rows.effect) * 100]),
            fmt="o",
            color=COLORS[a],
            capsize=3,
            label=ARM_NAMES[a],
        )
    ax.axvline(0, color="#8d9498", ls="--")
    ax.set_yticks(range(len(labels)), labels)
    ax.invert_yaxis()
    ax.set_xlabel("Conversion lift vs within-segment control (percentage points)")
    ax.set_title("Segment differences need confirmation", loc="left", pad=20)
    ax.legend(loc="lower right", frameon=False)
    finish(
        fig,
        "03_segment_heterogeneity",
        "Recent: recency ≤4 months • all segments use pre-treatment fields • pointwise 95% CI; exploratory, not individual uplift",
    )
    summary = pd.read_csv(tables / "01_campaign_summary.csv")
    population = (
        pd.read_csv(tables / "03_segments.csv")
        .groupby("customer_segment")
        .assigned_customers.sum()
        .sort_values()
    )
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(11, 5), gridspec_kw={"width_ratios": [1.6, 1]})
    ax.barh(population.index, population.values, color="#97c1bd")
    ax.set_xlabel("Assigned customers across all three arms")
    ax.set_title("Pre-treatment segment sizes", loc="left", pad=15)
    bx.bar(
        [ARM_NAMES[a] for a in summary.action],
        summary.conversion_rate * 100,
        color=["#a6abb0", COLORS[1], COLORS[2]],
    )
    bx.set_ylabel("Two-week purchase conversion (%)")
    bx.tick_params(axis="x", labelrotation=25)
    bx.set_title("Outcome rates by assignment", loc="left", pad=15)
    for i, value in enumerate(summary.conversion_rate * 100):
        bx.text(i, value + 0.08, f"{value:.2f}%", ha="center", fontsize=10)
    finish(
        fig,
        "04_customer_context",
        "Historical merchandise preference is not customer gender • no customer identity available • raw rows preserved",
    )
    policies = pd.read_csv(tables / "policies_holdout.csv")
    fig, ax = plt.subplots(figsize=(10, 6.2))
    y = np.arange(len(policies))
    for i, row in enumerate(policies.itertuples()):
        ax.errorbar(
            row.assumed_contribution_per_10000,
            i,
            xerr=[
                [row.assumed_contribution_per_10000 - row.contribution_ci_low_per_10000],
                [row.contribution_ci_high_per_10000 - row.assumed_contribution_per_10000],
            ],
            fmt="o",
            color="#c86b45" if "Segment" in row.policy else "#087f8c",
            capsize=4,
        )
    ax.set_yticks(y, policies.policy)
    ax.invert_yaxis()
    ax.axvline(0, color="#8d9498", ls="--")
    ax.set_xlabel("Estimated incremental contribution per 10,000 eligible customers ($)")
    ax.set_title("A learned rule must earn its advantage on held-out customers", loc="left", pad=20)
    finish(
        fig,
        "05_policy_comparison",
        "32,000 untouched test rows • HT estimate vs no email • pointwise 95% CI • assumed margin 40%, cost $0.02/email",
    )
    grid = pd.read_csv(tables / "scenario_grid.csv")
    grid = grid.loc[grid.margin.eq(0.4) & grid.minimum_net_contribution.eq(0)]
    fig, ax = plt.subplots(figsize=(9, 5.2))
    for cap, color in [(0.25, "#8199a3"), (0.5, "#087f8c"), (1.0, "#c86b45")]:
        rows = grid.loc[grid.capacity.eq(cap)].sort_values("cost")
        ax.plot(
            rows.cost,
            rows.expected_contribution_per_10000,
            "o-",
            color=color,
            label=f"≤{cap:.0%} email capacity",
        )
    ax.axhline(0, color="#8d9498", ls="--")
    ax.set_xlabel("Hypothetical cost per email ($)")
    ax.set_ylabel("Expected incremental contribution per 10,000 ($)")
    ax.set_title("Financial assumptions change the send / no-send decision", loc="left", pad=20)
    ax.legend(frameon=False)
    finish(
        fig,
        "06_budget_sensitivity",
        "Training-defined segment rule reranked for each cost • assumed margin 40% • point estimates; full intervals in scenario_grid.csv",
    )
