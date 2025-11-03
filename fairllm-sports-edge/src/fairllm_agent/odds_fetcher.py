from __future__ import annotations
from typing import Dict, Any
import json, pathlib

class OddsFetcher:
    """Fetches odds. For midpoint, read from local JSON."""
    def __init__(self, source_path: str | None = None):
        self.source_path = source_path

    def fetch(self) -> Dict[str, Any]:
        if not self.source_path:
            raise ValueError("No odds source_path provided.")
        p = pathlib.Path(self.source_path)
        with p.open() as f:
            return json.load(f)
