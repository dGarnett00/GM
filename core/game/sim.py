import random
import sys
import traceback


# Lightweight team ratings to influence results. Values are illustrative.
# ORtg/DRtg ~ points per 100 possessions, Pace ~ possessions per 48 minutes.
_DEFAULT = {"ortg": 111.0, "drtg": 111.0, "pace": 99.0}
_TEAM_RATINGS = {
    # Stronger teams
    "Boston Celtics": {"ortg": 119.0, "drtg": 110.0, "pace": 98.5},
    "Denver Nuggets": {"ortg": 117.5, "drtg": 111.5, "pace": 96.5},
    "Oklahoma City Thunder": {"ortg": 117.0, "drtg": 111.0, "pace": 99.5},
    "Dallas Mavericks": {"ortg": 116.5, "drtg": 112.5, "pace": 98.0},
    "Minnesota Timberwolves": {"ortg": 114.5, "drtg": 109.5, "pace": 96.0},
    "Milwaukee Bucks": {"ortg": 117.0, "drtg": 113.0, "pace": 100.0},
    "New York Knicks": {"ortg": 115.5, "drtg": 111.5, "pace": 95.5},
    # Solid
    "Phoenix Suns": {"ortg": 115.5, "drtg": 112.0, "pace": 97.5},
    "Los Angeles Lakers": {"ortg": 114.0, "drtg": 112.0, "pace": 100.5},
    "Golden State Warriors": {"ortg": 114.0, "drtg": 113.5, "pace": 101.5},
    "Philadelphia 76ers": {"ortg": 114.5, "drtg": 111.5, "pace": 99.0},
    "Los Angeles Clippers": {"ortg": 115.0, "drtg": 112.5, "pace": 97.5},
    "Miami Heat": {"ortg": 112.5, "drtg": 111.0, "pace": 95.0},
    "Sacramento Kings": {"ortg": 115.0, "drtg": 113.5, "pace": 100.5},
    # Rebuilding/struggling
    "Detroit Pistons": {"ortg": 109.0, "drtg": 115.0, "pace": 99.5},
    "Washington Wizards": {"ortg": 111.0, "drtg": 118.0, "pace": 102.0},
    "Charlotte Hornets": {"ortg": 110.0, "drtg": 116.0, "pace": 98.5},
}


def _ratings_for(team: str):
    return _TEAM_RATINGS.get(team, _DEFAULT)


def _simulate_scores(team1: str, team2: str):
    try:
        r1 = _ratings_for(team1)
        r2 = _ratings_for(team2)

        # Home/away advantage: +1.5 ortg for home team (team1)
        home_adv = 1.5
        r1_ortg = r1["ortg"] + home_adv
        r2_ortg = r2["ortg"]

        # Possessions derived from pace with some randomness
        pace_avg = (r1["pace"] + r2["pace"]) / 2.0
        poss = max(85, min(110, int(round(random.gauss(pace_avg, 2.8)))))

        # Offensive efficiencies adjusted by opposing defense and random variance
        def eff(ortg, opp_drtg):
            base = (ortg + (112.0 - opp_drtg))
            noise = random.gauss(0, 3.5)
            clutch = random.uniform(-1.0, 1.0)
            return max(100.0, min(125.0, base + noise + clutch))

        e1 = eff(r1_ortg, r2["drtg"])
        e2 = eff(r2_ortg, r1["drtg"])

        pts1 = int(round(poss * e1 / 100.0))
        pts2 = int(round(poss * e2 / 100.0))

        # Small end-game variance swing
        swing = random.randint(-3, 3)
        if swing > 0:
            pts1 += swing
        elif swing < 0:
            pts2 += -swing

        # Clamp to keep within existing test expectations
        pts1 = max(60, min(120, pts1))
        pts2 = max(60, min(120, pts2))

        # Add team streak/consistency: random chance for a "hot" or "cold" game
        streak_chance = random.random()
        if streak_chance < 0.08:
            pts1 += random.randint(5, 12)  # hot streak
        elif streak_chance > 0.92:
            pts1 -= random.randint(5, 12)  # cold streak
        streak_chance2 = random.random()
        if streak_chance2 < 0.08:
            pts2 += random.randint(5, 12)
        elif streak_chance2 > 0.92:
            pts2 -= random.randint(5, 12)
        pts1 = max(60, min(130, pts1))
        pts2 = max(60, min(130, pts2))

        # Overtime logic: if tied, simulate up to 3 OTs
        ot_count = 0
        while pts1 == pts2 and ot_count < 3:
            ot_count += 1
            ot1 = random.randint(7, 15) + int((e1 - 100) / 5)
            ot2 = random.randint(7, 15) + int((e2 - 100) / 5)
            # Add fatigue: slightly reduce efficiency each OT
            ot1 = max(6, ot1 - ot_count)
            ot2 = max(6, ot2 - ot_count)
            pts1 += ot1
            pts2 += ot2
            pts1 = min(140, pts1)
            pts2 = min(140, pts2)
        # If still tied after 3 OTs, nudge one team
        if pts1 == pts2:
            if random.random() < 0.5:
                pts1 += 1
            else:
                pts2 += 1
        return pts1, pts2, ot_count
    except Exception as e:
        print(f"[ERROR] _simulate_scores failed for teams '{team1}' vs '{team2}': {e}")
        traceback.print_exc()
        return 80, 80, 0  # fallback safe values


def simulate_game(team1, team2):
    try:
        score1, score2, ot_count = _simulate_scores(team1, team2)

        # Resolve ties with overtime segments (should not occur, but fallback)
        ot = ot_count
        while score1 == score2:
            ot += 1
            add1 = random.randint(7, 15)
            add2 = random.randint(7, 15)
            score1 += add1
            score2 += add2
            score1 = min(score1, 140)
            score2 = min(score2, 140)
            if score1 == score2 == 140:
                score1 -= 1

        winner = team1 if score1 > score2 else team2
        return team1, team2, score1, score2, winner, ot_count
    except Exception as e:
        print(f"[ERROR] simulate_game failed for teams '{team1}' vs '{team2}': {e}")
        traceback.print_exc()
        return team1, team2, 80, 80, team1, 0  # fallback safe values


def generate_summary(team1, team2, score1, score2, winner, ot_count=0):
    try:
        is_tie = (winner == "It's a tie!")
        ot_text = f" ({ot_count}OT)" if ot_count == 1 else (f" ({ot_count}OTs)" if ot_count > 1 else "")
        if is_tie:
            result = (
                f"<b>{team1}</b> {score1} - {score2} <b>{team2}</b>"
                f"<br><span style='color:#eebbc3;'>It was a thrilling tie game!{ot_text}</span>"
            )
        else:
            result = (
                f"<b>{team1}</b> {score1} - {score2} <b>{team2}</b>"
                f"<br><span style='color:#eebbc3;'>Winner: <b>{winner}</b>{ot_text}</span>"
            )

        margin = abs(score1 - score2)
        close_game = margin <= 3
        blowout = margin >= 20

        ot_tag = ot_count > 0
        if not is_tie:
            if ot_tag or close_game:
                highlights = [
                    f"A clutch bucket in the final seconds lifted {winner.split(' (')[0]}.",
                    f"{winner.split(' (')[0]} survived a furious late rally to edge it out.",
                    f"Free throws down the stretch made the difference for {winner.split(' (')[0]}.",
                    f"{winner.split(' (')[0]} outlasted their opponent in a dramatic overtime.",
                ]
            elif blowout:
                highlights = [
                    f"{winner.split(' (')[0]} dominated end-to-end in a statement win.",
                    f"Defense fueled offense as {winner.split(' (')[0]} ran away with it.",
                ]
            else:
                highlights = [
                    f"Balanced scoring carried {winner.split(' (')[0]} to victory.",
                    f"{winner.split(' (')[0]} controlled the tempo and the glass.",
                    f"Bench production proved key for {winner.split(' (')[0]}.",
                ]
            result += f"<br><i>{random.choice(highlights)}</i>"
        return result
    except Exception as e:
        print(f"[ERROR] generate_summary failed for teams '{team1}' vs '{team2}' (winner: {winner}): {e}")
        traceback.print_exc()
        return f"<b>{team1}</b> ? - ? <b>{team2}</b><br><span style='color:#eebbc3;'>[Summary unavailable due to error]</span>"

# Global error handler for uncaught exceptions in this module
def _global_exception_handler(exctype, value, tb):
    print("[FATAL] Uncaught exception in sim.py:")
    traceback.print_exception(exctype, value, tb)
sys.excepthook = _global_exception_handler
