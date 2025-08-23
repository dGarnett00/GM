import json
from pathlib import Path
from typing import Dict, Any

def load_player_bios(path: Path = None) -> Dict[str, Any]:
    """Return a dict mapping player name to their bio/attributes."""
    if path is None:
        path = Path(__file__).resolve().parent / "player_bio.json"
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    # The bios are under the 'players' key
    return {p["name"]: p for p in data["players"] if "name" in p}
