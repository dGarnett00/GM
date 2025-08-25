from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel
from PyQt5.QtGui import QFont
import json
from pathlib import Path

class PlayerBioDialog(QDialog):
    def __init__(self, player_name, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Player Bio - {player_name}")
        self.resize(400, 600)
        layout = QVBoxLayout()
        font = QFont('Arial', 12)

        info = self._get_player_info(player_name)
        if info:
            # Header
            header = QLabel(f"<b>{info.get('name', 'Player')}</b>")
            header.setFont(QFont('Arial', 16, QFont.Bold))
            layout.addWidget(header)

            # Position, Team, Number
            pos_team = f"{info.get('position', '')}, {info.get('team', '')}, #{info.get('number', '')}"
            layout.addWidget(QLabel(pos_team))

            # Height, Weight, BBRef
            hw = f"{info.get('height', '')}, {info.get('weight', '')}"
            if info.get('bbref'):
                hw += " - BBRef"
            layout.addWidget(QLabel(hw))

            # Born, Age
            layout.addWidget(QLabel(f"Born: {info.get('born', '')}"))
            layout.addWidget(QLabel(f"Age: {info.get('age', '')}"))

            # Draft, College, Experience, Contract
            layout.addWidget(QLabel(f"Draft: {info.get('draft', '')}"))
            layout.addWidget(QLabel(f"College: {info.get('college', '')}"))
            layout.addWidget(QLabel(f"Experience: {info.get('experience', '')}"))
            layout.addWidget(QLabel(f"Contract: {info.get('contract', '')}"))

            # 3PoV (if present)
            layout.addWidget(QLabel("<b>3PoV</b>"))

            # Summary Table
            summary = info.get('summary', {})
            if summary:
                summary_header = QLabel("<b>Summary</b>   G     MP    PTS   TRB   AST   FG%   3P%   FT%   TS%   PER   WS")
                layout.addWidget(summary_header)
                summary_row = QLabel(f"Career  {summary.get('G','')}   {summary.get('MP','')}   {summary.get('PTS','')}   {summary.get('TRB','')}   {summary.get('AST','')}   {summary.get('FG%','')}   {summary.get('3P%','')}   {summary.get('FT%','')}   {summary.get('TS%','')}   {summary.get('PER','')}   {summary.get('WS','')}")
                layout.addWidget(summary_row)

            # Overall, Potential
            layout.addWidget(QLabel(f"Overall: {info.get('overall', '')}"))
            layout.addWidget(QLabel(f"Potential: {info.get('potential', '')}"))

            # Physical
            layout.addWidget(QLabel("<b>Physical</b>"))
            for k, v in (info.get('physical', {}) or {}).items():
                layout.addWidget(QLabel(f"{k}: {v}"))

            # Shooting
            layout.addWidget(QLabel("<b>Shooting</b>"))
            for k, v in (info.get('shooting', {}) or {}).items():
                layout.addWidget(QLabel(f"{k}: {v}"))

            # Skill
            layout.addWidget(QLabel("<b>Skill</b>"))
            skills = info.get('skill', {}) or {}
            # Mapping of short symbol -> full description
            symbol_desc = {
                '3': 'Three Point Shooter',
                'A': 'Athlete',
                'B': 'Ball Handler',
                'Di': 'Interior Defender',
                'Dp': 'Perimeter Defender',
                'Po': 'Post Scorer',
                'Ps': 'Passer',
                'R': 'Rebounder',
                'V': 'Volume Scorer',
            }
            # Display each skill symbol with tooltip and associated numeric rating when available
            for sym, val in skills.items():
                lbl = QLabel()
                desc = symbol_desc.get(sym, '')
                if desc:
                    lbl.setText(f"<b>{sym}</b>")
                    lbl.setToolTip(f"{desc} — {val}")
                else:
                    lbl.setText(f"{sym}: {val}")
                layout.addWidget(lbl)

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
