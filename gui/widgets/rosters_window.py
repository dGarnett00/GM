from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget, QListWidgetItem
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtCore import Qt

from core.teams import load_teams, get_team_roster
from .player_bio import PlayerBioDialog
from gui.components.skill_badge import get_combined_badge
import json
import os


class RostersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Team Rosters')
        self.resize(500, 500)
        # Styling handled by QSS
        self.setObjectName('RostersWindow')

        title_font = QFont('Arial', 18, QFont.Bold)
        body_font = QFont('Arial', 11)

        layout = QVBoxLayout()
        title = QLabel('Team Rosters')
        title.setObjectName('TitleLabel')
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.team_combo = QComboBox()
        self.team_combo.setObjectName('TeamCombo')
        self.team_combo.setFont(body_font)
        self.team_combo.addItems([t.name for t in load_teams()])
        self.team_combo.addItem('Free Agents')
        self.team_combo.currentIndexChanged.connect(self._update_roster)
        layout.addWidget(self.team_combo)

        self.player_list = QListWidget()
        self.player_list.setObjectName('PlayerList')
        self.player_list.setFont(body_font)
        self.player_list.itemDoubleClicked.connect(self._show_player_bio)
        layout.addWidget(self.player_list)

        self.setLayout(layout)
        self._update_roster()

    def _update_roster(self):
        team = self.team_combo.currentText()
        self.player_list.clear()
        if team == 'Free Agents':
            # Load free agents from player_bio.json (team == '?')
            bio_path = os.path.join(os.path.dirname(__file__), '../../core/players/player_bio.json')
            with open(bio_path, encoding='utf-8') as f:
                data = json.load(f)
            free_agents = [p['name'] for p in data['players'] if p.get('team') == '?']
            if not free_agents:
                self.player_list.addItem('No free agents found.')
            else:
                for name in sorted(free_agents):
                    item = QListWidgetItem(name)
                    # No skill data for free agents here, keep default
                    self.player_list.addItem(item)
            return
        roster = get_team_roster(team)
        if not roster:
            self.player_list.addItem('No roster found.')
            return

        # Load skill info for players to create badges
        info_path = os.path.join(os.path.dirname(__file__), '../../core/teams/data/player_info.json')
        player_info = {}
        try:
            with open(info_path, encoding='utf-8') as f:
                data = json.load(f)
            for p in data:
                player_info[p.get('name')] = p
        except Exception:
            player_info = {}

        for name in roster:
            item = QListWidgetItem(name)
            p = player_info.get(name)
            if p:
                # Convert player info to symbols by heuristic rules
                skills = p.get('skill', {}) or {}
                shooting = p.get('shooting', {}) or {}
                physical = p.get('physical', {}) or {}
                symbols = []

                # Athlete: high Speed or Jump or Strength
                if any((physical.get('Speed', 0) >= 70, physical.get('Jump', 0) >= 70, physical.get('Strength', 0) >= 75)):
                    symbols.append('A')
                # Ball handler: high Dribble
                if skills.get('Dribble', 0) >= 65:
                    symbols.append('B')
                # Passer
                if skills.get('Pass', 0) >= 65:
                    symbols.append('Ps')
                # Rebounder
                if skills.get('Rebound', 0) >= 70:
                    symbols.append('R')
                # Interior defender vs perimeter defender using Defense IQ and position clues
                diq = skills.get('Defense IQ', 0)
                pos = p.get('position', '') or p.get('position', p.get('position', ''))
                if diq >= 65 and pos and pos.upper().find('C') != -1:
                    symbols.append('Di')
                elif diq >= 65:
                    symbols.append('Dp')
                # Post scorer: strong inside/shooting inside
                if shooting.get('Inside', 0) >= 70 or shooting.get('Field Goal', 0) >= 68:
                    symbols.append('Po')
                # Volume scorer: overall above threshold or high usage indicators
                if (p.get('overall') and isinstance(p.get('overall'), (int, float)) and p.get('overall') >= 75) or (p.get('summary', {}).get('PTS', 0) >= 18):
                    symbols.append('V')
                # Three point shooter
                if shooting.get('Three Point', 0) >= 60:
                    symbols.insert(0, '3')

                if symbols:
                    # create combined pixmap (cached) and set as icon
                    pix = get_combined_badge(symbols, size=18)
                    if not pix.isNull():
                        item.setIcon(QIcon(pix))
                    # Build tooltip text listing each symbol with numeric values
                    parts = []
                    desc_map = {
                        '3': 'Three Point Shooter', 'A': 'Athlete', 'B': 'Ball Handler',
                        'Di': 'Interior Defender', 'Dp': 'Perimeter Defender', 'Po': 'Post Scorer',
                        'Ps': 'Passer', 'R': 'Rebounder', 'V': 'Volume Scorer'
                    }
                    for s in symbols:
                        value = ''
                        if s == '3':
                            value = shooting.get('Three Point', '')
                        elif s == 'A':
                            value = f"Spd:{physical.get('Speed','')} Jmp:{physical.get('Jump','')} Str:{physical.get('Strength','')}"
                        elif s == 'B':
                            value = skills.get('Dribble', '')
                        elif s == 'Ps':
                            value = skills.get('Pass', '')
                        elif s == 'R':
                            value = skills.get('Rebound', '')
                        elif s in ('Di', 'Dp'):
                            value = skills.get('Defense IQ', '')
                        elif s == 'Po':
                            value = shooting.get('Inside', '')
                        elif s == 'V':
                            value = p.get('overall', '')
                        parts.append(f"{s} ({desc_map.get(s)}) : {value}")
                    item.setToolTip('\n'.join(parts))
            self.player_list.addItem(item)

    def _show_player_bio(self, item):
        player_name = item.text()
        dlg = PlayerBioDialog(player_name, self)
        dlg.exec_()
