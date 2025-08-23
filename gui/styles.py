"""Centralized styling constants and utilities for the Basketball GM GUI."""

from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt


class AppStyles:
    """Centralized styling constants for consistent UI design."""
    
    # Color palette
    BACKGROUND_PRIMARY = '#232946'  # Main background
    BACKGROUND_SECONDARY = '#121629'  # Text areas, input fields
    BACKGROUND_ACCENT = '#393d63'  # Buttons, menu items  
    BACKGROUND_HIGHLIGHT = '#2b2f55'  # Headers, selected items
    
    TEXT_PRIMARY = '#fffffe'  # Main text
    TEXT_ACCENT = '#eebbc3'  # Highlight text, links
    TEXT_BUTTON = '#232946'  # Button text on light backgrounds
    
    BORDER_COLOR = '#393d63'
    
    # Common styles
    WINDOW_STYLE = f'background-color: {BACKGROUND_PRIMARY}; color: {TEXT_PRIMARY};'
    
    BUTTON_PRIMARY = f'background: {BACKGROUND_ACCENT}; color: {TEXT_PRIMARY}; padding: 10px; border-radius: 8px;'
    BUTTON_SECONDARY = f'background: {TEXT_ACCENT}; color: {TEXT_BUTTON}; padding: 10px; border-radius: 8px;'
    
    COMBO_STYLE = f'padding: 4px; border-radius: 8px; background: {TEXT_ACCENT}; color: {TEXT_BUTTON};'
    
    TEXT_AREA_STYLE = f'background: {BACKGROUND_SECONDARY}; color: {TEXT_PRIMARY}; border-radius: 8px; padding: 10px;'
    
    HEADER_STYLE = f'text-align: left; padding: 6px 4px; background: {BACKGROUND_HIGHLIGHT}; color: {TEXT_PRIMARY};'
    
    TABLE_BORDER = f'border-bottom: 1px solid {BORDER_COLOR}; padding: 4px;'
    

class AppFonts:
    """Centralized font definitions for consistent typography."""
    
    @staticmethod
    def title_font(size: int = 20) -> QFont:
        """Large bold font for titles."""
        font = QFont('Arial', size, QFont.Bold)
        return font
    
    @staticmethod
    def subtitle_font(size: int = 10) -> QFont:
        """Small font for subtitles."""
        font = QFont('Arial', size)
        return font
    
    @staticmethod
    def button_font(size: int = 12) -> QFont:
        """Bold font for buttons."""
        font = QFont('Arial', size, QFont.Bold)
        return font
    
    @staticmethod
    def label_font(size: int = 12) -> QFont:
        """Regular font for labels and text."""
        font = QFont('Arial', size)
        return font
    
    @staticmethod
    def small_font(size: int = 10) -> QFont:
        """Small font for secondary text."""
        font = QFont('Arial', size)
        return font


class UIConstants:
    """Common UI constants and dimensions."""
    
    # Window sizes
    MAIN_MENU_SIZE = (420, 300)
    SIMULATOR_SIZE = (480, 400)
    ROSTERS_SIZE = (500, 500)
    
    # Spacing
    LAYOUT_SPACING = 16
    SMALL_SPACING = 8
    
    # Common alignments
    CENTER = Qt.AlignCenter
    LEFT = Qt.AlignLeft
    RIGHT = Qt.AlignRight