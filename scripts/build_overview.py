"""Presentation only: draw verified purchase rates, without rerunning or changing analysis."""

from pathlib import Path
import hashlib
import json
import pandas as pd
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "reports/tables/01_campaign_summary.csv"
OUTPUT = ROOT / "reports/figures/00_purchase_rate_overview"


def build():
    summary = pd.read_csv(SOURCE).set_index("action")
    # Validate displayed buyer proportions against original aggregate counts.
    labels = {0: "No Email", 2: "Women's Apparel Email", 1: "Men's Apparel Email"}
    colors = {0: "#949da5", 2: "#c86b45", 1: "#087f8c"}
    order = [0, 2, 1]
    for action in order:
        row = summary.loc[action]
        assert abs(row.conversion_rate - row.buyers / row.assigned_customers) < 1e-12
    plt.rcParams.update(
        {
            "font.family": "DejaVu Sans",
            "text.color": "#142c38",
            "figure.facecolor": "#faf9f5",
            "axes.facecolor": "#faf9f5",
            "savefig.facecolor": "#faf9f5",
            "svg.hashsalt": "hillstrom-plain-language-overview",
        }
    )
    fig, ax = plt.subplots(figsize=(9, 6))
    for action, y in zip(order, [2, 1, 0], strict=True):
        rate = float(summary.loc[action, "conversion_rate"]) * 100
        ax.barh(y, rate, height=0.31, color=colors[action])
        ax.text(0, y + 0.25, labels[action], fontsize=22, va="bottom")
        ax.text(rate + 0.045, y, f"{rate:.3f}%", fontsize=28, weight="bold", va="center")
    ax.set_xlim(0, 1.85)
    ax.set_ylim(-0.45, 2.6)
    ax.axis("off")
    fig.suptitle(
        "Which Email Got More Customers to Buy?",
        fontsize=24,
        weight="bold",
        x=0.06,
        ha="left",
        y=0.96,
    )
    fig.text(
        0.06,
        0.14,
        "Purchase rate = % of assigned shoppers who bought within two weeks.",
        fontsize=16,
    )
    fig.text(
        0.06,
        0.09,
        "Historical randomized experiment • 64,000 shoppers • 2008",
        fontsize=14,
        color="#56646e",
    )
    fig.text(
        0.06,
        0.045,
        "Men's / Women's refer to apparel promotions, not customer gender.",
        fontsize=13,
        color="#56646e",
    )
    fig.subplots_adjust(left=0.06, right=0.98, bottom=0.22, top=0.84)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUTPUT.with_suffix(".png"), dpi=160)
    fig.savefig(OUTPUT.with_suffix(".svg"), metadata={"Date": None})
    plt.close(fig)
    svg = OUTPUT.with_suffix(".svg")
    svg.write_text("\n".join(line.rstrip() for line in svg.read_text().splitlines()) + "\n")

    def sha(path):
        return hashlib.sha256(path.read_bytes()).hexdigest()

    record = {
        "purpose": "Plain-language overview; original analysis is unchanged",
        "source_path": str(SOURCE.relative_to(ROOT)),
        "source_sha256": sha(SOURCE),
        "source_dataset_sha256": json.loads((ROOT / "reports/data_audit.json").read_text())[
            "source_sha256"
        ],
        "historical_year": 2008,
        "outcome": "Share of assigned customers who purchased within two weeks",
        "customers": int(summary.assigned_customers.sum()),
        "rates": [
            {
                "action": a,
                "label": labels[a],
                "purchase_rate": float(summary.loc[a, "conversion_rate"]),
                "display_percent": f"{100 * summary.loc[a, 'conversion_rate']:.3f}%",
            }
            for a in order
        ],
        "estimated_extra_buyers_per_1000": float(
            (summary.loc[1, "conversion_rate"] - summary.loc[0, "conversion_rate"]) * 1000
        ),
        "figures": {
            str(OUTPUT.with_suffix(ext).relative_to(ROOT)): sha(OUTPUT.with_suffix(ext))
            for ext in [".png", ".svg"]
        },
    }
    (ROOT / "reports/overview_manifest.json").write_text(json.dumps(record, indent=2) + "\n")
    print("Overview created from protected campaign summary; no analysis files changed")


if __name__ == "__main__":
    build()
