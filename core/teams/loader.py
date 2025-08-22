from dataclasses import dataclass
from pathlib import Path
import json
from typing import List, Optional


@dataclass
class Team:
    # Display name used throughout the app (kept for backward compatibility)
    name: str

    # Rich metadata (optional)
    tid: Optional[int] = None
    cid: Optional[int] = None  # 0 = East, 1 = West
    did: Optional[int] = None  # 0..5 divisions
    region: Optional[str] = None
    abbrev: Optional[str] = None
    pop: Optional[float] = None  # in millions
    stadiumCapacity: Optional[int] = None


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
        if isinstance(item, dict):
            # Prefer region+name if provided, else "name" as-is
            region = item.get("region")
            base_name = item.get("name")
            display_name = (f"{region} {base_name}".strip()) if region and base_name else (base_name or "")
            if display_name:
                teams.append(
                    Team(
                        name=display_name,
                        tid=item.get("tid"),
                        cid=item.get("cid"),
                        did=item.get("did"),
                        region=region,
                        abbrev=item.get("abbrev"),
                        pop=item.get("pop"),
                        stadiumCapacity=item.get("stadiumCapacity"),
                    )
                )
        else:
            name = str(item)
            if name:
                teams.append(Team(name=name))
    return teams
