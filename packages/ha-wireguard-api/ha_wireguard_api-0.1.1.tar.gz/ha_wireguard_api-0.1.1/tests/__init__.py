"""Tests for WireGuard status API."""
import json
from pathlib import Path


def load_fixture(filename: str) -> str:
    """Load a fixture."""
    path = Path(__package__) / "fixtures" / filename
    text = path.read_text(encoding="utf-8")
    return json.loads(text)
