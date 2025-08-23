from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt

from core.teams import load_teams, get_team_roster


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

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(body_font)
        self.text.setStyleSheet('background: #121629; color: #fffffe; border-radius: 8px; padding: 10px;')
        layout.addWidget(self.text)

        self.setLayout(layout)
        self._update_roster()

    def _update_roster(self):
        team = self.team_combo.currentText()
        roster = get_team_roster(team)
        if not roster:
            self.text.setPlainText('No roster found.')
            return
        self.text.setPlainText('\n'.join(roster))
