import sys
from pathlib import Path

# Ensure project root is in sys.path when running directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.game import simulate_game, generate_summary


def test_simulate_game_basic():
    t1, t2, s1, s2, winner = simulate_game("A", "B")
    assert t1 == "A" and t2 == "B"
    assert 60 <= s1 <= 120 and 60 <= s2 <= 120
    assert winner in ("A", "B", "It's a tie!")


def test_generate_summary_html():
    html = generate_summary("A", "B", 100, 98, "A")
    assert "Winner" in html and "A" in html
