from PyQt5.QtWidgets import (
	QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QVBoxLayout as QVBL, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QFont, QGuiApplication
from PyQt5.QtCore import Qt
from gui.components.team_selector import TeamSelector
from gui.components.results_pane import ResultsPane
from gui.components.menu_builder import MenuBuilder
from gui.components.play_by_play import PlayByPlayWidget
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
		self.setObjectName('BasketballSimulatorWindow')
		# Start at a friendly size but allow resizing and fullscreen
		self.resize(480, 400)
		# Styling now handled by QSS

		font_title = QFont('Arial', 20, QFont.Bold)
		font_label = QFont('Arial', 12)
		font_button = QFont('Arial', 12, QFont.Bold)

		# Menu bar via helper
		self.menu_bar = MenuBuilder(self).build()

		# Back button under team selectors
		self.back_btn = QPushButton('Back to Main Menu')
		self.back_btn.setObjectName('BackButton')
		self.back_btn.setFont(font_button)
		self.back_btn.clicked.connect(self.back_to_main_menu)

		# Layouts
		main_layout = QVBL()
		main_layout.setMenuBar(self.menu_bar)
		layout = QVBoxLayout()

		# Title
		title = QLabel('🏀 Exhibition Manager')
		title.setObjectName('TitleLabel')
		title.setFont(font_title)
		title.setAlignment(Qt.AlignCenter)
		layout.addWidget(title)

		# Team selectors
		team_layout = QHBoxLayout()
		self.team1_selector = TeamSelector(font_label)
		self.team2_selector = TeamSelector(font_label)
		left = QVBoxLayout()
		left.addWidget(self.team1_selector)
		right = QVBoxLayout()
		right.addWidget(self.team2_selector)
		team_layout.addLayout(left)
		team_layout.addLayout(right)
		layout.addLayout(team_layout)

		# Back button
		layout.addWidget(self.back_btn)

		# Results pane
		self.result_box = ResultsPane(font_label)
		# mark results as a card for QSS
		self.result_box.setObjectName('ResultsPane')

		# Play-by-play widget and controls
		self.play_by_play = PlayByPlayWidget()
		self.play_by_play.setObjectName('PlayByPlayWidget')
		self.load_pbp_btn = QPushButton('Load Play-by-Play HTML')
		self.load_pbp_btn.setObjectName('LoadPBPButton')
		self.load_pbp_btn.setFont(font_button)
		self.load_pbp_btn.clicked.connect(self._load_play_by_play_html)

		# Two-column area: results on the left, play-by-play on the right
		two_col = QHBoxLayout()
		left_col = QVBoxLayout()
		left_col.addWidget(self.result_box)
		left_col.addWidget(self.load_pbp_btn)
		# Allow left column to expand more than right
		two_col.addLayout(left_col, 3)
		two_col.addWidget(self.play_by_play, 2)
		layout.addLayout(two_col)

		main_layout.addLayout(layout)
		self.setLayout(main_layout)

	def new_exhibition(self):
		"""Reset team selections to the first two teams and clear results."""
		self.reload_teams()
		if self.team1_selector.combo.count() > 0:
			self.team1_selector.setCurrentIndex(0)
		if self.team2_selector.combo.count() > 1:
			self.team2_selector.setCurrentIndex(1)
		elif self.team2_selector.combo.count() > 0:
			self.team2_selector.setCurrentIndex(0)
		self.clear_results()

	def randomize_teams(self):
		"""Pick two distinct random teams if available."""
		cnt = self.team1_selector.combo.count()
		if cnt == 0:
			return
		if cnt == 1:
			self.team1_selector.setCurrentIndex(0)
			self.team2_selector.setCurrentIndex(0)
			return
		i1, i2 = random.sample(range(cnt), 2)
		self.team1_selector.setCurrentIndex(i1)
		self.team2_selector.setCurrentIndex(i2)

	def swap_teams(self):
		"""Swap the current team selections."""
		i1 = self.team1_selector.combo.currentIndex()
		i2 = self.team2_selector.combo.currentIndex()
		if i1 >= 0 and i2 >= 0:
			self.team1_selector.setCurrentIndex(i2)
			self.team2_selector.setCurrentIndex(i1)

	def clear_results(self):
		"""Clear the results pane."""
		self.result_box.clear()

	def _current_matchup_slug(self) -> str:
		"""Build a simple filename slug from current selections."""
		t1 = (self.team1_selector.currentTeam() or 'Team1').replace(' ', '_')
		t2 = (self.team2_selector.currentTeam() or 'Team2').replace(' ', '_')
		return f"{t1}_vs_{t2}"

	def save_results_as_html(self):
		"""Save the current results (HTML) to a file."""
		html = self.result_box.toHtml()
		if not html.strip():
			QMessageBox.information(self, 'Save Results', 'No results to save yet.')
			return
		default_name = f"results_{self._current_matchup_slug()}.html"
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
		self.team1_selector.reload()
		self.team2_selector.reload()

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


	def _load_play_by_play_html(self):
		from PyQt5.QtWidgets import QFileDialog, QMessageBox
		start_dir = os.path.expanduser('~')
		path, _ = QFileDialog.getOpenFileName(self, 'Load Play-by-Play HTML', start_dir, 'HTML Files (*.html *.htm);;All Files (*)')
		if not path:
			return
		try:
			with open(path, 'r', encoding='utf-8') as f:
				html = f.read()
			self.play_by_play.load_html(html)
			QMessageBox.information(self, 'Play-by-Play', f'Loaded play-by-play from:\n{path}')
		except Exception as e:
			QMessageBox.critical(self, 'Play-by-Play', f'Failed to load file:\n{e}')



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


	# User action handlers removed
