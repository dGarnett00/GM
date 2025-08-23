from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont
import json
from pathlib import Path

class PlayerBioDialog(QDialog):
    def __init__(self, player_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Player Bio - {player_name}")
        self.resize(350, 200)
        layout = QVBoxLayout()
        font = QFont('Arial', 12)

        # Load player info
        info = self._get_player_info(player_name)
        if info:
            for k, v in info.items():
                label = QLabel(f"<b>{k.title()}:</b> {v}")
                label.setFont(font)
                layout.addWidget(label)
        else:
            label = QLabel("No player info found.")
            label.setFont(font)
            layout.addWidget(label)
        self.setLayout(layout)

    def _get_player_info(self, player_name):
        path = Path(__file__).parent.parent.parent / "core" / "teams" / "data" / "player_info.json"
        if not path.exists():
            return None
        with path.open("r", encoding="utf-8") as f:
            try:
                data = json.load(f)
            except Exception:
                return None
        for entry in data:
            if entry.get("name") == player_name:
                return entry
        return None
