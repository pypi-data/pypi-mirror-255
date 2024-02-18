"""Tests for WireGuard status API."""
import json
from pathlib import Path
from typing import Any


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    path = Path(__package__) / "fixtures" / filename
    return path.read_text(encoding="utf-8")


def load_json_fixture(filename: str) -> Any:
    """Load a json fixture."""
    return json.loads(load_fixture(filename))
