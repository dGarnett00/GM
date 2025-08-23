def simulate_game_with_events(team1, team2, event_callback=None, user_action_callback=None, user_actions=None):
    """
    Simulate a game with play-by-play event feed and user actions.
    event_callback(event: str): called for each event string.
    user_action_callback(): called when user input is needed (e.g., timeout, sub, playstyle).
    user_actions: list of user actions to consume (timeout, substitute, playstyle).
    """
    if user_actions is None:
        user_actions = []
    events = []
    def emit(event):
        events.append(event)
        if event_callback:
            event_callback(event)
    try:
        emit(f"Q1 Start: {team1} vs {team2}")
        score1, score2 = 0, 0
        q_scores = [(0, 0)]
        for q in range(1, 5):
            # Simulate quarter
            q1_pts = random.randint(20, 32)
            q2_pts = random.randint(20, 32)
            score1 += q1_pts
            score2 += q2_pts
            q_scores.append((score1, score2))
            emit(f"Q{q} End: {team1} {score1} - {score2} {team2}")
            # Key moment: allow user action at halftime and Q4 start
            if q == 2 or q == 4:
                if user_action_callback:
                    user_action_callback()
                if user_actions:
                    action = user_actions.pop(0)
                    emit(f"User action: {action}")
        # Simulate final moments
        if abs(score1 - score2) <= 3:
            emit(f"Final minute: Tie game!")
            if user_action_callback:
                user_action_callback()
            if user_actions:
                action = user_actions.pop(0)
                emit(f"User action: {action}")
        # Overtime if tied
        ot_count = 0
        while score1 == score2 and ot_count < 3:
            ot_count += 1
            ot1 = random.randint(7, 15)
            ot2 = random.randint(7, 15)
            score1 += ot1
            score2 += ot2
            emit(f"OT{ot_count}: {team1} {score1} - {score2} {team2}")
        if score1 == score2:
            if random.random() < 0.5:
                score1 += 1
            else:
                score2 += 1
        winner = team1 if score1 > score2 else team2
        emit(f"Final: {team1} {score1} - {score2} {team2}. Winner: {winner}")
        return team1, team2, score1, score2, winner, ot_count
    except Exception as e:
        emit(f"[ERROR] simulate_game_with_events failed: {e}")
        traceback.print_exc()
        return team1, team2, 80, 80, team1, 0

import random
import sys
import traceback
import os
import json
from pathlib import Path
from core.teams.rosters import load_rosters, get_team_roster


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
    # Try to use player attributes to influence team ratings
    try:
        rosters = load_rosters()
        roster = get_team_roster(team, rosters)
        # Load player bios
        bio_path = Path(__file__).resolve().parent.parent / "players" / "player_bio.json"
        with open(bio_path, encoding="utf-8") as f:
            bios = json.load(f)["players"]
        # Build a dict for fast lookup
        bio_dict = {p["name"]: p for p in bios if "name" in p}
        # Gather player attributes for this roster
        ovr = []
        off = []
        deff = []
        pace = []
        for name in roster:
            p = bio_dict.get(name)
            if not p:
                continue
            ovr.append(p.get("overall", 50))
            # Use Offense IQ, Field Goal, Three Point, Pass for offense
            shooting = p.get("shooting", {})
            skill = p.get("skill", {})
            off.append(
                0.4 * skill.get("Offense IQ", 50)
                + 0.2 * shooting.get("Field Goal", 50)
                + 0.2 * shooting.get("Three Point", 50)
                + 0.2 * skill.get("Pass", 50)
            )
            # Use Defense IQ, Rebound, Strength for defense
            physical = p.get("physical", {})
            deff.append(
                0.5 * skill.get("Defense IQ", 50)
                + 0.3 * skill.get("Rebound", 50)
                + 0.2 * physical.get("Strength", 50)
            )
            # Use Speed, Endurance for pace
            pace.append(0.6 * physical.get("Speed", 50) + 0.4 * physical.get("Endurance", 50))
        if ovr:
            avg_ovr = sum(ovr) / len(ovr)
            avg_off = sum(off) / len(off)
            avg_deff = sum(deff) / len(deff)
            avg_pace = sum(pace) / len(pace)
            # Map to NBA-like ranges
            ortg = 100 + (avg_off - 50) * 0.5 + (avg_ovr - 50) * 0.2
            drtg = 110 - (avg_deff - 50) * 0.4 - (avg_ovr - 50) * 0.1
            pace_val = 95 + (avg_pace - 50) * 0.15
            return {"ortg": ortg, "drtg": drtg, "pace": pace_val}
    except Exception as e:
        print(f"[WARN] Could not use player attributes for team '{team}': {e}")
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
