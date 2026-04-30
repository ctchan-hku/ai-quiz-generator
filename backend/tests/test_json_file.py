"""json_file.read_json."""

import json

from app.helpers.json_file import read_json


def test_read_json_roundtrip(tmp_path) -> None:
    p = tmp_path / "x.json"
    p.write_text(json.dumps({"a": 1}), encoding="utf-8")
    assert read_json(p) == {"a": 1}


def test_read_json_missing_file_returns_empty_dict(tmp_path) -> None:
    missing = tmp_path / "nope.json"
    assert read_json(missing) == {}


def test_read_json_invalid_json_returns_empty_dict(tmp_path) -> None:
    p = tmp_path / "bad.json"
    p.write_text("{not json", encoding="utf-8")
    assert read_json(p) == {}
