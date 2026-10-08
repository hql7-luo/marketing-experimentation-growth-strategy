from io import BytesIO
import pytest
from marketing_analytics.data import fetch


def test_changed_publisher_bytes_are_never_written(monkeypatch, tmp_path):
    monkeypatch.setattr("urllib.request.urlopen", lambda *a, **k: BytesIO(b"changed source"))
    target = tmp_path / "hillstrom.csv"
    target.write_bytes(b"existing local copy")
    with pytest.raises(ValueError, match="Publisher content changed"):
        fetch(target)
    assert target.read_bytes() == b"existing local copy"
