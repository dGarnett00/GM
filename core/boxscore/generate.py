import random
import logging


def _random_partition(total: int, parts: int, min_each: int = 0) -> list:
    """Randomly partition a total into parts with minimum values."""
    if parts <= 0:
        return []
    if total < parts * min_each:
        return [min_each] * parts
    
    remaining = max(0, total - parts * min_each)
    cuts = sorted(random.randint(0, remaining) for _ in range(parts - 1))
    seq = [cuts[0] if cuts else 0]
    for i in range(1, parts - 1):
        seq.append(cuts[i] - cuts[i - 1])
    seq.append(remaining - (cuts[-1] if cuts else 0))
    return [x + min_each for x in seq]


def _quarter_breakdown(total: int, quarters: int = 4, min_each: int = 10) -> list:
    """Break down total score into quarters with error handling."""
    try:
        if total <= 0 or quarters <= 0:
            return [0] * max(1, quarters)
        
        feasible_min = min(min_each, max(0, total // quarters))
        base = feasible_min * quarters
        extra = max(0, total - base)
        parts = _random_partition(extra, quarters, 0)
        random.shuffle(parts)
        result = [feasible_min + p for p in parts]
        
        # Ensure the sum equals total
        current_sum = sum(result)
        if current_sum != total:
            diff = total - current_sum
            result[0] += diff
            result[0] = max(0, result[0])
        
        return result
    except Exception:
        # Fallback: distribute evenly
        base = total // quarters if quarters > 0 else total
        remainder = total % quarters if quarters > 0 else 0
        result = [base] * quarters
        for i in range(remainder):
            result[i] += 1
        return result


def generate_boxscore(team1: str, team2: str, score1: int, score2: int) -> str:
    """Generate detailed boxscore with comprehensive error handling."""
    logger = logging.getLogger('basketball_gm')
    
    try:
        # Input validation
        if not team1 or not isinstance(team1, str):
            team1 = "Team A"
        if not team2 or not isinstance(team2, str):
            team2 = "Team B"
        
        team1, team2 = team1.strip(), team2.strip()
        
        # Validate scores
        try:
            score1 = int(score1) if score1 is not None else 0
            score2 = int(score2) if score2 is not None else 0
        except (ValueError, TypeError):
            logger.warning("Invalid scores provided, using defaults")
            score1, score2 = 100, 95
        
        # Ensure positive scores
        score1, score2 = max(0, score1), max(0, score2)
        
        # Try to load real rosters by team display name; fall back to synthetic if unavailable
        try:
            from core.teams import get_team_roster  # lazy import to avoid circular deps in some environments
        except Exception as e:  # pragma: no cover - best-effort import
            logger.warning(f"Could not import roster function: {e}")
            get_team_roster = None

        roster1 = []
        roster2 = []
        
        if get_team_roster:
            try:
                roster1 = get_team_roster(team1)
                roster2 = get_team_roster(team2)
            except Exception as e:
                logger.warning(f"Error loading rosters: {e}")

        # Generate quarter breakdowns
        q1 = _quarter_breakdown(score1)
        q2 = _quarter_breakdown(score2)

        def _points_distribution_dynamic(total_points: int, roster_len: int, starters_share: float = 0.68):
            """Distribute points among players with error handling."""
            try:
                # Default to 10 players if roster is empty
                if roster_len <= 0:
                    starters = 5
                    bench = 5
                else:
                    starters = min(5, roster_len)
                    bench = max(0, roster_len - starters)
                
                if total_points <= 0:
                    return [0] * (starters + bench)
                
                starters_pts_total = int(round(total_points * starters_share))
                bench_pts_total = total_points - starters_pts_total
                starters_pts = _random_partition(starters_pts_total, starters, 0)
                bench_pts = _random_partition(bench_pts_total, bench, 0)
                return starters_pts + bench_pts
            except Exception:
                # Fallback: distribute evenly
                total_players = max(1, roster_len if roster_len > 0 else 10)
                base_points = total_points // total_players
                remainder = total_points % total_players
                result = [base_points] * total_players
                for i in range(remainder):
                    result[i] += 1
                return result

        # Distribute points across actual roster size; if empty, use 10 synthetic players
        n1 = len(roster1) if roster1 else 10
        n2 = len(roster2) if roster2 else 10
        p_pts1 = _points_distribution_dynamic(score1, n1)
        p_pts2 = _points_distribution_dynamic(score2, n2)

        def decompose_points(points: int):
            """Decompose total points into 2PT, 3PT, and FT with error handling."""
            try:
                points = max(0, int(points))
                max3 = points // 3
                three_made = random.randint(0, max3) if max3 > 0 else 0
                rem = points - 3 * three_made
                ftm = random.randint(0, min(10, rem)) if rem > 0 else 0
                rem2 = rem - ftm
                if rem2 % 2 != 0:
                    if ftm > 0:
                        ftm -= 1
                        rem2 += 1
                    elif three_made > 0:
                        three_made -= 1
                        rem2 += 3
                two_made = rem2 // 2 if rem2 >= 0 else 0
                three_made = max(0, three_made)
                ftm = max(0, ftm)
                two_made = max(0, two_made)
                return three_made, two_made, ftm
            except Exception:
                # Fallback: mostly 2-pointers
                return 0, points // 2, points % 2

        def attempts_from_made(made: int, pct_low: float, pct_high: float, fallback_max: int = 3):
            """Calculate attempts from made shots with error handling."""
            try:
                made = max(0, int(made))
                if made <= 0:
                    att = random.randint(0, fallback_max)
                    pct = random.uniform(pct_low, pct_high)
                    return att, pct
                pct = random.uniform(max(0.01, pct_low), min(0.99, pct_high))
                att = max(made, int(round(made / max(0.05, pct))))
                return att, pct
            except Exception:
                return max(made, 1), 0.5

        def build_player_statline(player_name: str, pts: int, is_starter: bool, team_score: int, opp_score: int):
            """Build complete player stats with error handling."""
            try:
                pts = max(0, int(pts))
                three_m, two_m, ft_m = decompose_points(pts)
                two_att, _ = attempts_from_made(two_m, 0.38, 0.62)
                three_att, _ = attempts_from_made(three_m, 0.28, 0.42)
                ft_att, _ = attempts_from_made(ft_m, 0.68, 0.92)

                fgm = two_m + three_m
                fga = two_att + three_att
                reb = random.randint(0, 15)
                ast = random.randint(0, 12)
                minutes = random.randint(28, 36) if is_starter else random.randint(8, 22)

                stl = random.randint(0, 4 if is_starter else 3)
                blk = random.randint(0, 3 if is_starter else 2)
                tov = random.randint(0, 6 if is_starter else 4)
                pf = random.randint(0, 5)

                # Split rebounds into offensive/defensive (kept out of per-player columns to avoid width)
                oreb = random.randint(0, reb)
                dreb = reb - oreb

                team_diff = team_score - opp_score
                pm_bias = 1 if (is_starter and team_diff > 0) else (-1 if (is_starter and team_diff < 0) else 0)
                plus_minus = random.randint(-5, 5) + int(team_diff / 5) + pm_bias

                def pct_str(m, a):
                    return f"{(m / a * 100):.0f}%" if a > 0 else "-"

                return {
                    "player": str(player_name),
                    "min": minutes,
                    "fgm": fgm,
                    "fga": fga,
                    "three_m": three_m,
                    "three_a": three_att,
                    "ft_m": ft_m,
                    "ft_a": ft_att,
                    "reb": reb,
                    "oreb": oreb,
                    "dreb": dreb,
                    "ast": ast,
                    "stl": stl,
                    "blk": blk,
                    "tov": tov,
                    "pf": pf,
                    "+/-": plus_minus,
                    "pts": pts,
                    "fg_pct": pct_str(fgm, fga),
                    "three_pct": pct_str(three_m, three_att),
                    "ft_pct": pct_str(ft_m, ft_att),
                }
            except Exception as e:
                logger.warning(f"Error building player stats for {player_name}: {e}")
                # Return minimal valid statline
                return {
                    "player": str(player_name),
                    "min": 20, "fgm": 0, "fga": 0, "three_m": 0, "three_a": 0,
                    "ft_m": 0, "ft_a": 0, "reb": 0, "oreb": 0, "dreb": 0, "ast": 0,
                    "stl": 0, "blk": 0, "tov": 0, "pf": 0, "+/-": 0, "pts": pts,
                    "fg_pct": "-", "three_pct": "-", "ft_pct": "-"
                }

        # Rest of the function continues with the table generation...
        return _generate_boxscore_tables(team1, team2, score1, score2, q1, q2, p_pts1, p_pts2, roster1, roster2, build_player_statline)
        
    except Exception as e:
        logger.error(f"Error generating boxscore: {e}")
        # Return minimal boxscore
        return f"""
        <h3 style='margin-top:12px;'>Box Score</h3>
        <div style='margin:8px 0;'>
        <b>{team1}</b> {score1} - {score2} <b>{team2}</b><br>
        Error generating detailed statistics. Please try again.
        </div>
        """


def _generate_boxscore_tables(team1: str, team2: str, score1: int, score2: int, 
                             q1: list, q2: list, p_pts1: list, p_pts2: list,
                             roster1: list, roster2: list, build_player_statline):
    """Generate the HTML tables for the boxscore."""
    
    def team_table(team: str, pts_list: list, team_score: int, opp_score: int, roster_names: list[str] | None = None):
        """Generate team statistics table with error handling."""
        try:
            rows_html = []
            totals = {
                "min": 0, "fgm": 0, "fga": 0, "three_m": 0, "three_a": 0,
                "ft_m": 0, "ft_a": 0, "reb": 0, "oreb": 0, "dreb": 0, "ast": 0, 
                "stl": 0, "blk": 0, "tov": 0, "pf": 0, "pts": 0
            }
            statlines = []
            total_players = len(pts_list)
            starters_cut = min(5, total_players)
            
            for i, p in enumerate(pts_list, 1):
                is_starter = i <= starters_cut
                name = None
                if roster_names and i - 1 < len(roster_names):
                    name = str(roster_names[i - 1])
                if not name or not name.strip():
                    name = f"{team} Player {i}"
                    
                S = build_player_statline(name, p, is_starter, team_score, opp_score)
                statlines.append(S)
                
                # Insert grouping headers
                if i == 1:
                    rows_html.append(
                        "<tr><td colspan='16' style='text-align:left;padding:6px 4px;background:#2b2f55;color:#fffffe;'><b>Starters</b></td></tr>"
                    )
                if i == starters_cut + 1:
                    rows_html.append(
                        "<tr><td colspan='16' style='text-align:left;padding:6px 4px;background:#2b2f55;color:#fffffe;'><b>Bench</b></td></tr>"
                    )
                
                # Accumulate totals
                for key in totals:
                    if key in S:
                        totals[key] += S[key]
                
                rows_html.append(
                    "<tr>"
                    f"<td>{S['player']}</td>"
                    f"<td style='text-align:right'>{S['min']}</td>"
                    f"<td style='text-align:right'>{S['fgm']}-{S['fga']}</td>"
                    f"<td style='text-align:right'>{S['three_m']}-{S['three_a']}</td>"
                    f"<td style='text-align:right'>{S['ft_m']}-{S['ft_a']}</td>"
                    f"<td style='text-align:right'>{S['reb']}</td>"
                    f"<td style='text-align:right'>{S['ast']}</td>"
                    f"<td style='text-align:right'>{S['stl']}</td>"
                    f"<td style='text-align:right'>{S['blk']}</td>"
                    f"<td style='text-align:right'>{S['tov']}</td>"
                    f"<td style='text-align:right'>{S['pf']}</td>"
                    f"<td style='text-align:right'>{S['+/-']}</td>"
                    f"<td style='text-align:right'><b>{S['pts']}</b></td>"
                    f"<td style='text-align:right'>{S['fg_pct']}</td>"
                    f"<td style='text-align:right'>{S['three_pct']}</td>"
                    f"<td style='text-align:right'>{S['ft_pct']}</td>"
                    "</tr>"
                )

            def pct_str(m, a):
                return f"{(m / a * 100):.0f}%" if a > 0 else "-"

            totals_row = (
                "<tr>"
                "<td><b>Totals</b></td>"
                f"<td style='text-align:right'><b>{totals['min']}</b></td>"
                f"<td style='text-align:right'><b>{totals['fgm']}-{totals['fga']}</b></td>"
                f"<td style='text-align:right'><b>{totals['three_m']}-{totals['three_a']}</b></td>"
                f"<td style='text-align:right'><b>{totals['ft_m']}-{totals['ft_a']}</b></td>"
                f"<td style='text-align:right'><b>{totals['reb']}</b></td>"
                f"<td style='text-align:right'><b>{totals['ast']}</b></td>"
                f"<td style='text-align:right'><b>{totals['stl']}</b></td>"
                f"<td style='text-align:right'><b>{totals['blk']}</b></td>"
                f"<td style='text-align:right'><b>{totals['tov']}</b></td>"
                f"<td style='text-align:right'><b>{totals['pf']}</b></td>"
                f"<td style='text-align:right'><b>{(team_score - opp_score)}</b></td>"
                f"<td style='text-align:right'><b>{totals['pts']}</b></td>"
                f"<td style='text-align:right'><b>{pct_str(totals['fgm'], totals['fga'])}</b></td>"
                f"<td style='text-align:right'><b>{pct_str(totals['three_m'], totals['three_a'])}</b></td>"
                f"<td style='text-align:right'><b>{pct_str(totals['ft_m'], totals['ft_a'])}</b></td>"
                "</tr>"
            )

            header = (
                "<thead><tr>"
                "<th style='text-align:left;border-bottom:1px solid #393d63;padding:4px'>Player</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>MIN</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>FGM-A</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>3PM-A</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>FTM-A</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>REB</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>AST</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>STL</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>BLK</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>TOV</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>PF</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>+/-</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>PTS</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>FG%</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>3P%</th>"
                "<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>FT%</th>"
                "</tr></thead>"
            )

            table = (
                "<table style='border-collapse:collapse;width:100%;margin-top:8px;'>" + header +
                "<tbody>" + "\n".join(rows_html) + totals_row + "</tbody></table>"
            )
            return table, totals, statlines
            
        except Exception as e:
            logging.getLogger('basketball_gm').error(f"Error generating team table: {e}")
            return f"<div>Error generating {team} statistics</div>", {}, []

    # Generate quarter breakdown table
    quarters_html = f"""
    <table style="border-collapse:collapse;width:100%;margin-top:8px;">
      <thead>
        <tr>
          <th style="text-align:left;border-bottom:1px solid #393d63;padding:4px;">Team</th>
          <th style="text-align:left;border-bottom:1px solid #393d63;padding:4px;">Q1</th>
          <th style="text-align:left;border-bottom:1px solid #393d63;padding:4px;">Q2</th>
          <th style="text-align:left;border-bottom:1px solid #393d63;padding:4px;">Q3</th>
          <th style="text-align:left;border-bottom:1px solid #393d63;padding:4px;">Q4</th>
          <th style="text-align:left;border-bottom:1px solid #393d63;padding:4px;">Total</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="padding:4px;"><b>{team1}</b></td>
          <td style="text-align:right">{q1[0] if len(q1) > 0 else 0}</td>
          <td style="text-align:right">{q1[1] if len(q1) > 1 else 0}</td>
          <td style="text-align:right">{q1[2] if len(q1) > 2 else 0}</td>
          <td style="text-align:right">{q1[3] if len(q1) > 3 else 0}</td>
          <td style="text-align:right"><b>{score1}</b></td>
        </tr>
        <tr>
          <td style="padding:4px;"><b>{team2}</b></td>
          <td style="text-align:right">{q2[0] if len(q2) > 0 else 0}</td>
          <td style="text-align:right">{q2[1] if len(q2) > 1 else 0}</td>
          <td style="text-align:right">{q2[2] if len(q2) > 2 else 0}</td>
          <td style="text-align:right">{q2[3] if len(q2) > 3 else 0}</td>
          <td style="text-align:right"><b>{score2}</b></td>
        </tr>
      </tbody>
    </table>
    """

    team1_table, totals1, stats1 = team_table(team1, p_pts1, score1, score2, roster1)
    team2_table, totals2, stats2 = team_table(team2, p_pts2, score2, score1, roster2)

    # Generate additional sections (MVP, team comparison, etc.)
    mvp_section = _generate_mvp_section(stats1, stats2)
    comparison_section = _generate_team_comparison(team1, totals1, team2, totals2)
    
    return (
        "<h3 style='margin-top:12px;'>Box Score</h3>" +
        mvp_section +
        quarters_html +
        comparison_section +
        f"<h4 style='margin-top:12px;'>{team1}</h4>" + team1_table +
        f"<h4 style='margin-top:12px;'>{team2}</h4>" + team2_table
    )


def _generate_mvp_section(stats1: list, stats2: list) -> str:
    """Generate MVP section with error handling."""
    try:
        def game_score(s):
            try:
                made = s.get('fgm', 0)
                fga = s.get('fga', 0)
                ftm = s.get('ft_m', 0)
                fta = s.get('ft_a', 0)
                return (
                    s.get('pts', 0) + s.get('reb', 0) + s.get('ast', 0) + 
                    s.get('stl', 0) + s.get('blk', 0) - (fga - made) - (fta - ftm) - s.get('tov', 0)
                )
            except Exception:
                return s.get('pts', 0)
        
        all_stats = (stats1 or []) + (stats2 or [])
        if not all_stats:
            return ""
        
        mvp = max(all_stats, key=game_score)
        return (
            f"<div style='margin:8px 0;padding:6px;background:#2b2f55;color:#fffffe;border-radius:6px;'>"
            f"<b>Game MVP:</b> {mvp.get('player', 'Unknown')} — "
            f"{mvp.get('pts', 0)} PTS, {mvp.get('reb', 0)} REB, {mvp.get('ast', 0)} AST, "
            f"{mvp.get('stl', 0)} STL, {mvp.get('blk', 0)} BLK"
            f"</div>"
        )
    except Exception:
        return ""


def _generate_team_comparison(team_a: str, t1: dict, team_b: str, t2: dict) -> str:
    """Generate team comparison table with error handling."""
    try:
        def pct(m, a):
            return f"{(m / a * 100):.0f}%" if a > 0 else "-"
        
        def safe_get(d, key, default=0):
            return d.get(key, default) if isinstance(d, dict) else default
        
        def row(label, a, b):
            return (
                "<tr>"
                f"<td style='padding:4px'>{label}</td>"
                f"<td style='text-align:right;padding:4px'>{a}</td>"
                f"<td style='text-align:right;padding:4px'>{b}</td>"
                "</tr>"
            )
        
        efg1 = (safe_get(t1, 'fgm') + 0.5 * safe_get(t1, 'three_m')) / safe_get(t1, 'fga', 1)
        efg2 = (safe_get(t2, 'fgm') + 0.5 * safe_get(t2, 'three_m')) / safe_get(t2, 'fga', 1)
        
        header = (
            "<thead><tr>"
            "<th style='text-align:left;border-bottom:1px solid #393d63;padding:4px'>Team Comparison</th>"
            f"<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>{team_a}</th>"
            f"<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>{team_b}</th>"
            "</tr></thead>"
        )
        
        body = "".join([
            row("FG", f"{safe_get(t1, 'fgm')}-{safe_get(t1, 'fga')} ({pct(safe_get(t1, 'fgm'), safe_get(t1, 'fga'))})", 
                f"{safe_get(t2, 'fgm')}-{safe_get(t2, 'fga')} ({pct(safe_get(t2, 'fgm'), safe_get(t2, 'fga'))})"),
            row("3P", f"{safe_get(t1, 'three_m')}-{safe_get(t1, 'three_a')} ({pct(safe_get(t1, 'three_m'), safe_get(t1, 'three_a'))})", 
                f"{safe_get(t2, 'three_m')}-{safe_get(t2, 'three_a')} ({pct(safe_get(t2, 'three_m'), safe_get(t2, 'three_a'))})"),
            row("eFG%", f"{efg1*100:.0f}%", f"{efg2*100:.0f}%"),
            row("REB", safe_get(t1, 'reb'), safe_get(t2, 'reb')),
            row("AST", safe_get(t1, 'ast'), safe_get(t2, 'ast')),
            row("TOV", safe_get(t1, 'tov'), safe_get(t2, 'tov')),
        ])
        
        return (
            "<table style='border-collapse:collapse;width:100%;margin-top:8px;'>" +
            header + f"<tbody>{body}</tbody></table>"
        )
    except Exception:
        return "<div>Error generating team comparison</div>"
