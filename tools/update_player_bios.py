import json
from pathlib import Path

# Paths
ROOT = Path(__file__).resolve().parents[1]
NBA_ROSTER_PATH = ROOT / "2025-26.NBA.Roster.json"
PLAYER_INFO_PATH = ROOT / "core" / "teams" / "data" / "player_info.json"
TEAMS_PATH = ROOT / "core" / "teams" / "data" / "teams.json"

# Load team id to name mapping
with TEAMS_PATH.open("r", encoding="utf-8") as f:
    teams = json.load(f)
tid_to_team = {t["tid"]: f"{t['region']} {t['name']}" for t in teams if isinstance(t, dict) and "tid" in t}

def get_latest_rating(ratings):
    if not ratings:
        return {}
    return max(ratings, key=lambda r: r.get("season", 0))

def player_to_bio(player):
    import datetime
    ratings = player.get("ratings", [])
    rating = get_latest_rating(ratings)
    contract = player.get("contract", {})
    draft = player.get("draft", {})
    born = player.get("born", {})
    team = tid_to_team.get(player.get("tid"), "?")
    amount = contract.get('amount', '?')
    if isinstance(amount, int):
        amount_str = f"${amount:,}"
    else:
        amount_str = f"${amount}"

    # Calculate age
    current_year = 2025  # Set to roster's starting season or use datetime.datetime.now().year
    birth_year = born.get("year") if isinstance(born, dict) else None
    age = current_year - birth_year if birth_year and isinstance(birth_year, int) else "?"

    # Estimate experience
    draft_year = draft.get("year") if isinstance(draft, dict) else None
    experience = current_year - draft_year if draft_year and isinstance(draft_year, int) else "?"

    # Summary stats (career totals/averages)
    summary = {}
    stats = player.get("stats", [])
    if stats:
        # Use regular season only, not playoffs
        reg_stats = [s for s in stats if not s.get("playoffs")]
        if reg_stats:
            # Career totals/averages
            G = sum(s.get("gp", 0) for s in reg_stats)
            MP = sum(s.get("min", 0) for s in reg_stats)
            PTS = sum(s.get("pts", 0) for s in reg_stats)
            TRB = sum(s.get("orb", 0) + s.get("drb", 0) for s in reg_stats)
            AST = sum(s.get("ast", 0) for s in reg_stats)
            FGA = sum(s.get("fga", 0) for s in reg_stats)
            FGM = sum(s.get("fg", 0) for s in reg_stats)
            FG_PCT = round(FGM / FGA * 100, 1) if FGA else "?"
            TPA = sum(s.get("tpa", 0) for s in reg_stats)
            TPM = sum(s.get("tp", 0) for s in reg_stats)
            TP_PCT = round(TPM / TPA * 100, 1) if TPA else "?"
            FTA = sum(s.get("fta", 0) for s in reg_stats)
            FTM = sum(s.get("ft", 0) for s in reg_stats)
            FT_PCT = round(FTM / FTA * 100, 1) if FTA else "?"
            TS_PCT = "?"  # True shooting% could be calculated if needed
            PER = reg_stats[-1].get("per", "?")
            WS = reg_stats[-1].get("ows", 0) + reg_stats[-1].get("dws", 0) if reg_stats else "?"
            summary = {
                "G": G,
                "MP": MP,
                "PTS": PTS,
                "TRB": TRB,
                "AST": AST,
                "FG%": FG_PCT,
                "3P%": TP_PCT,
                "FT%": FT_PCT,
                "TS%": TS_PCT,
                "PER": PER,
                "WS": WS
            }

    # Physical, Shooting, Skill from latest rating
    physical = {}
    shooting = {}
    skill = {}
    if rating:
        # Example mapping, adjust as needed
        physical = {
            "Height": player.get('hgt', '?'),
            "Weight": player.get('weight', '?'),
            "Strength": rating.get('stre', '?'),
            "Speed": rating.get('spd', '?'),
            "Jump": rating.get('jmp', '?'),
            "Endurance": rating.get('endu', '?')
        }
        shooting = {
            "Inside": rating.get('ins', '?'),
            "Dunk": rating.get('dnk', '?'),
            "Free Throw": rating.get('ft', '?'),
            "Field Goal": rating.get('fg', '?'),
            "Three Point": rating.get('tp', '?')
        }
        skill = {
            "Defense IQ": rating.get('diq', '?'),
            "Offense IQ": rating.get('oiq', '?'),
            "Dribble": rating.get('drb', '?'),
            "Pass": rating.get('pss', '?'),
            "Rebound": rating.get('reb', '?')
        }

    # Compute overall as average of key rating attributes
    def compute_overall(r):
        keys = ["stre", "spd", "jmp", "endu", "ins", "dnk", "ft", "fg", "tp", "diq", "oiq", "drb", "pss", "reb"]
        values = [r.get(k, 0) for k in keys if isinstance(r.get(k, 0), (int, float))]
        return round(sum(values) / len(values), 1) if values else "?"

    overall = compute_overall(rating) if rating else "?"
    # Potential as max overall from all ratings
    potential = max((compute_overall(r) for r in ratings if r), default="?")

    return {
        "name": player.get("name", "?"),
        "team": team,
        "position": player.get("pos", "?"),
        "number": player.get("stats", [{}])[-1].get("jerseyNumber", "?"),
        "height": f"{player.get('hgt', '?')} in",  # or convert to ft/in
        "weight": f"{player.get('weight', '?')} lbs",
        "bbref": bool(player.get("srID")),
        "born": birth_year if birth_year else "?",
        "age": age,
        "draft": f"{draft.get('year', '?')} R{draft.get('round', '?')} P{draft.get('pick', '?')}",
        "college": player.get("college", "?"),
        "experience": experience,
        "contract": f"{amount_str} exp {contract.get('exp', '?')}",
        "summary": summary,
        "overall": overall,
        "potential": potential,
        "physical": physical,
        "shooting": shooting,
        "skill": skill
    }

# Load NBA roster
with NBA_ROSTER_PATH.open("r", encoding="utf-8") as f:
    data = json.load(f)
players = data["players"]

bios = [player_to_bio(p) for p in players]

with PLAYER_INFO_PATH.open("w", encoding="utf-8") as f:
    json.dump(bios, f, indent=2, ensure_ascii=False)

print(f"Updated {PLAYER_INFO_PATH} with {len(bios)} player bios.")
