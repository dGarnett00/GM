from PyQt5.QtWidgets import QTextEdit
from PyQt5.QtGui import QFont


class ResultsPane(QTextEdit):
    """A read-only text pane for results, styled via QSS.

    Subclasses QTextEdit to maintain API compatibility with existing code.
    """

    def __init__(self, font: QFont | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName('ResultsPane')
        if font:
            self.setFont(font)
        self.setReadOnly(True)
