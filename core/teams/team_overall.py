
from pathlib import Path
from typing import Optional
import json

def load_team_overall(team_name: str, rosters_path: Optional[Path] = None, player_info_path: Optional[Path] = None) -> float:
    """
    Calculate the team overall (OVR) using a more realistic method:
    - Use the average of the top 8 player overalls on the roster (simulating a real NBA rotation).
    - If fewer than 8 players, average all available overalls.
    """
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
    # Sort overalls descending and take the top 8 (or all if fewer)
    overalls.sort(reverse=True)
    top_n = 8
    top_overalls = overalls[:top_n]
    return round(sum(top_overalls) / len(top_overalls), 1)
