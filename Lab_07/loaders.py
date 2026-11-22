import csv
import io
import json
from functools import singledispatch
from pathlib import Path
from typing import Any

def _parse_csv_text(text: str) -> list[dict[str, Any]]:
    reader = csv.DictReader(io.StringIO(text))
    return [dict(row) for row in reader]

def _validate_records(records: Any) -> list[dict[str, Any]]:
    if not isinstance(records, list):
        raise ValueError("Expected a list of records")
    if any(not isinstance(item, dict) for item in records):
        raise ValueError("All items in the collection must be dictionaries")
    return [dict(item) for item in records]

@singledispatch
def load_employees(src: Any) -> list[dict[str, Any]]:
    raise TypeError(f"Unsupported source type: {type(src)!r}")

@load_employees.register
def _(src: str) -> list[dict[str, Any]]:
    cleaned = src.strip()
    if cleaned.startswith("["):
        return _validate_records(json.loads(cleaned))
    if cleaned.startswith("{"):
        parsed = json.loads(cleaned)
        if isinstance(parsed, dict) and "employees" in parsed:
            return _validate_records(parsed["employees"])
        raise ValueError("JSON object must contain an 'employees' key")
    path = Path(cleaned)
    if path.suffix.lower() == ".csv":
        return _parse_csv_text(path.read_text(encoding="utf-8"))
    if path.suffix.lower() == ".json":
        return load_employees(path)
    if "\n" in cleaned and "," in cleaned.splitlines()[0]:
        return _parse_csv_text(cleaned)
    return load_employees(path)


@load_employees.register
def _(src: Path) -> list[dict[str, Any]]:
    if src.suffix.lower() == ".csv":
        return _parse_csv_text(src.read_text(encoding="utf-8"))
    parsed = json.loads(src.read_text(encoding="utf-8"))
    if isinstance(parsed, dict) and "employees" in parsed:
        return _validate_records(parsed["employees"])
    return _validate_records(parsed)

@load_employees.register
def _(src: io.TextIOBase) -> list[dict[str, Any]]:
    content = src.read()
    name = getattr(src, "name", "")
    if isinstance(name, str) and name.lower().endswith(".csv"):
        return _parse_csv_text(content)
    stripped = content.lstrip()
    if stripped.startswith("[") or stripped.startswith("{"):
        return load_employees(stripped)
    return _parse_csv_text(content)

@load_employees.register
def _(src: list) -> list[dict[str, Any]]:
    return _validate_records(src)
