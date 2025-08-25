import sys
from pathlib import Path
from core import generate_boxscore

# Ensure project root is in sys.path when running directly
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
def test_generate_boxscore_html():
    html = generate_boxscore("A", "B", 95, 90)
    assert "Box Score" in html
    assert "A" in html and "B" in html
    assert "Q1" in html and "Q4" in html
