from PyQt5.QtWidgets import QWidget, QVBoxLayout, QComboBox, QLabel
from PyQt5.QtGui import QFont
from PyQt5.QtCore import pyqtSignal, Qt
from core.teams import load_teams
from core.teams.team_overall import load_team_overall

class TeamSelector(QWidget):
    teamChanged = pyqtSignal(str)

    def __init__(self, label_font: QFont | None = None, parent=None):
        super().__init__(parent)
        self._label_font = label_font or QFont('Arial', 12)
        self.combo = QComboBox()
        self.combo.setEditable(False)
        self.combo.currentIndexChanged.connect(self._emit_change)
        self.ovr_label = QLabel()
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
        self.combo.addItems(teams)
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
