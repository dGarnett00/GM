import json
from pathlib import Path

# Load rosters
rosters_path = Path(__file__).parent.parent / "core" / "teams" / "data" / "rosters" / "rosters.json"
player_info_path = Path(__file__).parent.parent / "core" / "teams" / "data" / "player_info.json"

with rosters_path.open("r", encoding="utf-8") as f:
    rosters = json.load(f)

# Use Jaylen Brown as a template
jaylen_brown = {
    "position": "GF",
    "number": 7,
    "height": "6'6\"",
    "weight": "223 lbs",
    "bbref": True,
    "born": "1996 - Georgia, USA",
    "age": 26,
    "draft": "2016 - Round 1 (Pick 3) by BOS",
    "college": "California",
    "experience": "5 years",
    "contract": "$28.47M/yr thru 2024",
    "summary": {
      "G": 337,
      "MP": 27.7,
      "PTS": 15.1,
      "TRB": 4.7,
      "AST": 1.8,
      "FG%": 47.3,
      "3P%": 37.8,
      "FT%": 69.9,
      "TS%": 56.8,
      "PER": 15.1,
      "WS": 18.7
    },
    "overall": "65 (+1)",
    "potential": "69 (+1)",
    "physical": {
      "Height": 57,
      "Strength": 62,
      "Speed": 72,
      "Jumping": 58,
      "Endurance": 70
    },
    "shooting": {
      "Inside": 75,
      "Dunks/Layups": "90 (+4)",
      "Free Throws": 38,
      "Mid Range": "80 (+5)",
      "Three Pointers": "58 (-3)"
    },
    "skill": {}
}

player_infos = []
for team, players in rosters.items():
    for player in players:
        if player == "Jaylen Brown" and team == "Boston Celtics":
            info = {"name": player, "team": team}
            info.update(jaylen_brown)
        else:
            info = {
                "name": player,
                "team": team,
                "position": "?",
                "number": "?",
                "height": "?",
                "weight": "?",
                "bbref": False,
                "born": "?",
                "age": "?",
                "draft": "?",
                "college": "?",
                "experience": "?",
                "contract": "?",
                "summary": {},
                "overall": "?",
                "potential": "?",
                "physical": {},
                "shooting": {},
                "skill": {}
            }
        player_infos.append(info)

with player_info_path.open("w", encoding="utf-8") as f:
    json.dump(player_infos, f, indent=2, ensure_ascii=False)
