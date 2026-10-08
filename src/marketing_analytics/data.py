"""Source integrity and explicit schema validation; no customer rows are published."""

from pathlib import Path
import hashlib
import urllib.request
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

SOURCE_URL = "http://www.minethatdata.com/Kevin_Hillstrom_MineThatData_E-MailAnalytics_DataMiningChallenge_2008.03.20.csv"
SHA256 = "0e5893329d8b93cefecc571777672028290ab69865718020c78c7284f291aece"
ARM_MAP = {"No E-Mail": 0, "Mens E-Mail": 1, "Womens E-Mail": 2}
ARM_NAMES = {0: "No Email", 1: "Men's Email", 2: "Women's Email"}
FEATURES = ["recency", "history", "mens", "womens", "newbie", "channel", "zip_code"]
COLUMNS = [
    "recency",
    "history_segment",
    "history",
    "mens",
    "womens",
    "zip_code",
    "newbie",
    "channel",
    "segment",
    "visit",
    "conversion",
    "spend",
]
SEED = 20080320


def fetch(path: Path) -> None:
    """Verify publisher bytes before writing; HTTP is disclosed in provenance."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(SOURCE_URL, timeout=60) as response:
        blob = response.read()
    if hashlib.sha256(blob).hexdigest() != SHA256:
        raise ValueError(
            "Publisher content changed: review source; do not silently replace pinned data"
        )
    path.write_bytes(blob)


def load(path: Path) -> pd.DataFrame:
    if hashlib.sha256(path.read_bytes()).hexdigest() != SHA256:
        raise ValueError("Unexpected source SHA256")
    raw = pd.read_csv(path)
    validate(raw)
    data = raw.copy()
    data["zip_code"] = data["zip_code"].replace({"Surburban": "Suburban"})
    data["action"] = data["segment"].map(ARM_MAP).astype(int)
    pref = np.select(
        [data.mens.eq(1) & data.womens.eq(1), data.mens.eq(1), data.womens.eq(1)],
        ["Both", "Men only", "Women only"],
        default="Neither",
    )
    data["customer_segment"] = np.where(data.recency.le(4), "Recent", "Lapsed") + " | " + pref
    return data


def validate(data: pd.DataFrame) -> None:
    if list(data.columns) != COLUMNS or len(data) != 64000:
        raise ValueError("Unexpected schema or row count")
    if data.isna().any().any():
        raise ValueError("Missing source fields")
    if set(data.segment) != set(ARM_MAP):
        raise ValueError("Unexpected treatment labels")
    for col in ["mens", "womens", "newbie", "visit", "conversion"]:
        if not data[col].isin([0, 1]).all():
            raise ValueError(f"Non-binary {col}")
    if not data.recency.between(1, 12).all():
        raise ValueError("Recency outside 1–12 months")
    if (
        not np.isfinite(data[["history", "spend"]].to_numpy()).all()
        or (data[["history", "spend"]] < 0).any().any()
    ):
        raise ValueError("Invalid monetary values")
    if (data.conversion > data.visit).any() or not data.conversion.eq(data.spend.gt(0)).all():
        raise ValueError("Outcome consistency failed")
    if set(data.zip_code) != {"Surburban", "Urban", "Rural"} or set(data.channel) != {
        "Web",
        "Phone",
        "Multichannel",
    }:
        raise ValueError("Unexpected categorical fields")


def split(data: pd.DataFrame):
    train, test = train_test_split(data, test_size=0.5, stratify=data.action, random_state=SEED)
    return train.copy(), test.copy()
