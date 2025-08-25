from PyQt5.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, QMenuBar, QMenu, QAction, QVBoxLayout as QVBL, QComboBox, QFileDialog, QMessageBox, QListWidget
)
# Boxscore generation available in core, but not used here after simulation removal
from PyQt5.QtGui import QFont, QGuiApplication
from PyQt5.QtCore import Qt
# generate_summary removed with simulation
from core.teams import load_teams
from core.teams.team_overall import load_team_overall
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import os
import random

class BasketballSimulatorWindow(QWidget):
	def __init__(self):
		super().__init__()
		self._main_menu = None
		self.init_ui()

	def init_ui(self):
		self.setWindowTitle('Basketball GM — Exhibition Manager')
		# Start at a friendly size but allow resizing and fullscreen
		self.resize(480, 400)
		self.setStyleSheet('background-color: #232946; color: #fffffe;')

		font_title = QFont('Arial', 20, QFont.Bold)
		font_label = QFont('Arial', 12)
		font_button = QFont('Arial', 12, QFont.Bold)

		# Menu bar
		self.menu_bar = QMenuBar(self)

		# File menu (Exhibition controls and utilities)
		file_menu = QMenu('File', self)
		new_action = QAction('New Exhibition', self)
		new_action.setShortcut('Ctrl+N')
		new_action.triggered.connect(self.new_exhibition)
		random_action = QAction('Randomize Teams', self)
		random_action.setShortcut('Ctrl+R')
		random_action.triggered.connect(self.randomize_teams)
		swap_action = QAction('Swap Teams', self)
		swap_action.setShortcut('Ctrl+S')
		swap_action.triggered.connect(self.swap_teams)
		clear_action = QAction('Clear Results', self)
		clear_action.setShortcut('Ctrl+L')
		clear_action.triggered.connect(self.clear_results)
		save_action = QAction('Save Results as HTML…', self)
		save_action.setShortcut('Ctrl+Shift+S')
		save_action.triggered.connect(self.save_results_as_html)
		copy_action = QAction('Copy Results to Clipboard', self)
		copy_action.setShortcut('Ctrl+Alt+C')
		copy_action.triggered.connect(self.copy_results_to_clipboard)
		print_action = QAction('Print Results…', self)
		print_action.setShortcut('Ctrl+P')
		print_action.triggered.connect(self.print_results)
		back_action = QAction('Back to Main Menu', self)
		back_action.setShortcut('Ctrl+M')
		back_action.triggered.connect(self.back_to_main_menu)
		exit_action = QAction('Exit', self)
		exit_action.triggered.connect(self.close)

		for act in (new_action, random_action, swap_action, clear_action):
			file_menu.addAction(act)
		file_menu.addSeparator()
		for act in (save_action, copy_action, print_action):
			file_menu.addAction(act)
		file_menu.addSeparator()
		file_menu.addAction(back_action)
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

		# Teams menu removed per request



		help_menu = QMenu('Help', self)
		about_action = QAction('About', self)
		about_action.triggered.connect(self.show_about)
		help_menu.addAction(about_action)
		self.menu_bar.addMenu(help_menu)


		main_layout = QVBL()
		main_layout.setMenuBar(self.menu_bar)

		layout = QVBoxLayout()
		title = QLabel('🏀 Exhibition Manager')
		title.setFont(font_title)
		title.setAlignment(Qt.AlignCenter)
		layout.addWidget(title)

		team_layout = QHBoxLayout()

		def make_team_combo_and_label() -> tuple[QComboBox, QLabel]:
			combo = QComboBox()
			combo.setEditable(False)
			combo.setFont(font_label)
			combo.setStyleSheet('padding: 4px; border-radius: 8px; background: #eebbc3; color: #232946;')
			teams = [t.name for t in load_teams()]
			combo.addItems(teams)
			label = QLabel()
			label.setFont(font_label)
			label.setAlignment(Qt.AlignCenter)
			label.setStyleSheet('color: #eebbc3; background: transparent;')
			return combo, label

		self.team1_combo, self.team1_ovr_label = make_team_combo_and_label()
		self.team2_combo, self.team2_ovr_label = make_team_combo_and_label()
		team1_layout = QVBoxLayout()
		team1_layout.addWidget(self.team1_combo)
		team1_layout.addWidget(self.team1_ovr_label)
		team2_layout = QVBoxLayout()
		team2_layout.addWidget(self.team2_combo)
		team2_layout.addWidget(self.team2_ovr_label)
		team_layout.addLayout(team1_layout)
		team_layout.addLayout(team2_layout)
		layout.addLayout(team_layout)

		# --- Live Event Feed (UI retained but static) ---
		event_feed_layout = QHBoxLayout()
		self.event_feed = QListWidget()
		self.event_feed.setStyleSheet('background: #181b2a; color: #eebbc3; border-radius: 8px; padding: 6px;')
		self.event_feed.setMinimumHeight(120)
		self.event_feed.setMaximumHeight(180)
		event_feed_layout.addWidget(QLabel('Live Game Feed (disabled):'))
		event_feed_layout.addWidget(self.event_feed)
		layout.addLayout(event_feed_layout)

		# --- Simulation controls removed ---
		user_choice_layout = QHBoxLayout()
		layout.addLayout(user_choice_layout)

		def update_team1_ovr():
			team = self.team1_combo.currentText()
			ovr = load_team_overall(team)
			self.team1_ovr_label.setText(f"OVR: {ovr}" if ovr else "")

		def update_team2_ovr():
			team = self.team2_combo.currentText()
			ovr = load_team_overall(team)
			self.team2_ovr_label.setText(f"OVR: {ovr}" if ovr else "")

		self.team1_combo.currentIndexChanged.connect(update_team1_ovr)
		self.team2_combo.currentIndexChanged.connect(update_team2_ovr)
		update_team1_ovr()
		update_team2_ovr()

		# Back button under team selectors
		self.back_btn = QPushButton('Back to Main Menu')
		self.back_btn.setFont(font_button)
		self.back_btn.setStyleSheet('background: #393d63; color: #fffffe; padding: 10px; border-radius: 8px;')
		self.back_btn.clicked.connect(self.back_to_main_menu)
		layout.addWidget(self.back_btn)

		# Simulate button removed

		self.result_box = QTextEdit()
		self.result_box.setReadOnly(True)
		self.result_box.setFont(font_label)
		self.result_box.setStyleSheet('background: #121629; color: #fffffe; border-radius: 8px; padding: 10px;')
		layout.addWidget(self.result_box)

		main_layout.addLayout(layout)
		self.setLayout(main_layout)

	def new_exhibition(self):
		"""Reset team selections to the first two teams and clear results."""
		self.reload_teams()
		if self.team1_combo.count() > 0:
			self.team1_combo.setCurrentIndex(0)
		if self.team2_combo.count() > 1:
			self.team2_combo.setCurrentIndex(1)
		elif self.team2_combo.count() > 0:
			self.team2_combo.setCurrentIndex(0)
		self.clear_results()

	def randomize_teams(self):
		"""Pick two distinct random teams if available."""
		cnt = self.team1_combo.count()
		if cnt == 0:
			return
		if cnt == 1:
			self.team1_combo.setCurrentIndex(0)
			self.team2_combo.setCurrentIndex(0)
			return
		i1, i2 = random.sample(range(cnt), 2)
		self.team1_combo.setCurrentIndex(i1)
		self.team2_combo.setCurrentIndex(i2)

	def swap_teams(self):
		"""Swap the current team selections."""
		i1 = self.team1_combo.currentIndex()
		i2 = self.team2_combo.currentIndex()
		if i1 >= 0 and i2 >= 0:
			self.team1_combo.setCurrentIndex(i2)
			self.team2_combo.setCurrentIndex(i1)

	def clear_results(self):
		"""Clear the results pane."""
		self.result_box.clear()

	def _current_matchup_slug(self) -> str:
		"""Build a simple filename slug from current selections."""
		t1 = (self.team1_combo.currentText() or 'Team1').replace(' ', '_')
		t2 = (self.team2_combo.currentText() or 'Team2').replace(' ', '_')
		return f"{t1}_vs_{t2}"

	def save_results_as_html(self):
		"""Save the current results (HTML) to a file."""
		html = self.result_box.toHtml()
		if not html.strip():
			QMessageBox.information(self, 'Save Results', 'No results to save yet.')
			return
		default_name = f"boxscore_{self._current_matchup_slug()}.html"
		start_dir = os.path.expanduser('~')
		path, _ = QFileDialog.getSaveFileName(self, 'Save Results as HTML', os.path.join(start_dir, default_name), 'HTML Files (*.html);;All Files (*)')
		if not path:
			return
		try:
			with open(path, 'w', encoding='utf-8') as f:
				f.write(html)
			QMessageBox.information(self, 'Save Results', f'Saved to:\n{path}')
		except Exception as e:
			QMessageBox.critical(self, 'Save Results', f'Failed to save file:\n{e}')

	def copy_results_to_clipboard(self):
		"""Copy the results as plain text to the system clipboard."""
		text = self.result_box.toPlainText()
		if not text.strip():
			QMessageBox.information(self, 'Copy Results', 'No results to copy yet.')
			return
		QGuiApplication.clipboard().setText(text)
		QMessageBox.information(self, 'Copy Results', 'Results copied to clipboard.')

	def print_results(self):
		"""Open a print dialog to print the results pane."""
		if not (self.result_box.toPlainText().strip() or self.result_box.toHtml().strip()):
			QMessageBox.information(self, 'Print Results', 'No results to print yet.')
			return
		printer = QPrinter(QPrinter.HighResolution)
		dialog = QPrintDialog(printer, self)
		if dialog.exec_() == QPrintDialog.Accepted:
			self.result_box.print(printer)

	def reload_teams(self):
		"""Reload team list from core.teams and repopulate dropdowns and update OVR labels."""
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
		# Update OVR labels
		if hasattr(self, 'team1_ovr_label') and hasattr(self, 'team2_ovr_label'):
			team1 = self.team1_combo.currentText()
			team2 = self.team2_combo.currentText()
			from core.teams.team_overall import load_team_overall
			ovr1 = load_team_overall(team1)
			ovr2 = load_team_overall(team2)
			self.team1_ovr_label.setText(f"OVR: {ovr1}" if ovr1 else "")
			self.team2_ovr_label.setText(f"OVR: {ovr2}" if ovr2 else "")

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
		QMessageBox.information(self, 'About', 'Basketball GM — Exhibition Manager\nCreated with PyQt5')



	def back_to_main_menu(self):
		"""Close this window and return to the main menu."""
		# Local import to avoid circular dependency
		from .start_menu import MainMenuWindow
		self._main_menu = MainMenuWindow()
		self._main_menu.show()
		self.close()

	def keyPressEvent(self, event):
		"""Let ESC exit fullscreen; otherwise default behavior."""
		if event.key() == Qt.Key_Escape and self.isFullScreen():
			self.toggle_fullscreen()
			return
		super().keyPressEvent(event)

	def simulate_game(self):
		# Simulation removed: show info message
		QMessageBox.information(self, 'Simulation Removed', 'Game simulation has been removed from this build.')


	# User action handlers removed
