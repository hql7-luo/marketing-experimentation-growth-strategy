"""Fail on source-row publication, broken local assets, or aggregate/figure drift."""

from pathlib import Path
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
print(f"Publication checks passed: {len(manifest)} pinned aggregate/figure artifacts; no raw data")
