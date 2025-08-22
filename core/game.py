import random

def simulate_game(team1, team2):
	score1 = random.randint(60, 120)
	score2 = random.randint(60, 120)
	winner = team1 if score1 > score2 else team2 if score2 > score1 else "It's a tie!"
	return team1, team2, score1, score2, winner

def generate_summary(team1, team2, score1, score2, winner):
	if winner == "It's a tie!":
		result = f"<b>{team1}</b> {score1} - {score2} <b>{team2}</b><br><span style='color:#eebbc3;'>It was a thrilling tie game!</span>"
	else:
		result = f"<b>{team1}</b> {score1} - {score2} <b>{team2}</b><br><span style='color:#eebbc3;'>Winner: <b>{winner}</b></span>"
	highlights = [
		f"{winner} dominated the paint and controlled the boards.",
		f"A last-second three-pointer sealed the win for {winner}.",
		f"Both teams showed great defense, but {winner} had the edge.",
		f"The crowd was on their feet as {winner} pulled ahead in the final minutes.",
		f"{winner} made a stunning comeback after trailing at halftime."
	]
	if winner != "It's a tie!":
		result += f"<br><i>{random.choice(highlights)}</i>"
	return result

# --- Box score generation ---
def _random_partition(total: int, parts: int, min_each: int = 0) -> list:
		"""Partition integer 'total' into 'parts' non-negative integers with at least min_each each."""
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
		"""Return a list of 'quarters' integers that sum to total, each at least min_each (clamped)."""
		# ensure min_each doesn't exceed feasible average
		feasible_min = min(min_each, max(0, total // quarters))
		base = feasible_min * quarters
		extra = max(0, total - base)
		parts = _random_partition(extra, quarters, 0)
		# random shuffle to avoid monotony
		random.shuffle(parts)
		return [feasible_min + p for p in parts]


def generate_boxscore(team1: str, team2: str, score1: int, score2: int) -> str:
	"""Generate a detailed HTML box score for both teams.

	Includes:
	- Quarter-by-quarter scoring that sums to the final score
	- Five-player lines per team with MIN, FGM-A, 3PM-A, FTM-A, REB, AST, PTS, FG%, 3P%, FT%
	- Totals row (team aggregates)
	"""
		q1 = _quarter_breakdown(score1)
		q2 = _quarter_breakdown(score2)

		# Player distributions (5 players)
		p_pts1 = _random_partition(score1, 5, 0)
		p_pts2 = _random_partition(score2, 5, 0)

		def decompose_points(points: int):
			"""Return a plausible breakdown (3PM, 2PM, FTM) that sums to points."""
			# Start with some threes
			max3 = points // 3
			three_made = random.randint(0, max3) if max3 > 0 else 0
			rem = points - 3 * three_made
			# Free throws up to remaining
			ftm = random.randint(0, min(10, rem)) if rem > 0 else 0
			rem2 = rem - ftm
			if rem2 % 2 != 0:
				# Adjust to make even for 2s
				if ftm > 0:
					ftm -= 1
					rem2 += 1
				elif three_made > 0:
					three_made -= 1
					rem2 += 3
			two_made = rem2 // 2 if rem2 >= 0 else 0
			# Ensure non-negative
			three_made = max(0, three_made)
			ftm = max(0, ftm)
			two_made = max(0, two_made)
			return three_made, two_made, ftm

		def attempts_from_made(made: int, pct_low: float, pct_high: float, fallback_max: int = 3) -> (int, float):
			"""Given made and a pct range, pick attempts and return (attempts, pct)."""
			if made <= 0:
				# zero made: either zero attempts or small attempts with low pct
				att = random.randint(0, fallback_max)
				pct = random.uniform(pct_low, pct_high)
				return att, pct
			pct = random.uniform(pct_low, pct_high)
			# ensure attempts >= made; invert pct
			att = max(made, int(round(made / max(0.05, pct))))
			return att, pct

		def build_player_statline(team: str, idx: int, pts: int):
			three_m, two_m, ft_m = decompose_points(pts)
			two_att, two_pct = attempts_from_made(two_m, 0.38, 0.62)
			three_att, three_pct = attempts_from_made(three_m, 0.28, 0.42)
			ft_att, ft_pct = attempts_from_made(ft_m, 0.68, 0.92)

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

		def team_table(team: str, pts_list: list) -> (str, dict):
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
				f"<table style='{table_style}'>" + header +
				"<tbody>" + "\n".join(rows_html) + totals_row + "</tbody></table>"
			)
			return table, totals

		table_style = (
				"border-collapse:collapse;width:100%;margin-top:8px;"
		)
		th_style = "text-align:left;border-bottom:1px solid #393d63;padding:4px;"
		td_style = "padding:4px;"

		quarters_html = f"""
		<table style="{table_style}">
			<thead>
				<tr>
					<th style="{th_style}">Team</th>
					<th style="{th_style}">Q1</th>
					<th style="{th_style}">Q2</th>
					<th style="{th_style}">Q3</th>
					<th style="{th_style}">Q4</th>
					<th style="{th_style}">Total</th>
				</tr>
			</thead>
			<tbody>
				<tr>
					<td style="{td_style}"><b>{team1}</b></td>
					<td style="text-align:right">{q1[0]}</td>
					<td style="text-align:right">{q1[1]}</td>
					<td style="text-align:right">{q1[2]}</td>
					<td style="text-align:right">{q1[3]}</td>
					<td style="text-align:right"><b>{score1}</b></td>
				</tr>
				<tr>
					<td style="{td_style}"><b>{team2}</b></td>
					<td style="text-align:right">{q2[0]}</td>
					<td style="text-align:right">{q2[1]}</td>
					<td style="text-align:right">{q2[2]}</td>
					<td style="text-align:right">{q2[3]}</td>
					<td style="text-align:right"><b>{score2}</b></td>
				</tr>
			</tbody>
		</table>
		"""

		team1_table, totals1 = team_table(team1, p_pts1)
		team2_table, totals2 = team_table(team2, p_pts2)

		return (
				"<h3 style='margin-top:12px;'>Box Score</h3>" + quarters_html +
				f"<h4 style='margin-top:12px;'>{team1}</h4>" + team1_table +
				f"<h4 style='margin-top:12px;'>{team2}</h4>" + team2_table
		)
