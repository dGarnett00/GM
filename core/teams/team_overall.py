
from pathlib import Path
import json

def load_team_overall(team_name: str, rosters_path: Path = None, player_info_path: Path = None) -> float:
    """Calculate the average overall for a team."""
    if rosters_path is None:
        rosters_path = Path(__file__).resolve().parent / "data" / "rosters" / "rosters.json"
    if player_info_path is None:
        player_info_path = Path(__file__).resolve().parent / "data" / "player_info.json"
    with open(rosters_path, "r", encoding="utf-8") as f:
        rosters = json.load(f)
    with open(player_info_path, "r", encoding="utf-8") as f:
        players = json.load(f)
    player_overall = {p["name"]: p["overall"] for p in players if "overall" in p}
    roster = rosters.get(team_name, [])
    overalls = [player_overall.get(name) for name in roster]
    overalls = [o for o in overalls if o is not None]
    if not overalls:
        return 0.0
    return round(sum(overalls) / len(overalls), 1)
