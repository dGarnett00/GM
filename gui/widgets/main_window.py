from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTextEdit, 
    QMenuBar, QMenu, QAction, QVBoxLayout as QVBL, QComboBox, QFileDialog, QMessageBox
)
from PyQt5.QtGui import QGuiApplication
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrinter, QPrintDialog
import os
import random
import logging

from core import simulate_game, generate_summary, generate_boxscore
from core.teams import load_teams
from ..styles import AppStyles, AppFonts, UIConstants
from ..error_handling import ErrorHandler, safe_execute_method, InputValidator, ValidationError


class BasketballSimulatorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self._main_menu = None
        self.logger = logging.getLogger('basketball_gm')
        self.init_ui()

    @safe_execute_method("initializing simulator window UI")
    def init_ui(self):
        self.setWindowTitle('Exhibition Basketball Game Simulator')
        self.resize(*UIConstants.SIMULATOR_SIZE)
        self.setStyleSheet(AppStyles.WINDOW_STYLE)

        # Menu bar
        self.menu_bar = QMenuBar(self)
        self._create_menus()

        main_layout = QVBL()
        main_layout.setMenuBar(self.menu_bar)

        layout = QVBoxLayout()
        
        # Title
        title = QLabel('🏀 Basketball Game Simulator')
        title.setFont(AppFonts.title_font())
        title.setAlignment(UIConstants.CENTER)
        layout.addWidget(title)

        # Team selection
        team_layout = QHBoxLayout()
        self.team1_combo = self._create_team_combo()
        self.team2_combo = self._create_team_combo()
        team_layout.addWidget(self.team1_combo)
        team_layout.addWidget(self.team2_combo)
        layout.addLayout(team_layout)

        # Back button
        self.back_btn = QPushButton('Back to Main Menu')
        self.back_btn.setFont(AppFonts.button_font())
        self.back_btn.setStyleSheet(AppStyles.BUTTON_PRIMARY)
        self.back_btn.clicked.connect(self.back_to_main_menu)
        layout.addWidget(self.back_btn)

        # Simulate button
        self.simulate_btn = QPushButton('Simulate Game')
        self.simulate_btn.setFont(AppFonts.button_font())
        self.simulate_btn.setStyleSheet(AppStyles.BUTTON_PRIMARY)
        self.simulate_btn.clicked.connect(self.simulate_game)
        layout.addWidget(self.simulate_btn)

        # Results area
        self.result_box = QTextEdit()
        self.result_box.setReadOnly(True)
        self.result_box.setFont(AppFonts.label_font())
        self.result_box.setStyleSheet(AppStyles.TEXT_AREA_STYLE)
        layout.addWidget(self.result_box)

        main_layout.addLayout(layout)
        self.setLayout(main_layout)

    @safe_execute_method("creating menus")
    def _create_menus(self):
        """Create the application menu bar with error handling."""
        # File menu
        file_menu = QMenu('File', self)
        
        # Game actions
        new_action = self._create_action('New Exhibition', 'Ctrl+N', self.new_exhibition)
        random_action = self._create_action('Randomize Teams', 'Ctrl+R', self.randomize_teams)
        swap_action = self._create_action('Swap Teams', 'Ctrl+S', self.swap_teams)
        clear_action = self._create_action('Clear Results', 'Ctrl+L', self.clear_results)
        
        # Output actions
        save_action = self._create_action('Save Results as HTML…', 'Ctrl+Shift+S', self.save_results_as_html)
        copy_action = self._create_action('Copy Results to Clipboard', 'Ctrl+Alt+C', self.copy_results_to_clipboard)
        print_action = self._create_action('Print Results…', 'Ctrl+P', self.print_results)
        
        # Navigation actions
        back_action = self._create_action('Back to Main Menu', 'Ctrl+M', self.back_to_main_menu)
        exit_action = self._create_action('Exit', None, self.close)

        # Add actions to menu
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
        self.fullscreen_action = self._create_action('Toggle Full Screen', 'F11', self.toggle_fullscreen)
        self.fullscreen_action.setCheckable(True)
        view_menu.addAction(self.fullscreen_action)
        self.menu_bar.addMenu(view_menu)

        # Help menu
        help_menu = QMenu('Help', self)
        about_action = self._create_action('About', None, self.show_about)
        help_menu.addAction(about_action)
        self.menu_bar.addMenu(help_menu)

    def _create_action(self, text: str, shortcut: str, slot) -> QAction:
        """Helper to create menu actions with error handling."""
        action = QAction(text, self)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(slot)
        return action

    @safe_execute_method("creating team combo box")
    def _create_team_combo(self) -> QComboBox:
        """Create a team selection combo box with error handling."""
        combo = QComboBox()
        combo.setEditable(False)
        combo.setFont(AppFonts.label_font())
        combo.setStyleSheet(AppStyles.COMBO_STYLE)
        
        try:
            teams = load_teams()
            team_names = [t.name for t in teams]
            if not team_names:
                team_names = ["No teams available"]
                self.logger.warning("No teams loaded for game selection")
            
            combo.addItems(team_names)
            
        except Exception as e:
            ErrorHandler.handle_exception(self, "loading teams for game selection", e)
            combo.addItems(["Error loading teams"])
        
        return combo

    @safe_execute_method("starting new exhibition")
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
        self.logger.info("Started new exhibition")

    @safe_execute_method("randomizing teams")
    def randomize_teams(self):
        """Pick two distinct random teams if available."""
        cnt = self.team1_combo.count()
        if cnt == 0:
            ErrorHandler.show_warning(self, "No Teams", "No teams available for randomization.")
            return
        if cnt == 1:
            self.team1_combo.setCurrentIndex(0)
            self.team2_combo.setCurrentIndex(0)
            ErrorHandler.show_info(self, "Single Team", "Only one team available.")
            return
        
        i1, i2 = random.sample(range(cnt), 2)
        self.team1_combo.setCurrentIndex(i1)
        self.team2_combo.setCurrentIndex(i2)
        self.logger.info(f"Randomized teams: {self.team1_combo.currentText()} vs {self.team2_combo.currentText()}")

    @safe_execute_method("swapping teams")
    def swap_teams(self):
        """Swap the current team selections."""
        i1 = self.team1_combo.currentIndex()
        i2 = self.team2_combo.currentIndex()
        if i1 >= 0 and i2 >= 0:
            self.team1_combo.setCurrentIndex(i2)
            self.team2_combo.setCurrentIndex(i1)
            self.logger.info("Swapped team selections")

    @safe_execute_method("clearing results")
    def clear_results(self):
        """Clear the results pane."""
        self.result_box.clear()
        self.logger.info("Cleared results")

    def _current_matchup_slug(self) -> str:
        """Build a simple filename slug from current selections."""
        t1 = (self.team1_combo.currentText() or 'Team1').replace(' ', '_')
        t2 = (self.team2_combo.currentText() or 'Team2').replace(' ', '_')
        return f"{t1}_vs_{t2}"

    @safe_execute_method("saving results as HTML")
    def save_results_as_html(self):
        """Save the current results (HTML) to a file."""
        html = self.result_box.toHtml()
        if not html.strip():
            ErrorHandler.show_info(self, 'Save Results', 'No results to save yet.')
            return
        
        default_name = f"boxscore_{self._current_matchup_slug()}.html"
        start_dir = os.path.expanduser('~')
        path, _ = QFileDialog.getSaveFileName(
            self, 'Save Results as HTML', 
            os.path.join(start_dir, default_name), 
            'HTML Files (*.html);;All Files (*)'
        )
        
        if not path:
            return
        
        try:
            with open(path, 'w', encoding='utf-8') as f:
                f.write(html)
            ErrorHandler.show_info(self, 'Save Results', f'Saved to:\n{path}')
            self.logger.info(f"Saved results to {path}")
        except Exception as e:
            ErrorHandler.handle_exception(self, "saving results file", e)

    @safe_execute_method("copying results to clipboard")
    def copy_results_to_clipboard(self):
        """Copy the results as plain text to the system clipboard."""
        text = self.result_box.toPlainText()
        if not text.strip():
            ErrorHandler.show_info(self, 'Copy Results', 'No results to copy yet.')
            return
        
        try:
            QGuiApplication.clipboard().setText(text)
            ErrorHandler.show_info(self, 'Copy Results', 'Results copied to clipboard.')
            self.logger.info("Copied results to clipboard")
        except Exception as e:
            ErrorHandler.handle_exception(self, "copying to clipboard", e)

    @safe_execute_method("printing results")
    def print_results(self):
        """Open a print dialog to print the results pane."""
        if not (self.result_box.toPlainText().strip() or self.result_box.toHtml().strip()):
            ErrorHandler.show_info(self, 'Print Results', 'No results to print yet.')
            return
        
        try:
            printer = QPrinter(QPrinter.HighResolution)
            dialog = QPrintDialog(printer, self)
            if dialog.exec_() == QPrintDialog.Accepted:
                self.result_box.print(printer)
                self.logger.info("Printed results")
        except Exception as e:
            ErrorHandler.handle_exception(self, "printing results", e)

    @safe_execute_method("reloading teams")
    def reload_teams(self):
        """Reload team list from core.teams and repopulate dropdowns."""
        try:
            teams = load_teams()
            team_names = [t.name for t in teams]
            
            if not team_names:
                team_names = ["No teams available"]
                ErrorHandler.show_warning(self, "Teams", "No teams could be loaded.")
            
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
            self.logger.info(f"Reloaded {len(team_names)} teams")
            
        except Exception as e:
            ErrorHandler.handle_exception(self, "reloading teams", e)

    @safe_execute_method("toggling fullscreen")
    def toggle_fullscreen(self, checked=False):
        """Toggle between fullscreen and normal window."""
        try:
            if self.isFullScreen():
                self.showNormal()
                self.fullscreen_action.setChecked(False)
                self.logger.info("Exited fullscreen mode")
            else:
                self.showFullScreen()
                self.fullscreen_action.setChecked(True)
                self.logger.info("Entered fullscreen mode")
        except Exception as e:
            ErrorHandler.handle_exception(self, "toggling fullscreen", e)

    @safe_execute_method("showing about dialog")
    def show_about(self):
        """Show the about dialog."""
        ErrorHandler.show_info(self, 'About', 'Basketball GM Simulator\nCreated with PyQt5')

    @safe_execute_method("returning to main menu")
    def back_to_main_menu(self):
        """Close this window and return to the main menu."""
        try:
            # Local import to avoid circular dependency
            from .start_menu import MainMenuWindow
            self._main_menu = MainMenuWindow()
            self._main_menu.show()
            self.close()
            self.logger.info("Returned to main menu")
        except Exception as e:
            ErrorHandler.handle_exception(self, "returning to main menu", e)

    def keyPressEvent(self, event):
        """Let ESC exit fullscreen; otherwise default behavior."""
        try:
            if event.key() == Qt.Key_Escape and self.isFullScreen():
                self.toggle_fullscreen()
                return
            super().keyPressEvent(event)
        except Exception as e:
            self.logger.error(f"Error in key press event: {e}")

    @safe_execute_method("simulating game")
    def simulate_game(self):
        """Simulate a game between the selected teams."""
        # Validate selections
        try:
            # Ensure we always use a valid selection from the predefined list
            if self.team1_combo.currentIndex() < 0 and self.team1_combo.count() > 0:
                self.team1_combo.setCurrentIndex(0)
            if self.team2_combo.currentIndex() < 0 and self.team2_combo.count() > 0:
                self.team2_combo.setCurrentIndex(0)
            
            team1 = self.team1_combo.currentText()
            team2 = self.team2_combo.currentText()
            
            # Validate team selections
            InputValidator.validate_team_selection(team1, team2)
            
            # Check for error states
            if team1 in ["No teams available", "Error loading teams"] or \
               team2 in ["No teams available", "Error loading teams"]:
                ErrorHandler.show_error(self, "Invalid Teams", 
                                      "Cannot simulate game with invalid team selections. "
                                      "Please reload teams or restart the application.")
                return
            
            self.logger.info(f"Starting simulation: {team1} vs {team2}")
            
            # Run simulation
            t1, t2, score1, score2, winner = simulate_game(team1, team2)
            summary = generate_summary(t1, t2, score1, score2, winner)
            box = generate_boxscore(t1, t2, score1, score2)
            
            self.result_box.setHtml(summary + "<br>" + box)
            self.logger.info(f"Simulation completed: {t1} {score1} - {score2} {t2}, Winner: {winner}")
            
        except ValidationError as e:
            ErrorHandler.show_error(self, "Invalid Selection", str(e))
        except Exception as e:
            ErrorHandler.handle_exception(self, "simulating the game", e)
