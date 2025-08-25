from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import pyqtSignal, Qt
from core.teams import load_teams, get_team_roster
from core.teams.team_overall import load_team_overall
from gui.components.skill_badge import get_combined_badge
import os
import json


class TeamSelector(QWidget):
    teamChanged = pyqtSignal(str)

    def __init__(self, label_font: QFont | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName('TeamSelector')
        self._label_font = label_font or QFont('Arial', 12)

        self.combo = QComboBox()
        self.combo.setObjectName('TeamCombo')
        self.combo.setEditable(False)
        self.combo.currentIndexChanged.connect(self._emit_change)

        self.ovr_label = QLabel()
        self.ovr_label.setObjectName('OvrLabel')
        self.ovr_label.setAlignment(Qt.AlignCenter)
        self.ovr_label.setFont(self._label_font)

        layout = QVBoxLayout()
        layout.addWidget(self.combo)
        layout.addWidget(self.ovr_label)
        self.setLayout(layout)

        self.reload()

    def reload(self):
        teams = [t.name for t in load_teams()]
        current = self.combo.currentText()
        self.combo.blockSignals(True)
        self.combo.clear()
        # Populate combo with team names and optional badge icons
        info_path = os.path.join(os.path.dirname(__file__), '../../core/teams/data/player_info.json')
        player_info = {}
        try:
            with open(info_path, encoding='utf-8') as f:
                pdata = json.load(f)
            for p in pdata:
                player_info[p.get('name')] = p
        except Exception:
            player_info = {}

        for tname in teams:
            self.combo.addItem(tname)
            # Build team-level symbols by sampling roster
            try:
                roster = get_team_roster(tname) or []
            except Exception:
                roster = []
            symbols = []
            # simple heuristic: collect top symbols from first few players
            for pname in roster[:5]:
                p = player_info.get(pname)
                if not p:
                    continue
                skills = p.get('skill', {}) or {}
                shooting = p.get('shooting', {}) or {}
                physical = p.get('physical', {}) or {}
                if any((physical.get('Speed', 0) >= 70, physical.get('Jump', 0) >= 70, physical.get('Strength', 0) >= 75)):
                    symbols.append('A')
                if skills.get('Dribble', 0) >= 65:
                    symbols.append('B')
                if skills.get('Pass', 0) >= 65:
                    symbols.append('Ps')
                if skills.get('Rebound', 0) >= 70:
                    symbols.append('R')
                diq = skills.get('Defense IQ', 0)
                pos = p.get('position', '') or p.get('position', p.get('position', ''))
                if diq >= 65 and pos and pos.upper().find('C') != -1:
                    symbols.append('Di')
                elif diq >= 65:
                    symbols.append('Dp')
                if shooting.get('Inside', 0) >= 70 or shooting.get('Field Goal', 0) >= 68:
                    symbols.append('Po')
                if (p.get('overall') and isinstance(p.get('overall'), (int, float)) and p.get('overall') >= 75) or (p.get('summary', {}).get('PTS', 0) >= 18):
                    symbols.append('V')
                if shooting.get('Three Point', 0) >= 60:
                    symbols.insert(0, '3')
            # dedupe while preserving order
            seen = set()
            symbols = [s for s in symbols if not (s in seen or seen.add(s))]
            if symbols:
                pix = get_combined_badge(symbols, size=14)
                if pix and not pix.isNull():
                    idx = self.combo.findText(tname)
                    if idx >= 0:
                        self.combo.setItemIcon(idx, QIcon(pix))
        # restore previous selection if possible
        idx = self.combo.findText(current)
        if idx >= 0:
            self.combo.setCurrentIndex(idx)
        elif self.combo.count() > 0:
            self.combo.setCurrentIndex(0)
        self.combo.blockSignals(False)
        self._update_ovr()

    def currentTeam(self) -> str:
        return self.combo.currentText()

    def setCurrentIndex(self, i: int):
        self.combo.setCurrentIndex(i)

    def _emit_change(self, *_):
        self._update_ovr()
        self.teamChanged.emit(self.currentTeam())

    def _update_ovr(self):
        team = self.currentTeam()
        ovr = load_team_overall(team)
        self.ovr_label.setText(f"OVR: {ovr}" if ovr else "")
