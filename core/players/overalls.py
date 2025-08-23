import json
from pathlib import Path
from typing import Dict

def load_player_overalls(path: Path = None) -> Dict[str, float]:
    """Return a dict mapping player name to overall rating."""
    if path is None:
        path = Path(__file__).resolve().parent.parent / "teams" / "data" / "player_info.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return {p["name"]: p["overall"] for p in data if "overall" in p}
