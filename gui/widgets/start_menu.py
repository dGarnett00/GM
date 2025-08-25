from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QMessageBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt
import os
import sys

"""
Main menu for the Basketball GM app.

Imports of heavy windows are intentionally done lazily inside methods to reduce
startup failures if optional modules have issues. This ensures the app launches
reliably and can surface errors gracefully.
"""


class MainMenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.sim_window = None
        self.rosters_window = None
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle('Basketball GM — Main Menu')
        self.resize(420, 300)
        self.setStyleSheet('background-color: #232946; color: #fffffe;')

        title_font = QFont('Arial', 22, QFont.Bold)
        btn_font = QFont('Arial', 12, QFont.Bold)
        sub_font = QFont('Arial', 10)

        layout = QVBoxLayout()
        layout.setSpacing(16)

        title = QLabel('🏀 Basketball GM')
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        subtitle = QLabel('Exhibition Manager')
        subtitle.setFont(sub_font)
        subtitle.setAlignment(Qt.AlignCenter)
        layout.addWidget(subtitle)

        start_btn = QPushButton('Exhibition')
        start_btn.setFont(btn_font)
        start_btn.setStyleSheet('background:#393d63;color:#fffffe;padding:10px;border-radius:8px;')
        start_btn.clicked.connect(self.start_game)
        layout.addWidget(start_btn)

        rosters_btn = QPushButton('Rosters')
        rosters_btn.setFont(btn_font)
        rosters_btn.setStyleSheet('background:#393d63;color:#fffffe;padding:10px;border-radius:8px;')
        rosters_btn.clicked.connect(self.open_rosters)
        layout.addWidget(rosters_btn)

        reload_btn = QPushButton('Reload')
        reload_btn.setFont(btn_font)
        reload_btn.setStyleSheet('background:#393d63;color:#fffffe;padding:10px;border-radius:8px;')
        reload_btn.clicked.connect(self.reload_app)
        layout.addWidget(reload_btn)

        exit_btn = QPushButton('Exit')
        exit_btn.setFont(btn_font)
        exit_btn.setStyleSheet('background:#eebbc3;color:#232946;padding:10px;border-radius:8px;')
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)

        layout.addStretch(1)
        self.setLayout(layout)

    def start_game(self):
        # Launch the simulator window and close the main menu
        try:
            if self.sim_window is None:
                from .main_window import BasketballSimulatorWindow  # lazy import
                self.sim_window = BasketballSimulatorWindow()
            self.sim_window.show()
            self.close()
        except Exception as e:
            QMessageBox.critical(self, 'Unable to open', f'Failed to open Exhibition window.\n\n{e}')

    def open_rosters(self):
        try:
            if self.rosters_window is None:
                from .rosters_window import RostersWindow  # lazy import
                self.rosters_window = RostersWindow()
            self.rosters_window.show()
        except Exception as e:
            QMessageBox.critical(self, 'Unable to open', f'Failed to open Rosters window.\n\n{e}')

    def reload_app(self):
        # Restart the Python process to fully reload the app
        python = sys.executable
        os.execl(python, python, *sys.argv)
