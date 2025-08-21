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
        import random
        result += f"<br><i>{random.choice(highlights)}</i>"
    return result
