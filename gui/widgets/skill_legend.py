from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLabel, QTextBrowser, QHBoxLayout
from PyQt5.QtGui import QFont
from gui.components.skill_badge import get_badge_pixmap


class SkillLegendDialog(QDialog):
  """Dialog showing rating scale and a legend of skill symbols with icons."""

  def __init__(self, parent=None):
    super().__init__(parent)
    self.setWindowTitle('Player Ratings & Skill Symbols')
    self.resize(480, 380)

    layout = QVBoxLayout()

    title = QLabel('<b>Player Ratings (0-100)</b>')
    title.setFont(QFont('Arial', 14, QFont.Bold))
    layout.addWidget(title)

    scale = QTextBrowser()
    scale.setReadOnly(True)
    scale.setOpenExternalLinks(False)
    scale.setHtml(
      """
      <p>Player ratings are on a 0-100 scale; typical values are around 50.</p>
      <ul>
        <li><b>85+</b>: All-time great</li>
        <li><b>75+</b>: MVP candidate</li>
        <li><b>65+</b>: All League candidate</li>
        <li><b>55+</b>: Starter</li>
        <li><b>45+</b>: Role player</li>
        <li><b>&lt;45</b>: Below role player</li>
      </ul>
      """
    )
    layout.addWidget(scale)

    items = [
      ('3', 'Three Point Shooter'),
      ('A', 'Athlete'),
      ('B', 'Ball Handler'),
      ('Di', 'Interior Defender'),
      ('Dp', 'Perimeter Defender'),
      ('Po', 'Post Scorer'),
      ('Ps', 'Passer'),
      ('R', 'Rebounder'),
      ('V', 'Volume Scorer'),
    ]

    for sym, desc in items:
      h = QHBoxLayout()
      lbl_icon = QLabel()
      pix = get_badge_pixmap(sym, size=22)
      lbl_icon.setPixmap(pix)
      lbl_icon.setFixedSize(24, 24)
      lbl_icon.setToolTip(desc)
      lbl_text = QLabel(f"<b>{sym}</b> — {desc}")
      h.addWidget(lbl_icon)
      h.addWidget(lbl_text)
      layout.addLayout(h)

    layout.addStretch(1)
    self.setLayout(layout)
