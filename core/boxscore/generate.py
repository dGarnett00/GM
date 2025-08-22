import random


def _random_partition(total: int, parts: int, min_each: int = 0) -> list:
    if parts <= 0:
        return []
    remaining = max(0, total - parts * min_each)
    cuts = sorted(random.randint(0, remaining) for _ in range(parts - 1))
    seq = [cuts[0] if cuts else 0]
    for i in range(1, parts - 1):
        seq.append(cuts[i] - cuts[i - 1])
    seq.append(remaining - (cuts[-1] if cuts else 0))
    return [x + min_each for x in seq]


def _quarter_breakdown(total: int, quarters: int = 4, min_each: int = 10) -> list:
    feasible_min = min(min_each, max(0, total // quarters))
    base = feasible_min * quarters
    extra = max(0, total - base)
    parts = _random_partition(extra, quarters, 0)
    random.shuffle(parts)
    return [feasible_min + p for p in parts]


def generate_boxscore(team1: str, team2: str, score1: int, score2: int) -> str:
    q1 = _quarter_breakdown(score1)
    q2 = _quarter_breakdown(score2)

    def _points_distribution(total_points: int, starters: int = 5, bench: int = 5, starters_share: float = 0.68):
        starters_pts_total = int(round(total_points * starters_share))
        bench_pts_total = total_points - starters_pts_total
        starters_pts = _random_partition(starters_pts_total, starters, 0)
        bench_pts = _random_partition(bench_pts_total, bench, 0)
        return starters_pts + bench_pts

    # 10 players per team: 5 starters + 5 bench
    p_pts1 = _points_distribution(score1)
    p_pts2 = _points_distribution(score2)

    def decompose_points(points: int):
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

    def attempts_from_made(made: int, pct_low: float, pct_high: float, fallback_max: int = 3):
        if made <= 0:
            att = random.randint(0, fallback_max)
            pct = random.uniform(pct_low, pct_high)
            return att, pct
        pct = random.uniform(pct_low, pct_high)
        att = max(made, int(round(made / max(0.05, pct))))
        return att, pct

    def build_player_statline(team: str, idx: int, pts: int, is_starter: bool, team_score: int, opp_score: int):
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
            "player": f"{team} Player {idx}",
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

    def team_table(team: str, pts_list: list, team_score: int, opp_score: int):
        rows_html = []
        totals = {
            "min": 0, "fgm": 0, "fga": 0, "three_m": 0, "three_a": 0,
            "ft_m": 0, "ft_a": 0, "reb": 0, "oreb": 0, "dreb": 0, "ast": 0, "stl": 0, "blk": 0, "tov": 0, "pf": 0, "pts": 0
        }
        statlines = []
        for i, p in enumerate(pts_list, 1):
            is_starter = i <= 5
            S = build_player_statline(team, i, p, is_starter, team_score, opp_score)
            statlines.append(S)
            # Insert grouping headers
            if i == 1:
                rows_html.append(
                    "<tr><td colspan='16' style='text-align:left;padding:6px 4px;background:#2b2f55;color:#fffffe;'><b>Starters</b></td></tr>"
                )
            if i == 6:
                rows_html.append(
                    "<tr><td colspan='16' style='text-align:left;padding:6px 4px;background:#2b2f55;color:#fffffe;'><b>Bench</b></td></tr>"
                )
            totals["min"] += S["min"]
            totals["fgm"] += S["fgm"]
            totals["fga"] += S["fga"]
            totals["three_m"] += S["three_m"]
            totals["three_a"] += S["three_a"]
            totals["ft_m"] += S["ft_m"]
            totals["ft_a"] += S["ft_a"]
            totals["reb"] += S["reb"]
            totals["oreb"] += S["oreb"]
            totals["dreb"] += S["dreb"]
            totals["ast"] += S["ast"]
            totals["stl"] += S["stl"]
            totals["blk"] += S["blk"]
            totals["tov"] += S["tov"]
            totals["pf"] += S["pf"]
            totals["pts"] += S["pts"]
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
          <td style="text-align:right">{q1[0]}</td>
          <td style="text-align:right">{q1[1]}</td>
          <td style="text-align:right">{q1[2]}</td>
          <td style="text-align:right">{q1[3]}</td>
          <td style="text-align:right"><b>{score1}</b></td>
        </tr>
        <tr>
          <td style="padding:4px;"><b>{team2}</b></td>
          <td style="text-align:right">{q2[0]}</td>
          <td style="text-align:right">{q2[1]}</td>
          <td style="text-align:right">{q2[2]}</td>
          <td style="text-align:right">{q2[3]}</td>
          <td style="text-align:right"><b>{score2}</b></td>
        </tr>
      </tbody>
    </table>
    """

    team1_table, totals1, stats1 = team_table(team1, p_pts1, score1, score2)
    team2_table, totals2, stats2 = team_table(team2, p_pts2, score2, score1)

    def leaders_html(team_name: str, stats: list) -> str:
        if not stats:
            return ""
        top_pts = max(stats, key=lambda s: s["pts"])
        top_reb = max(stats, key=lambda s: s["reb"])
        top_ast = max(stats, key=lambda s: s["ast"])
        return (
            f"<div style='margin:6px 0;font-size:12px;'><b>Leaders — {team_name}:</b> "
            f"PTS: {top_pts['player']} ({top_pts['pts']}) • "
            f"REB: {top_reb['player']} ({top_reb['reb']}) • "
            f"AST: {top_ast['player']} ({top_ast['ast']})"
            "</div>"
        )

    def pct(m, a):
        return f"{(m / a * 100):.0f}%" if a > 0 else "-"

    def team_shooting_summary(team_name: str, totals: dict) -> str:
        # Advanced rates
        efg = (totals['fgm'] + 0.5 * totals['three_m']) / totals['fga'] if totals['fga'] > 0 else 0.0
        ts = totals['pts'] / (2 * (totals['fga'] + 0.44 * totals['ft_a'])) if (totals['fga'] + 0.44 * totals['ft_a']) > 0 else 0.0
        return (
            f"<div style='margin:4px 0 8px 0;font-size:12px;color:#eebbc3;'>"
            f"<b>{team_name}</b> shooting — "
            f"FG: {totals['fgm']}-{totals['fga']} ({pct(totals['fgm'], totals['fga'])}) • "
            f"3P: {totals['three_m']}-{totals['three_a']} ({pct(totals['three_m'], totals['three_a'])}) • "
            f"FT: {totals['ft_m']}-{totals['ft_a']} ({pct(totals['ft_m'], totals['ft_a'])}) • "
            f"eFG%: {efg*100:.0f}% • TS%: {ts*100:.0f}%"
            f"</div>"
        )

    def team_comparison(team_a: str, t1: dict, team_b: str, t2: dict) -> str:
        def row(label, a, b):
            return (
                "<tr>"
                f"<td style='padding:4px'>{label}</td>"
                f"<td style='text-align:right;padding:4px'>{a}</td>"
                f"<td style='text-align:right;padding:4px'>{b}</td>"
                "</tr>"
            )
        efg1 = (t1['fgm'] + 0.5 * t1['three_m']) / t1['fga'] if t1['fga'] > 0 else 0.0
        efg2 = (t2['fgm'] + 0.5 * t2['three_m']) / t2['fga'] if t2['fga'] > 0 else 0.0
        ts1 = t1['pts'] / (2 * (t1['fga'] + 0.44 * t1['ft_a'])) if (t1['fga'] + 0.44 * t1['ft_a']) > 0 else 0.0
        ts2 = t2['pts'] / (2 * (t2['fga'] + 0.44 * t2['ft_a'])) if (t2['fga'] + 0.44 * t2['ft_a']) > 0 else 0.0
        header = (
            "<thead><tr>"
            "<th style='text-align:left;border-bottom:1px solid #393d63;padding:4px'>Team Comparison</th>"
            f"<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>{team_a}</th>"
            f"<th style='text-align:right;border-bottom:1px solid #393d63;padding:4px'>{team_b}</th>"
            "</tr></thead>"
        )
        body = "".join([
            row("FG", f"{t1['fgm']}-{t1['fga']} ({pct(t1['fgm'], t1['fga'])})", f"{t2['fgm']}-{t2['fga']} ({pct(t2['fgm'], t2['fga'])})"),
            row("3P", f"{t1['three_m']}-{t1['three_a']} ({pct(t1['three_m'], t1['three_a'])})", f"{t2['three_m']}-{t2['three_a']} ({pct(t2['three_m'], t2['three_a'])})"),
            row("FT", f"{t1['ft_m']}-{t1['ft_a']} ({pct(t1['ft_m'], t1['ft_a'])})", f"{t2['ft_m']}-{t2['ft_a']} ({pct(t2['ft_m'], t2['ft_a'])})"),
            row("eFG%", f"{efg1*100:.0f}%", f"{efg2*100:.0f}%"),
            row("TS%", f"{ts1*100:.0f}%", f"{ts2*100:.0f}%"),
            row("REB", t1['reb'], t2['reb']),
            row("OREB", t1['oreb'], t2['oreb']),
            row("DREB", t1['dreb'], t2['dreb']),
            row("AST", t1['ast'], t2['ast']),
            row("STL", t1['stl'], t2['stl']),
            row("BLK", t1['blk'], t2['blk']),
            row("TOV", t1['tov'], t2['tov']),
            row("PF", t1['pf'], t2['pf']),
        ])
        return (
            "<table style='border-collapse:collapse;width:100%;margin-top:8px;'>" +
            header + f"<tbody>{body}</tbody></table>"
        )

    def mvp_html(stats_a: list, stats_b: list) -> str:
        def game_score(s):
            made = s['fgm']
            fga = s['fga']
            ftm = s['ft_m']
            fta = s['ft_a']
            return (
                s['pts'] + s['reb'] + s['ast'] + s['stl'] + s['blk']
                - (fga - made) - (fta - ftm) - s['tov']
            )
        all_stats = (stats_a or []) + (stats_b or [])
        if not all_stats:
            return ""
        mvp = max(all_stats, key=game_score)
        return (
            f"<div style='margin:8px 0;padding:6px;background:#2b2f55;color:#fffffe;border-radius:6px;'>"
            f"<b>Game MVP:</b> {mvp['player']} — "
            f"{mvp['pts']} PTS, {mvp['reb']} REB, {mvp['ast']} AST, {mvp['stl']} STL, {mvp['blk']} BLK"
            f"</div>"
        )

    return (
        "<h3 style='margin-top:12px;'>Box Score</h3>" +
        mvp_html(stats1, stats2) +
        quarters_html +
        team_comparison(team1, totals1, team2, totals2) +
        f"<h4 style='margin-top:12px;'>{team1}</h4>" + team_shooting_summary(team1, totals1) + team1_table + leaders_html(team1, stats1) +
        f"<h4 style='margin-top:12px;'>{team2}</h4>" + team_shooting_summary(team2, totals2) + team2_table + leaders_html(team2, stats2)
    )
