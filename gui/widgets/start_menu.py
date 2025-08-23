from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton
from PyQt5.QtCore import Qt
import os
import sys
import logging

from .main_window import BasketballSimulatorWindow
from .rosters_window import RostersWindow
from ..styles import AppStyles, AppFonts, UIConstants
from ..error_handling import ErrorHandler, safe_execute_method


class MainMenuWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.sim_window = None
        self.rosters_window = None
        self.logger = logging.getLogger('basketball_gm')
        self._init_ui()

    @safe_execute_method("initializing main menu UI")
    def _init_ui(self):
        self.setWindowTitle('Basketball GM — Main Menu')
        self.resize(*UIConstants.MAIN_MENU_SIZE)
        self.setStyleSheet(AppStyles.WINDOW_STYLE)

        layout = QVBoxLayout()
        layout.setSpacing(UIConstants.LAYOUT_SPACING)

        # Title
        title = QLabel('🏀 Basketball GM')
        title.setFont(AppFonts.title_font(22))
        title.setAlignment(UIConstants.CENTER)
        layout.addWidget(title)

        # Subtitle
        subtitle = QLabel('Exhibition Game Simulator')
        subtitle.setFont(AppFonts.subtitle_font())
        subtitle.setAlignment(UIConstants.CENTER)
        layout.addWidget(subtitle)

        # Exhibition button
        start_btn = QPushButton('Exhibition')
        start_btn.setFont(AppFonts.button_font())
        start_btn.setStyleSheet(AppStyles.BUTTON_PRIMARY)
        start_btn.clicked.connect(self.start_game)
        layout.addWidget(start_btn)

        # Rosters button
        rosters_btn = QPushButton('Rosters')
        rosters_btn.setFont(AppFonts.button_font())
        rosters_btn.setStyleSheet(AppStyles.BUTTON_PRIMARY)
        rosters_btn.clicked.connect(self.open_rosters)
        layout.addWidget(rosters_btn)

        # Reload button
        reload_btn = QPushButton('Reload')
        reload_btn.setFont(AppFonts.button_font())
        reload_btn.setStyleSheet(AppStyles.BUTTON_PRIMARY)
        reload_btn.clicked.connect(self.reload_app)
        layout.addWidget(reload_btn)

        # Exit button
        exit_btn = QPushButton('Exit')
        exit_btn.setFont(AppFonts.button_font())
        exit_btn.setStyleSheet(AppStyles.BUTTON_SECONDARY)
        exit_btn.clicked.connect(self.close)
        layout.addWidget(exit_btn)

        layout.addStretch(1)
        self.setLayout(layout)

    @safe_execute_method("starting game")
    def start_game(self):
        """Launch the simulator window and close the main menu."""
        try:
            if self.sim_window is None:
                self.sim_window = BasketballSimulatorWindow()
            self.sim_window.show()
            self.close()
            self.logger.info("Exhibition window opened successfully")
        except Exception as e:
            ErrorHandler.handle_exception(self, "opening exhibition window", e)

    @safe_execute_method("opening rosters window")
    def open_rosters(self):
        """Open the rosters window."""
        try:
            if self.rosters_window is None:
                self.rosters_window = RostersWindow()
            self.rosters_window.show()
            self.logger.info("Rosters window opened successfully")
        except Exception as e:
            ErrorHandler.handle_exception(self, "opening rosters window", e)

    @safe_execute_method("reloading application")
    def reload_app(self):
        """Restart the Python process to fully reload the app."""
        try:
            self.logger.info("Reloading application")
            python = sys.executable
            os.execl(python, python, *sys.argv)
        except Exception as e:
            ErrorHandler.handle_exception(self, "reloading the application", e)
