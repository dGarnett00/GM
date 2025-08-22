from PyQt5.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QMenuBar, QMenu, QAction, QVBoxLayout as QVBL, QComboBox
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
from core import simulate_game, generate_summary, generate_boxscore
from core.teams import load_teams

class BasketballSimulatorWindow(QWidget):
	def __init__(self):
		super().__init__()
		self.init_ui()

	def init_ui(self):
		self.setWindowTitle('Exhibition Basketball Game Simulator')
		# Start at a friendly size but allow resizing and fullscreen
		self.resize(480, 400)
		self.setStyleSheet('background-color: #232946; color: #fffffe;')

		font_title = QFont('Arial', 20, QFont.Bold)
		font_label = QFont('Arial', 12)
		font_button = QFont('Arial', 12, QFont.Bold)

		# Menu bar
		self.menu_bar = QMenuBar(self)
		file_menu = QMenu('File', self)
		exit_action = QAction('Exit', self)
		exit_action.triggered.connect(self.close)
		file_menu.addAction(exit_action)
		self.menu_bar.addMenu(file_menu)

		# View menu
		view_menu = QMenu('View', self)
		self.fullscreen_action = QAction('Toggle Full Screen', self)
		self.fullscreen_action.setCheckable(True)
		self.fullscreen_action.setShortcut('F11')
		self.fullscreen_action.triggered.connect(self.toggle_fullscreen)
		view_menu.addAction(self.fullscreen_action)
		self.menu_bar.addMenu(view_menu)

		# Teams menu
		teams_menu = QMenu('Teams', self)
		reload_action = QAction('Reload Teams', self)
		reload_action.triggered.connect(self.reload_teams)
		teams_menu.addAction(reload_action)
		self.menu_bar.addMenu(teams_menu)

		help_menu = QMenu('Help', self)
		about_action = QAction('About', self)
		about_action.triggered.connect(self.show_about)
		help_menu.addAction(about_action)
		self.menu_bar.addMenu(help_menu)

		main_layout = QVBL()
		main_layout.setMenuBar(self.menu_bar)

		layout = QVBoxLayout()
		title = QLabel('🏀 Basketball Game Simulator')
		title.setFont(font_title)
		title.setAlignment(Qt.AlignCenter)
		layout.addWidget(title)

		team_layout = QHBoxLayout()

		def make_team_combo() -> QComboBox:
			combo = QComboBox()
			combo.setEditable(False)  # Disallow typing custom names
			combo.setFont(font_label)
			combo.setStyleSheet('padding: 4px; border-radius: 8px; background: #eebbc3; color: #232946;')
			teams = [t.name for t in load_teams()]
			combo.addItems(teams)
			return combo

		self.team1_combo = make_team_combo()
		self.team2_combo = make_team_combo()
		team_layout.addWidget(self.team1_combo)
		team_layout.addWidget(self.team2_combo)
		layout.addLayout(team_layout)

		self.simulate_btn = QPushButton('Simulate Game')
		self.simulate_btn.setFont(font_button)
		self.simulate_btn.setStyleSheet('background: #393d63; color: #fffffe; padding: 10px; border-radius: 8px;')
		self.simulate_btn.clicked.connect(self.simulate_game)
		layout.addWidget(self.simulate_btn)

		self.result_box = QTextEdit()
		self.result_box.setReadOnly(True)
		self.result_box.setFont(font_label)
		self.result_box.setStyleSheet('background: #121629; color: #fffffe; border-radius: 8px; padding: 10px;')
		layout.addWidget(self.result_box)

		main_layout.addLayout(layout)
		self.setLayout(main_layout)

	def reload_teams(self):
		"""Reload team list from core.teams and repopulate dropdowns."""
		team_names = [t.name for t in load_teams()]
		def repop(combo: QComboBox):
			current = combo.currentText()
			combo.blockSignals(True)
			combo.clear()
			combo.addItems(team_names)
			idx = combo.findText(current)
			if idx >= 0:
				combo.setCurrentIndex(idx)
			elif combo.count() > 0:
				combo.setCurrentIndex(0)
			combo.blockSignals(False)
		repop(self.team1_combo)
		repop(self.team2_combo)

	def toggle_fullscreen(self, checked=False):
		"""Toggle between fullscreen and normal window."""
		if self.isFullScreen():
			self.showNormal()
			self.fullscreen_action.setChecked(False)
		else:
			self.showFullScreen()
			self.fullscreen_action.setChecked(True)

	def show_about(self):
		from PyQt5.QtWidgets import QMessageBox
		QMessageBox.information(self, 'About', 'Basketball GM Simulator\nCreated with PyQt5')

	def keyPressEvent(self, event):
		"""Let ESC exit fullscreen; otherwise default behavior."""
		if event.key() == Qt.Key_Escape and self.isFullScreen():
			self.toggle_fullscreen()
			return
		super().keyPressEvent(event)

	def simulate_game(self):
		# Ensure we always use a valid selection from the predefined list
		if self.team1_combo.currentIndex() < 0 and self.team1_combo.count() > 0:
			self.team1_combo.setCurrentIndex(0)
		if self.team2_combo.currentIndex() < 0 and self.team2_combo.count() > 0:
			self.team2_combo.setCurrentIndex(0)
		team1 = self.team1_combo.currentText()
		team2 = self.team2_combo.currentText()
		t1, t2, score1, score2, winner = simulate_game(team1, team2)
		summary = generate_summary(t1, t2, score1, score2, winner)
		box = generate_boxscore(t1, t2, score1, score2)
		self.result_box.setHtml(summary + "<br>" + box)
