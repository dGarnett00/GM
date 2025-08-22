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

    p_pts1 = _random_partition(score1, 5, 0)
    p_pts2 = _random_partition(score2, 5, 0)

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

    def build_player_statline(team: str, idx: int, pts: int):
        three_m, two_m, ft_m = decompose_points(pts)
        two_att, _ = attempts_from_made(two_m, 0.38, 0.62)
        three_att, _ = attempts_from_made(three_m, 0.28, 0.42)
        ft_att, _ = attempts_from_made(ft_m, 0.68, 0.92)

        fgm = two_m + three_m
        fga = two_att + three_att
        reb = random.randint(0, 15)
        ast = random.randint(0, 12)
        minutes = random.randint(20, 36)

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
            "ast": ast,
            "pts": pts,
            "fg_pct": pct_str(fgm, fga),
            "three_pct": pct_str(three_m, three_att),
            "ft_pct": pct_str(ft_m, ft_att),
        }

    def team_table(team: str, pts_list: list):
        rows_html = []
        totals = {
            "min": 0, "fgm": 0, "fga": 0, "three_m": 0, "three_a": 0,
            "ft_m": 0, "ft_a": 0, "reb": 0, "ast": 0, "pts": 0
        }
        for i, p in enumerate(pts_list, 1):
            S = build_player_statline(team, i, p)
            totals["min"] += S["min"]
            totals["fgm"] += S["fgm"]
            totals["fga"] += S["fga"]
            totals["three_m"] += S["three_m"]
            totals["three_a"] += S["three_a"]
            totals["ft_m"] += S["ft_m"]
            totals["ft_a"] += S["ft_a"]
            totals["reb"] += S["reb"]
            totals["ast"] += S["ast"]
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
        return table, totals

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

    team1_table, _ = team_table(team1, p_pts1)
    team2_table, _ = team_table(team2, p_pts2)

    return (
        "<h3 style='margin-top:12px;'>Box Score</h3>" + quarters_html +
        f"<h4 style='margin-top:12px;'>{team1}</h4>" + team1_table +
        f"<h4 style='margin-top:12px;'>{team2}</h4>" + team2_table
    )
