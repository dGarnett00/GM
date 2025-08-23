from __future__ import annotations

from pathlib import Path
from typing import Dict, List
import json


def _default_rosters_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "rosters" / "rosters.json"


def load_rosters(path: Path | None = None) -> Dict[str, List[str]]:
    p = Path(path) if path else _default_rosters_path()
    if not p.exists():
        return {}
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, dict) else {}


def get_team_roster(team_display_name: str, rosters: Dict[str, List[str]] | None = None) -> List[str]:
    if rosters is None:
        rosters = load_rosters()
    lst = rosters.get(team_display_name) or []
    # Ensure it's a list of strings
    return [str(x) for x in lst if isinstance(x, (str, int))]
