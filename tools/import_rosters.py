import json
import sys
from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parents[1]
TEAMS_PATH = ROOT / "core" / "teams" / "data" / "teams.json"
ROSTERS_PATH = ROOT / "core" / "teams" / "data" / "rosters" / "rosters.json"


def load_tid_to_name() -> Dict[int, str]:
    with TEAMS_PATH.open("r", encoding="utf-8") as f:
        teams = json.load(f)
    mapping: Dict[int, str] = {}
    for item in teams:
        if isinstance(item, dict):
            tid = item.get("tid")
            if isinstance(tid, int):
                region = item.get("region")
                name = item.get("name")
                disp = f"{region} {name}".strip() if region and name else (name or "")
                if disp:
                    mapping[tid] = disp
    return mapping


def player_display_name(p: dict) -> str | None:
    name = p.get("name")
    if name:
        return str(name)
    first = p.get("firstName")
    last = p.get("lastName")
    if first or last:
        parts = [x for x in [first, last] if x]
        return " ".join(parts)
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/import_rosters.py <path-to-NBA-roster.json>")
        sys.exit(1)
    src = Path(sys.argv[1])
    if not src.exists():
        print(f"Source file not found: {src}")
        sys.exit(2)

    with src.open("r", encoding="utf-8") as f:
        data = json.load(f)
    players = data.get("players") if isinstance(data, dict) else data
    if not isinstance(players, list):
        print("Invalid source format: expected an object with 'players' or a list")
        sys.exit(3)

    tid_to_name = load_tid_to_name()
    rosters: Dict[str, List[str]] = {v: [] for v in tid_to_name.values()}

    for p in players:
        if not isinstance(p, dict):
            continue
        tid = p.get("tid")
        if not isinstance(tid, int) or tid not in tid_to_name:
            continue
        pname = player_display_name(p)
        if not pname:
            continue
        team_name = tid_to_name[tid]
        lst = rosters.setdefault(team_name, [])
        if pname not in lst:
            lst.append(pname)

    ROSTERS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with ROSTERS_PATH.open("w", encoding="utf-8") as f:
        json.dump(rosters, f, indent=2, ensure_ascii=False)
    print(f"Wrote {ROSTERS_PATH} with {sum(len(v) for v in rosters.values())} players across {len(rosters)} teams.")


if __name__ == "__main__":
    main()
