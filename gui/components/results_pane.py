from PyQt5.QtWidgets import QTextEdit, QFrame, QVBoxLayout
from PyQt5.QtGui import QFont


class ResultsPane(QFrame):
    """A read-only card wrapper around QTextEdit so QSS can style the card.

    This preserves the public API by exposing the internal QTextEdit via
    standard QTextEdit methods on the wrapped widget.
    """

    def __init__(self, font: QFont | None = None, parent=None):
        super().__init__(parent)
        self.setObjectName('ResultsPane')
        self.inner = QTextEdit(self)
        if font:
            self.inner.setFont(font)
        self.inner.setReadOnly(True)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.inner)
        self.setLayout(layout)

    # Proxy commonly used methods
    def toHtml(self):
        return self.inner.toHtml()

    def toPlainText(self):
        return self.inner.toPlainText()

    def clear(self):
        return self.inner.clear()

    def print(self, printer):
        return self.inner.print(printer)
