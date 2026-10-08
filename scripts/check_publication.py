"""Fail on source-row publication, broken local assets, or aggregate/figure drift."""

from pathlib import Path
import csv
import hashlib
import json
import subprocess
import re

root = Path(__file__).resolve().parents[1]
tracked = subprocess.check_output(["git", "ls-files"], cwd=root, text=True).splitlines()
for name in tracked:
    if name.startswith(("data/raw/", "data/processed/")) and not name.endswith(".gitkeep"):
        raise SystemExit(f"Row-level data staged: {name}")
    if name.endswith((".sqlite", ".db")):
        raise SystemExit(f"Runtime database staged: {name}")
manifest = json.loads((root / "reports/manifest.json").read_text())
for name, expected in manifest.items():
    actual = hashlib.sha256((root / name).read_bytes()).hexdigest()
    assert actual == expected, f"Artifact hash mismatch: {name}"
overview = json.loads((root / "reports/overview_manifest.json").read_text())
summary_path = root / overview["source_path"]
assert hashlib.sha256(summary_path.read_bytes()).hexdigest() == overview["source_sha256"]
with summary_path.open(newline="") as source:
    summary = {int(row["action"]): row for row in csv.DictReader(source)}
assert overview["customers"] == sum(int(row["assigned_customers"]) for row in summary.values())
assert overview["historical_year"] == 2008
assert (
    overview["source_dataset_sha256"]
    == json.loads((root / "reports/data_audit.json").read_text())["source_sha256"]
)
for rate in overview["rates"]:
    row = summary[rate["action"]]
    observed = int(row["buyers"]) / int(row["assigned_customers"])
    assert abs(observed - rate["purchase_rate"]) < 1e-12
    assert rate["display_percent"] == f"{observed * 100:.3f}%"
extra_buyers = (
    int(summary[1]["buyers"]) / int(summary[1]["assigned_customers"])
    - int(summary[0]["buyers"]) / int(summary[0]["assigned_customers"])
) * 1000
assert abs(extra_buyers - overview["estimated_extra_buyers_per_1000"]) < 1e-10
for name, expected in overview["figures"].items():
    assert hashlib.sha256((root / name).read_bytes()).hexdigest() == expected, (
        f"Overview figure hash mismatch: {name}"
    )
for document in [root / "README.md", root / "README.zh-CN.md", root / "reports/executive_memo.md"]:
    for target in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", document.read_text()):
        if target.startswith(("http:", "https:", "#", "mailto:")):
            continue
        assert (document.parent / target.split("#")[0]).exists(), (
            f"Broken link: {document.name}: {target}"
        )
notebook = json.loads((root / "notebooks/01_research.ipynb").read_text())
for cell in notebook["cells"]:
    for output in cell.get("outputs", []):
        assert output.get("output_type") != "error", "Executed notebook contains an error"
assert all(
    c.get("execution_count") is not None for c in notebook["cells"] if c["cell_type"] == "code"
), "Notebook must be executed"
print(
    f"Publication checks passed: {len(manifest)} original artifacts; "
    "overview rates match buyer counts; no raw data"
)
