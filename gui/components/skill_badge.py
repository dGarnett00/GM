from PyQt5.QtGui import QPixmap, QPainter, QColor, QFont, QPen
from PyQt5.QtCore import Qt
import os

# Cache for generated and loaded pixmaps
_PIXMAP_CACHE: dict[str, QPixmap] = {}

# Path to bundled SVG icons
_ICONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'resources', 'skill_icons')


def _color_for_symbol(sym: str) -> QColor:
    colors = {
        '3': QColor('#2b8cff'),
        'A': QColor('#28c76f'),
        'B': QColor('#ff9f43'),
        'Di': QColor('#ff6b6b'),
        'Dp': QColor('#845ef7'),
        'Po': QColor('#ff6bd6'),
        'Ps': QColor('#00c2ff'),
        'R': QColor('#f6c85f'),
        'V': QColor('#ff5252'),
    }
    return colors.get(sym, QColor('#888'))


def make_badge_pixmap(sym: str, size: int = 20) -> QPixmap:
    """Return a QPixmap with the symbol rendered inside a rounded badge."""
    pix = QPixmap(size, size)
    pix.fill(Qt.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.Antialiasing)

    bg = _color_for_symbol(sym)
    pen = QPen(Qt.transparent)
    p.setPen(pen)
    p.setBrush(bg)
    radius = 4
    p.drawRoundedRect(0, 0, size, size, radius, radius)

    # Draw symbol text
    f = QFont('Arial', max(8, int(size * 0.55)))
    f.setBold(True)
    p.setFont(f)
    p.setPen(QColor('#ffffff'))
    metrics = p.fontMetrics()
    text_w = metrics.horizontalAdvance(sym)
    text_h = metrics.ascent()
    x = (size - text_w) / 2
    y = (size + text_h) / 2 - 1
    p.drawText(int(x), int(y), sym)
    p.end()
    return pix


def _load_icon_svg(sym: str, size: int = 20) -> QPixmap:
    """Try to load an SVG icon asset for the symbol and return a QPixmap sized appropriately."""
    key = f"svg:{sym}:{size}"
    if key in _PIXMAP_CACHE:
        return _PIXMAP_CACHE[key]
    svg_path = os.path.join(_ICONS_DIR, f"{sym}.svg")
    pix = QPixmap()
    try:
        if os.path.exists(svg_path):
            # QPixmap can load SVG on many platforms; rely on Qt's support here
            pix.load(svg_path)
            if not pix.isNull() and (pix.width() != size or pix.height() != size):
                pix = pix.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    except Exception:
        pass
    _PIXMAP_CACHE[key] = pix
    return pix


def get_badge_pixmap(sym: str, size: int = 20) -> QPixmap:
    """Get a pixmap for a symbol, preferring SVG asset then falling back to painter-generated."""
    key = f"badge:{sym}:{size}"
    if key in _PIXMAP_CACHE:
        return _PIXMAP_CACHE[key]
    pix = _load_icon_svg(sym, size)
    if pix.isNull():
        pix = make_badge_pixmap(sym, size)
    _PIXMAP_CACHE[key] = pix
    return pix


def make_combined_badge(symbols: list[str], size: int = 18, spacing: int = 2) -> QPixmap:
    """Return a combined horizontal pixmap of multiple badges."""
    if not symbols:
        return QPixmap()
    parts = [get_badge_pixmap(s, size=size) for s in symbols]
    width = len(parts) * size + max(0, len(parts) - 1) * spacing
    height = size
    pix = QPixmap(width, height)
    pix.fill(Qt.transparent)
    painter = QPainter(pix)
    painter.setRenderHint(QPainter.Antialiasing)
    x = 0
    for p in parts:
        painter.drawPixmap(int(x), 0, p)
        x += size + spacing
    painter.end()
    return pix


# Cache for combined pixmaps keyed by (symbols,size,spacing)
_COMBINED_CACHE: dict[str, QPixmap] = {}


def get_combined_badge(symbols: list[str], size: int = 18, spacing: int = 2) -> QPixmap:
    if not symbols:
        return QPixmap()
    key = f"comb:{','.join(symbols)}:{size}:{spacing}"
    if key in _COMBINED_CACHE:
        return _COMBINED_CACHE[key]
    pix = make_combined_badge(symbols, size=size, spacing=spacing)
    _COMBINED_CACHE[key] = pix
    return pix
