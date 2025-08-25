from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSlider, QTextBrowser
)
from PyQt5.QtCore import QTimer, Qt

# Try to import QWebEngineView for high-fidelity HTML rendering. If the
# environment doesn't have PyQtWebEngine installed, we'll fall back to
# QTextBrowser and display a small warning.
try:
    from PyQt5.QtWebEngineWidgets import QWebEngineView  # type: ignore
except Exception:
    QWebEngineView = None  # type: ignore


class PlayByPlayWidget(QWidget):
    """A lightweight play-by-play pane with simple playback controls.

    Uses QTextBrowser to render HTML fragments. Plays can be loaded from an
    HTML file (li, p, or div blocks) or appended programmatically.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName('PlayByPlayWidget')

        self._displayed = []
        self.plays = []
        self.index = 0
        self.playing = False

        # Controls
        controls = QHBoxLayout()
        # mark controls for styling
        self.play_btn = QPushButton('Play')
        self.play_btn.setObjectName('PBPPlay')
        self.next_btn = QPushButton('Next')
        self.next_btn.setObjectName('PBPNext')
        self.speed_label = QLabel('1.00x')
        self.speed_label.setObjectName('PBPSpdLbl')
        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(10, 300)  # percent (0.1x - 3.0x)
        self.speed_slider.setValue(100)

        controls.addWidget(self.play_btn)
        controls.addWidget(self.next_btn)
        controls.addWidget(self.speed_label)
        controls.addWidget(self.speed_slider)

        # Browser area - prefer QWebEngineView when available for full CSS/JS
        if QWebEngineView is not None:
            self.browser = QWebEngineView()
            # QWebEngineView doesn't have setOpenExternalLinks; links open in engine
        else:
            self.browser = QTextBrowser()
            self.browser.setOpenExternalLinks(True)
            self.browser.setObjectName('PlayByPlayBrowser')

        # Layout
        root = QVBoxLayout()
        root.addLayout(controls)
        root.addWidget(self.browser)
        self.setLayout(root)

        # Timer for auto-play
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._play_step)

        # Signals
        self.play_btn.clicked.connect(self.toggle_play)
        self.next_btn.clicked.connect(self.next_play)
        self.speed_slider.valueChanged.connect(self._update_speed_label)

        self._update_speed_label()

    def load_html(self, html: str):
        """Load full HTML into the browser and parse plays for playback."""
        # Show full HTML as-is in the browser
        try:
            if QWebEngineView is not None and isinstance(self.browser, QWebEngineView):
                # QWebEngineView uses setHtml with a baseUrl optional arg; use simple form
                self.browser.setHtml(html)
            else:
                self.browser.setHtml(html)
        except Exception:
            # Fallback for QTextBrowser
            try:
                self.browser.setPlainText(html)
            except Exception:
                # As a last resort, leave silently
                pass

        # Parse possible play entries for stepwise playback
        self._parse_plays_from_html(html)
        self.index = 0
        self._displayed = []
        self._render_display()

    def append_line(self, html_line: str):
        """Append a single play (HTML fragment) to the internal play list."""
        self.plays.append(html_line)

    def _parse_plays_from_html(self, html: str):
        import re

        # Try common containers in order: <li>, <div class="play">, <p>
        plays = re.findall(r'<li[^>]*>(.*?)</li>', html, flags=re.DOTALL | re.IGNORECASE)
        if plays:
            self.plays = [p.strip() for p in plays]
            return

        plays = re.findall(r'<div[^>]*class=["\']?play[^"\']*["\']?[^>]*>(.*?)</div>', html, flags=re.DOTALL | re.IGNORECASE)
        if plays:
            self.plays = [p.strip() for p in plays]
            return

        plays = re.findall(r'<p[^>]*>(.*?)</p>', html, flags=re.DOTALL | re.IGNORECASE)
        if plays:
            self.plays = [p.strip() for p in plays]
            return

        # Last resort: split on newlines and keep non-empty lines
        lines = [ln.strip() for ln in html.splitlines() if ln.strip()]
        self.plays = lines

    def _update_speed_label(self):
        val = self.speed_slider.value()
        speed = val / 100.0
        self.speed_label.setText(f'{speed:.2f}x')
        if self.playing:
            self._start_timer()

    def _start_timer(self):
        speed = max(0.01, self.speed_slider.value() / 100.0)
        # base interval 1000ms per play at 1x
        interval = int(1000 / speed)
        interval = max(50, interval)
        self.timer.start(interval)

    def toggle_play(self):
        if self.playing:
            self.timer.stop()
            self.play_btn.setText('Play')
            self.playing = False
        else:
            self.playing = True
            self.play_btn.setText('Pause')
            self._start_timer()

    def _play_step(self):
        if self.index >= len(self.plays):
            self.timer.stop()
            self.play_btn.setText('Play')
            self.playing = False
            return
        item = self.plays[self.index]
        self._displayed.append(item)
        self.index += 1
        self._render_display()

    def next_play(self):
        # If auto-playing, stop first
        if self.playing:
            self.toggle_play()
        self._play_step()

    def _build_html(self):
        # Simple scaffold for displayed entries
        body = '\n'.join(f"<div class='pbp-entry'>{entry}</div>" for entry in self._displayed)
        return f"<html><head></head><body>{body}</body></html>"

    def _render_display(self):
        html = self._build_html()
        # QWebEngineView requires a different call path
        try:
            if QWebEngineView is not None and isinstance(self.browser, QWebEngineView):
                self.browser.setHtml(html)
            else:
                self.browser.setHtml(html)
        except Exception:
            try:
                self.browser.setPlainText(html)
            except Exception:
                pass

