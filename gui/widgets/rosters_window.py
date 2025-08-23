from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QListWidget
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from core.teams import load_teams, get_team_roster
from .player_bio import PlayerBioDialog



class RostersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Team Rosters')
        self.resize(500, 500)
        self.setStyleSheet('background-color: #232946; color: #fffffe;')

        title_font = QFont('Arial', 18, QFont.Bold)
        body_font = QFont('Arial', 11)

        layout = QVBoxLayout()
        title = QLabel('Team Rosters')
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.team_combo = QComboBox()
        self.team_combo.setStyleSheet('padding: 4px; border-radius: 8px; background: #eebbc3; color: #232946;')
        self.team_combo.setFont(body_font)
        self.team_combo.addItems([t.name for t in load_teams()])
        self.team_combo.currentIndexChanged.connect(self._update_roster)
        layout.addWidget(self.team_combo)

        self.player_list = QListWidget()
        self.player_list.setFont(body_font)
        self.player_list.setStyleSheet('background: #121629; color: #fffffe; border-radius: 8px; padding: 10px;')
        self.player_list.itemDoubleClicked.connect(self._show_player_bio)
        layout.addWidget(self.player_list)

        self.setLayout(layout)
        self._update_roster()

    def _update_roster(self):
        team = self.team_combo.currentText()
        roster = get_team_roster(team)
        self.player_list.clear()
        if not roster:
            self.player_list.addItem('No roster found.')
            return
        self.player_list.addItems(roster)

    def _show_player_bio(self, item):
        player_name = item.text()
        dlg = PlayerBioDialog(player_name, self)
        dlg.exec_()
