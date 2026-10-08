"""Record aggregate/figure bytes after an intentional reviewed regeneration."""

from pathlib import Path
import hashlib
import json

root = Path(__file__).resolve().parents[1]
paths = sorted((root / "reports/tables").glob("*.csv"))
paths += sorted((root / "reports/figures").glob("*"))
paths += [root / "reports/results.json", root / "reports/data_audit.json"]
manifest = {
    str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
}
(root / "reports/manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
print(f"Recorded {len(manifest)} aggregate/figure artifacts")
