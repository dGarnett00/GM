from dataclasses import dataclass
from pathlib import Path
import json
from typing import List


@dataclass
class Team:
    name: str


def _default_teams_path() -> Path:
    return Path(__file__).resolve().parent / "data" / "teams.json"


def load_teams(path: Path | None = None) -> List[Team]:
    p = Path(path) if path else _default_teams_path()
    if not p.exists():
        # Fallback to a small built-in list
        return [Team(name=n) for n in [
            "Lakers", "Warriors", "Celtics", "Bulls", "Heat", "Suns"
        ]]
    with p.open("r", encoding="utf-8") as f:
        data = json.load(f)
    teams = []
    for item in data:
        name = item.get("name") if isinstance(item, dict) else str(item)
        if name:
            teams.append(Team(name=name))
    return teams
