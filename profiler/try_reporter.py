import json
from profiler.reporter import save_json


def test_save_json_creates_valid_file(tmp_path):
    data = {"summary": {"total": 3}}
    path = save_json(data, tmp_path / "run.json")
    with open(path, encoding="utf-8") as file:
        assert json.load(file) == data