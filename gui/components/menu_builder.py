from PyQt5.QtWidgets import QMenuBar, QMenu
from PyQt5.QtGui import QKeySequence
from PyQt5.QtWidgets import QAction


class MenuBuilder:
    """Helper to build the menu bar for the Exhibition window."""

    def __init__(self, host):
        self.host = host

    def build(self) -> QMenuBar:
        bar = QMenuBar(self.host)
        bar.setObjectName('MainMenuBar')

        file_menu = QMenu('File', self.host)

        def add_action(menu, text, slot, shortcut=None, checkable=False):
            act = QAction(text, self.host)
            if shortcut:
                act.setShortcut(QKeySequence(shortcut))
            if checkable:
                act.setCheckable(True)
            act.triggered.connect(slot)
            menu.addAction(act)
            return act

        add_action(file_menu, 'New Exhibition', self.host.new_exhibition, 'Ctrl+N')
        add_action(file_menu, 'Randomize Teams', self.host.randomize_teams, 'Ctrl+R')
        add_action(file_menu, 'Swap Teams', self.host.swap_teams, 'Ctrl+S')
        add_action(file_menu, 'Clear Results', self.host.clear_results, 'Ctrl+L')
        file_menu.addSeparator()
        add_action(file_menu, 'Save Results as HTML…', self.host.save_results_as_html, 'Ctrl+Shift+S')
        add_action(file_menu, 'Copy Results to Clipboard', self.host.copy_results_to_clipboard, 'Ctrl+Alt+C')
        add_action(file_menu, 'Print Results…', self.host.print_results, 'Ctrl+P')
        file_menu.addSeparator()
        add_action(file_menu, 'Back to Main Menu', self.host.back_to_main_menu, 'Ctrl+M')
        add_action(file_menu, 'Exit', self.host.close)

        bar.addMenu(file_menu)

        view_menu = QMenu('View', self.host)
        self.host.fullscreen_action = add_action(view_menu, 'Toggle Full Screen', self.host.toggle_fullscreen, 'F11', checkable=True)
        bar.addMenu(view_menu)

        help_menu = QMenu('Help', self.host)
        add_action(help_menu, 'About', self.host.show_about)
        # Player ratings & skill legend
        def _open_skill_legend():
            try:
                from gui.widgets.skill_legend import SkillLegendDialog
                dlg = SkillLegendDialog(self.host)
                dlg.exec_()
            except Exception:
                # If import fails, fallback to About
                self.host.show_about()

        add_action(help_menu, 'Player Ratings & Skills', _open_skill_legend)
        bar.addMenu(help_menu)

        return bar
