"""
Theme system for light and dark mode support
"""
from typing import Dict
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication


class Theme:
    """Theme manager for light and dark modes"""
    
    # Light mode colors
    LIGHT_COLORS = {
        'background': '#FFFFFF',
        'foreground': '#000000',
        'secondary_background': '#F5F5F5',
        'secondary_foreground': '#333333',
        'border': '#CCCCCC',
        'button_background': '#E0E0E0',
        'button_hover': '#D0D0D0',
        'button_pressed': '#B0B0B0',
        'button_text': '#000000',
        'header_background': '#F0F0F0',
        'header_text': '#000000',
        'scrollbar_background': '#E0E0E0',
        'scrollbar_handle': '#B0B0B0',
        'input_background': '#FFFFFF',
        'input_border': '#CCCCCC',
        'label_text': '#000000',
        'label_secondary': '#666666',
        'status_success': '#00AA00',
        'status_warning': '#FF8800',
        'status_error': '#FF0000',
        # Color coding for values
        'value_normal': '#000000',
        'value_warning': '#FF8800',
        'value_error': '#FF0000',
        'value_caution': '#FFAA00',
        'value_average': '#0000FF',
        'value_maximum': '#9C27B0',  # Purple
    }
    
    # Dark mode colors
    DARK_COLORS = {
        'background': '#1E1E1E',
        'foreground': '#E0E0E0',
        'secondary_background': '#2D2D2D',
        'secondary_foreground': '#E0E0E0',
        'border': '#404040',
        'button_background': '#3C3C3C',
        'button_hover': '#4C4C4C',
        'button_pressed': '#2C2C2C',
        'button_text': '#E0E0E0',
        'header_background': '#252525',
        'header_text': '#E0E0E0',
        'scrollbar_background': '#2D2D2D',
        'scrollbar_handle': '#505050',
        'input_background': '#2D2D2D',
        'input_border': '#404040',
        'label_text': '#E0E0E0',
        'label_secondary': '#A0A0A0',
        'status_success': '#4CAF50',
        'status_warning': '#FF9800',
        'status_error': '#F44336',
        # Color coding for values - adjusted for dark mode visibility
        'value_normal': '#E0E0E0',
        'value_warning': '#FF9800',
        'value_error': '#F44336',
        'value_caution': '#FFC107',
        'value_average': '#64B5F6',  # Lighter blue for dark mode
        'value_maximum': '#BA68C8',  # Lighter purple for dark mode
    }
    
    def __init__(self):
        self.settings = QSettings()
        self._dark_mode = self.settings.value('dark_mode', True, type=bool)
        self._current_colors = self.DARK_COLORS if self._dark_mode else self.LIGHT_COLORS
    
    @property
    def is_dark_mode(self) -> bool:
        """Check if dark mode is enabled"""
        return self._dark_mode
    
    def set_dark_mode(self, enabled: bool):
        """Set dark mode on or off"""
        self._dark_mode = enabled
        self._current_colors = self.DARK_COLORS if enabled else self.LIGHT_COLORS
        self.settings.setValue('dark_mode', enabled)
        self.apply_to_app()
    
    def toggle_dark_mode(self):
        """Toggle dark mode"""
        self.set_dark_mode(not self._dark_mode)
    
    def get_color(self, key: str) -> str:
        """Get a color value by key"""
        return self._current_colors.get(key, '#000000')
    
    def get_all_colors(self) -> Dict[str, str]:
        """Get all current theme colors"""
        return self._current_colors.copy()
    
    def apply_to_app(self):
        """Apply theme to the entire QApplication"""
        app = QApplication.instance()
        if not app:
            return
        
        palette = QPalette()
        colors = self._current_colors
        
        # Set palette colors
        palette.setColor(QPalette.ColorRole.Window, QColor(colors['background']))
        palette.setColor(QPalette.ColorRole.WindowText, QColor(colors['foreground']))
        palette.setColor(QPalette.ColorRole.Base, QColor(colors['input_background']))
        palette.setColor(QPalette.ColorRole.AlternateBase, QColor(colors['secondary_background']))
        palette.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors['background']))
        palette.setColor(QPalette.ColorRole.ToolTipText, QColor(colors['foreground']))
        palette.setColor(QPalette.ColorRole.Text, QColor(colors['foreground']))
        palette.setColor(QPalette.ColorRole.Button, QColor(colors['button_background']))
        palette.setColor(QPalette.ColorRole.ButtonText, QColor(colors['button_text']))
        palette.setColor(QPalette.ColorRole.BrightText, QColor(colors['value_error']))
        palette.setColor(QPalette.ColorRole.Link, QColor(colors['value_average']))
        palette.setColor(QPalette.ColorRole.Highlight, QColor(colors['value_average']))
        palette.setColor(QPalette.ColorRole.HighlightedText, QColor(colors['background']))
        
        app.setPalette(palette)
    
    def get_stylesheet(self) -> str:
        """Get a stylesheet string for widgets"""
        colors = self._current_colors
        return f"""
            QWidget {{
                background-color: {colors['background']};
                color: {colors['foreground']};
            }}
            QPushButton {{
                background-color: {colors['button_background']};
                color: {colors['button_text']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                padding: 8px;
            }}
            QPushButton:hover {{
                background-color: {colors['button_hover']};
            }}
            QPushButton:pressed {{
                background-color: {colors['button_pressed']};
            }}
            QPushButton:disabled {{
                background-color: {colors['secondary_background']};
                color: {colors['label_secondary']};
            }}
            QLabel {{
                color: {colors['label_text']};
            }}
            QScrollArea {{
                background-color: {colors['background']};
                border: 1px solid {colors['border']};
            }}
            QScrollBar:vertical {{
                background-color: {colors['scrollbar_background']};
                width: 12px;
                border: none;
            }}
            QScrollBar::handle:vertical {{
                background-color: {colors['scrollbar_handle']};
                min-height: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {colors['button_hover']};
            }}
            QScrollBar:horizontal {{
                background-color: {colors['scrollbar_background']};
                height: 12px;
                border: none;
            }}
            QScrollBar::handle:horizontal {{
                background-color: {colors['scrollbar_handle']};
                min-width: 20px;
                border-radius: 6px;
            }}
            QScrollBar::handle:horizontal:hover {{
                background-color: {colors['button_hover']};
            }}
            QCheckBox {{
                color: {colors['label_text']};
            }}
            QCheckBox::indicator {{
                background-color: {colors['input_background']};
                border: 2px solid {colors['border']};
            }}
            QCheckBox::indicator:checked {{
                background-color: {colors['value_average']};
            }}
            QGroupBox {{
                color: {colors['label_text']};
                border: 1px solid {colors['border']};
                border-radius: 4px;
                margin-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
            QDialog {{
                background-color: {colors['background']};
            }}
            QMenuBar {{
                background-color: {colors['header_background']};
                color: {colors['header_text']};
            }}
            QMenuBar::item {{
                background-color: transparent;
            }}
            QMenuBar::item:selected {{
                background-color: {colors['button_hover']};
            }}
            QMenu {{
                background-color: {colors['background']};
                color: {colors['foreground']};
                border: 1px solid {colors['border']};
            }}
            QMenu::item:selected {{
                background-color: {colors['button_hover']};
            }}
            QStatusBar {{
                background-color: {colors['header_background']};
                color: {colors['header_text']};
            }}
            QInputDialog {{
                background-color: {colors['background']};
            }}
            QMessageBox {{
                background-color: {colors['background']};
            }}
        """


# Global theme instance
_theme_instance = None


def get_theme() -> Theme:
    """Get the global theme instance"""
    global _theme_instance
    if _theme_instance is None:
        _theme_instance = Theme()
    return _theme_instance

