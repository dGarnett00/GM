import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ROSTERS_PATH = ROOT / "core" / "teams" / "data" / "rosters" / "rosters.json"
TEAMS_PATH = ROOT / "core" / "teams" / "data" / "teams.json"


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: Path, data):
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_team_display_names():
    teams = load_json(TEAMS_PATH)
    names = []
    for t in teams:
        region = t.get("region") or ""
        name = t.get("name") or t.get("team") or ""
        disp = f"{region} {name}".strip()
        names.append(disp)
    return names


def indicators():
    # Minimal, robust indicators per team; case-insensitive exact string match on roster entries
    return {
        "Atlanta Hawks": {"Trae Young", "Dejounte Murray", "Onyeka Okongwu", "Jalen Johnson", "Clint Capela"},
        "Boston Celtics": {"Jayson Tatum", "Jaylen Brown", "Kristaps Porzingis", "Derrick White", "Payton Pritchard"},
        "Brooklyn Nets": {"Nic Claxton", "Cam Thomas", "Day'Ron Sharpe", "Mikal Bridges", "Noah Clowney"},
        "New York Knicks": {"Jalen Brunson", "Julius Randle", "Mitchell Robinson", "OG Anunoby", "Josh Hart"},
        "Philadelphia 76ers": {"Joel Embiid", "Tyrese Maxey"},
        "Toronto Raptors": {"Scottie Barnes", "R.J. Barrett", "Immanuel Quickley", "Jakob Poeltl", "Gradey Dick"},
        "Chicago Bulls": {"Zach LaVine", "DeMar DeRozan", "Nikola Vucevic", "Coby White"},
        "Cleveland Cavaliers": {"Donovan Mitchell", "Darius Garland", "Evan Mobley", "Jarrett Allen"},
        "Detroit Pistons": {"Cade Cunningham", "Jalen Duren", "Jaden Ivey", "Ausar Thompson", "Isaiah Stewart"},
        "Indiana Pacers": {"Tyrese Haliburton", "Pascal Siakam", "Myles Turner", "Bennedict Mathurin", "Andrew Nembhard", "Obi Toppin"},
        "Milwaukee Bucks": {"Giannis Antetokounmpo", "Khris Middleton", "Brook Lopez"},
        "Charlotte Hornets": {"LaMelo Ball", "Brandon Miller", "Mark Williams", "Miles Bridges"},
        "Miami Heat": {"Jimmy Butler", "Bam Adebayo", "Tyler Herro"},
        "Orlando Magic": {"Paolo Banchero", "Franz Wagner", "Wendell Carter Jr.", "Jalen Suggs"},
        "Washington Wizards": {"Kyle Kuzma", "Jordan Poole", "Deni Avdija", "Tyus Jones"},
        "Denver Nuggets": {"Nikola Jokic", "Jamal Murray", "Michael Porter Jr.", "Aaron Gordon"},
        "Minnesota Timberwolves": {"Anthony Edwards", "Karl-Anthony Towns", "Rudy Gobert", "Jaden McDaniels", "Naz Reid"},
        "Oklahoma City Thunder": {"Shai Gilgeous-Alexander", "Chet Holmgren", "Jalen Williams"},
        "Portland Trail Blazers": {"Scoot Henderson", "Shaedon Sharpe", "Anfernee Simons", "Deandre Ayton", "Jerami Grant"},
        "Utah Jazz": {"Lauri Markkanen", "Walker Kessler", "Keyonte George", "Collin Sexton"},
        "Golden State Warriors": {"Stephen Curry", "Klay Thompson", "Draymond Green"},
        "Los Angeles Clippers": {"Kawhi Leonard", "Paul George", "James Harden", "Ivica Zubac", "Norman Powell"},
        "Los Angeles Lakers": {"LeBron James", "Anthony Davis", "Austin Reaves", "D'Angelo Russell"},
        "Phoenix Suns": {"Devin Booker", "Kevin Durant", "Bradley Beal"},
        "Sacramento Kings": {"De'Aaron Fox", "Domantas Sabonis", "Keegan Murray"},
        "Dallas Mavericks": {"Luka Doncic", "Kyrie Irving", "Dereck Lively II", "Daniel Gafford"},
        "Houston Rockets": {"Jalen Green", "Alperen Sengun", "Jabari Smith Jr.", "Amen Thompson", "Dillon Brooks"},
        "Memphis Grizzlies": {"Ja Morant", "Jaren Jackson Jr.", "Desmond Bane"},
        "New Orleans Pelicans": {"Zion Williamson", "Brandon Ingram", "C.J. McCollum", "CJ McCollum", "Herbert Jones"},
        "San Antonio Spurs": {"Victor Wembanyama", "Devin Vassell", "Keldon Johnson", "Jeremy Sochan"},
    }


def score_roster(roster, name_set):
    rset = {str(x).strip() for x in roster}
    return len(rset & name_set)


def main():
    rosters = load_json(ROSTERS_PATH)
    team_names = set(get_team_display_names())
    hints = indicators()

    # Ensure hints cover exactly team_names intersection
    hints = {k: v for k, v in hints.items() if k in team_names}

    # Build candidate scores: for each existing roster (by current key), compute scores to each team
    roster_by_old_key = rosters
    scored = []  # (bestScore, bestTeam, oldKey, roster, allScores)
        # Player-related logic removed

    # Assign greedily by best score
    scored.sort(key=lambda x: x[0], reverse=True)
    assigned = {}
    leftover = []
        # Player-related logic removed

    # Fill any remaining teams with leftover in arbitrary order; if still empty, keep their old key players if unique
    remaining_teams = [t for t in team_names if t not in assigned]
    for team, (old_key, players) in zip(remaining_teams, leftover):
        assigned[team] = players

    # As a final pass, ensure we didn't drop any team: if some teams still missing, preserve their original mapping
    for t in team_names:
        if t not in assigned and t in roster_by_old_key:
            assigned[t] = roster_by_old_key[t]

    # Backup and write
    backup = ROSTERS_PATH.with_suffix(".json.bak")
    save_json(backup, rosters)
    # Sort keys alphabetically for readability
    ordered = {k: assigned[k] for k in sorted(assigned.keys())}
    save_json(ROSTERS_PATH, ordered)

    # Print a tiny summary
    print(f"Repaired rosters written to {ROSTERS_PATH}")
    print(f"Backup saved to {backup}")


if __name__ == "__main__":
    main()
