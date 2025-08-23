import json
from pathlib import Path

# Paths
rosters_path = Path(__file__).resolve().parent.parent / "core" / "teams" / "data" / "rosters" / "rosters.json"
info_path = Path(__file__).resolve().parent.parent / "core" / "teams" / "data" / "player_info.json"
out_path = Path(__file__).resolve().parent.parent / "core" / "players" / "player_bio.json"

# Load all roster player names
with open(rosters_path, "r", encoding="utf-8") as f:
    rosters = json.load(f)
all_names = set()
for team, players in rosters.items():
    all_names.update(players)

# Load all player bios
with open(info_path, "r", encoding="utf-8") as f:
    all_bios = json.load(f)

# Build a dict for fast lookup
bio_dict = {p["name"]: p for p in all_bios if "name" in p}

# Collect bios for all roster players
bios = []
missing = []
for name in sorted(all_names):
    if name in bio_dict:
        bios.append(bio_dict[name])
    else:
        missing.append(name)

# Write pretty-printed JSON
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(bios, f, indent=2, ensure_ascii=False)

if missing:
    print("Missing bios for:", ", ".join(missing))
else:
    print("All roster players found in player_info.json.")
