from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit
from PyQt5.QtCore import Qt
import logging

from core.teams import load_teams, get_team_roster
from ..styles import AppStyles, AppFonts, UIConstants
from ..error_handling import ErrorHandler, safe_execute_method


class RostersWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.logger = logging.getLogger('basketball_gm')
        self._init_ui()

    @safe_execute_method("initializing rosters window UI")
    def _init_ui(self):
        self.setWindowTitle('Team Rosters')
        self.resize(*UIConstants.ROSTERS_SIZE)
        self.setStyleSheet(AppStyles.WINDOW_STYLE)

        layout = QVBoxLayout()

        # Title
        title = QLabel('Team Rosters')
        title.setFont(AppFonts.title_font(18))
        title.setAlignment(UIConstants.CENTER)
        layout.addWidget(title)

        # Team selector
        self.team_combo = QComboBox()
        self.team_combo.setStyleSheet(AppStyles.COMBO_STYLE)
        self.team_combo.setFont(AppFonts.label_font(11))
        
        # Load teams with error handling
        try:
            teams = load_teams()
            team_names = [t.name for t in teams]
            if not team_names:
                team_names = ["No teams available"]
                self.logger.warning("No teams loaded for roster display")
            
            self.team_combo.addItems(team_names)
            self.team_combo.currentIndexChanged.connect(self._update_roster)
            
        except Exception as e:
            ErrorHandler.handle_exception(self, "loading teams for roster display", e)
            self.team_combo.addItems(["Error loading teams"])
        
        layout.addWidget(self.team_combo)

        # Roster display
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setFont(AppFonts.label_font(11))
        self.text.setStyleSheet(AppStyles.TEXT_AREA_STYLE)
        layout.addWidget(self.text)

        self.setLayout(layout)
        self._update_roster()

    @safe_execute_method("updating roster display")
    def _update_roster(self):
        """Update the roster display for the selected team."""
        team = self.team_combo.currentText()
        
        if not team or team in ["No teams available", "Error loading teams"]:
            self.text.setPlainText('No team selected or teams unavailable.')
            return
        
        try:
            roster = get_team_roster(team)
            
            if not roster:
                self.text.setPlainText(f'No roster found for {team}.\n\nA roster will be generated automatically during games.')
                self.logger.info(f"No roster data found for team: {team}")
            else:
                # Format the roster nicely
                formatted_roster = f"Roster for {team}:\n\n"
                
                # Show starters first (first 5 players)
                if len(roster) >= 5:
                    formatted_roster += "Starters:\n"
                    for i, player in enumerate(roster[:5], 1):
                        formatted_roster += f"{i:2d}. {player}\n"
                    
                    if len(roster) > 5:
                        formatted_roster += "\nBench:\n"
                        for i, player in enumerate(roster[5:], 6):
                            formatted_roster += f"{i:2d}. {player}\n"
                else:
                    # Less than 5 players, just list them
                    for i, player in enumerate(roster, 1):
                        formatted_roster += f"{i:2d}. {player}\n"
                
                formatted_roster += f"\nTotal Players: {len(roster)}"
                
                self.text.setPlainText(formatted_roster)
                self.logger.info(f"Displayed roster for {team} ({len(roster)} players)")
                
        except Exception as e:
            ErrorHandler.handle_exception(self, f"loading roster for {team}", e)
            self.text.setPlainText(f'Error loading roster for {team}.\n\nPlease try again or check the logs for details.')
