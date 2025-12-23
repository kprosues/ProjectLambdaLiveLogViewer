"""
Column visibility configuration dialog
Allows users to show/hide columns and persists preferences
"""
from typing import Dict, Set
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QCheckBox, QLabel, 
    QGroupBox, QPushButton, QScrollArea, QDialog, QDialogButtonBox,
    QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal, QSettings
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from theme import Theme


# Default columns to select when no preferences are saved
# These will only be selected if they exist in the loaded datalog file
DEFAULT_SELECTED_COLUMNS = {
    "Time",
    "Ignition Advance Multiplier",
    "Knock Retard",
    "Fuel Trim - Short Term",
    "Fuel Trim - Long Term",
}


class ColumnConfigDialog(QDialog):
    """Dialog for configuring column visibility"""
    
    visibility_changed = pyqtSignal(dict)  # Emits dict of {column_name: visible}
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.settings = QSettings()
        self.checkboxes: Dict[str, QCheckBox] = {}
        self.column_info: list = []
        self.theme = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI"""
        self.setWindowTitle("Column Visibility")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Button bar with select/deselect all buttons
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 10)
        
        self.select_all_button = QPushButton("Select All")
        self.select_all_button.setMinimumHeight(50)
        self.select_all_button.setMinimumWidth(180)
        # Button style will be set by apply_theme if theme is available
        if not self.theme:
            self.select_all_button.setStyleSheet("""
                QPushButton {
                    font-size: 14pt;
                    font-weight: bold;
                    padding: 10px;
                }
            """)
        self.select_all_button.clicked.connect(self._select_all)
        self.select_all_button.setEnabled(False)
        button_layout.addWidget(self.select_all_button)
        
        self.deselect_all_button = QPushButton("Deselect All")
        self.deselect_all_button.setMinimumHeight(50)
        self.deselect_all_button.setMinimumWidth(180)
        # Button style will be set by apply_theme if theme is available
        if not self.theme:
            self.deselect_all_button.setStyleSheet("""
                QPushButton {
                    font-size: 14pt;
                    font-weight: bold;
                    padding: 10px;
                }
            """)
        self.deselect_all_button.clicked.connect(self._deselect_all)
        self.deselect_all_button.setEnabled(False)
        button_layout.addWidget(self.deselect_all_button)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Checkbox container widget with scrolling and grid layout
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        checkbox_widget = QWidget()
        self.checkbox_layout = QGridLayout(checkbox_widget)
        self.checkbox_layout.setSpacing(10)
        self.checkbox_layout.setContentsMargins(10, 10, 10, 10)
        
        self.checkbox_container = checkbox_widget
        scroll.setWidget(checkbox_widget)
        
        layout.addWidget(scroll, 1)  # Stretch factor to fill space
        
        # Dialog buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        button_box.rejected.connect(self.accept)
        # Button box style will be set by theme stylesheet
        if not self.theme:
            button_box.setStyleSheet("""
                QPushButton {
                    font-size: 12pt;
                    padding: 8px 20px;
                    min-height: 40px;
                }
            """)
        layout.addWidget(button_box)
    
    def apply_theme(self, theme: 'Theme'):
        """Apply theme to this dialog"""
        self.theme = theme
        if theme:
            self.setStyleSheet(theme.get_stylesheet())
            # Update button styles
            if self.theme:
                button_style = f"""
                    QPushButton {{
                        background-color: {self.theme.get_color('button_background')};
                        color: {self.theme.get_color('button_text')};
                        font-size: 14pt;
                        font-weight: bold;
                        padding: 10px;
                        border: 1px solid {self.theme.get_color('border')};
                        border-radius: 4px;
                    }}
                    QPushButton:hover {{
                        background-color: {self.theme.get_color('button_hover')};
                    }}
                    QPushButton:pressed {{
                        background-color: {self.theme.get_color('button_pressed')};
                    }}
                """
                self.select_all_button.setStyleSheet(button_style)
                self.deselect_all_button.setStyleSheet(button_style)
                
                checkbox_style = f"""
                    QCheckBox {{
                        font-size: 12pt;
                        spacing: 15px;
                        padding: 8px;
                        min-height: 45px;
                        color: {self.theme.get_color('label_text')};
                    }}
                    QCheckBox::indicator {{
                        width: 28px;
                        height: 28px;
                        background-color: {self.theme.get_color('input_background')};
                        border: 2px solid {self.theme.get_color('border')};
                    }}
                    QCheckBox::indicator:checked {{
                        background-color: {self.theme.get_color('value_average')};
                    }}
                """
                # Apply to existing checkboxes
                for checkbox in self.checkboxes.values():
                    checkbox.setStyleSheet(checkbox_style)
    
    def set_columns(self, column_info: list):
        """
        Set the columns to configure
        
        Args:
            column_info: List of (column_name, unit) tuples
        """
        # Sort columns alphabetically by column name
        sorted_column_info = sorted(column_info, key=lambda x: x[0].lower())
        self.column_info = sorted_column_info
        
        # Clear existing checkboxes
        for checkbox in self.checkboxes.values():
            checkbox.setParent(None)
            checkbox.deleteLater()
        self.checkboxes.clear()
        
        # Load saved preferences
        saved_visibility = self._load_visibility_preferences()
        
        # Create checkboxes for each column in a grid (3 columns)
        num_columns = 3
        # Default checkbox style
        checkbox_style = """
            QCheckBox {
                font-size: 12pt;
                spacing: 15px;
                padding: 8px;
                min-height: 45px;
            }
            QCheckBox::indicator {
                width: 28px;
                height: 28px;
            }
        """
        # Use theme style if available
        if self.theme:
            checkbox_style = f"""
                QCheckBox {{
                    font-size: 12pt;
                    spacing: 15px;
                    padding: 8px;
                    min-height: 45px;
                    color: {self.theme.get_color('label_text')};
                }}
                QCheckBox::indicator {{
                    width: 28px;
                    height: 28px;
                    background-color: {self.theme.get_color('input_background')};
                    border: 2px solid {self.theme.get_color('border')};
                }}
                QCheckBox::indicator:checked {{
                    background-color: {self.theme.get_color('value_average')};
                }}
            """
        
        for idx, (column_name, unit) in enumerate(sorted_column_info):
            checkbox = QCheckBox(self._format_column_label(column_name, unit))
            checkbox.setChecked(saved_visibility.get(column_name, True))
            checkbox.setStyleSheet(checkbox_style)
            checkbox.stateChanged.connect(self._on_checkbox_changed)
            row = idx // num_columns
            col = idx % num_columns
            self.checkbox_layout.addWidget(checkbox, row, col)
            self.checkboxes[column_name] = checkbox
        
        # Enable buttons if we have columns
        has_columns = len(self.checkboxes) > 0
        self.select_all_button.setEnabled(has_columns)
        self.deselect_all_button.setEnabled(has_columns)
        
        self._emit_visibility()
    
    def _format_column_label(self, name: str, unit: str) -> str:
        """Format column label for display"""
        if unit:
            return f"{name} ({unit})"
        return name
    
    def _on_checkbox_changed(self):
        """Handle checkbox state change"""
        self._save_visibility_preferences()
        self._emit_visibility()
    
    def _emit_visibility(self):
        """Emit current visibility state"""
        visibility = {
            name: checkbox.isChecked()
            for name, checkbox in self.checkboxes.items()
        }
        self.visibility_changed.emit(visibility)
    
    def _load_visibility_preferences(self) -> Dict[str, bool]:
        """Load column visibility preferences from QSettings"""
        visibility = {}
        settings_key = "column_visibility/"
        
        # Check if any preferences have been saved for the current columns
        has_saved_preferences = any(
            self.settings.contains(f"{settings_key}{column_name}")
            for column_name, _ in self.column_info
        )
        
        for column_name, _ in self.column_info:
            key = f"{settings_key}{column_name}"
            if has_saved_preferences:
                # Use saved preference, defaulting to False for unsaved columns
                visibility[column_name] = self.settings.value(key, False, type=bool)
            else:
                # First time loading - use default selection if column exists in defaults
                visibility[column_name] = column_name in DEFAULT_SELECTED_COLUMNS
        
        return visibility
    
    def _save_visibility_preferences(self):
        """Save column visibility preferences to QSettings"""
        settings_key = "column_visibility/"
        
        for column_name, checkbox in self.checkboxes.items():
            key = f"{settings_key}{column_name}"
            self.settings.setValue(key, checkbox.isChecked())
    
    def _select_all(self):
        """Select all column checkboxes"""
        # Temporarily disconnect to avoid multiple signals
        for checkbox in self.checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(True)
            checkbox.blockSignals(False)
        
        # Save preferences and emit signal once
        self._save_visibility_preferences()
        self._emit_visibility()
    
    def _deselect_all(self):
        """Deselect all column checkboxes"""
        # Temporarily disconnect to avoid multiple signals
        for checkbox in self.checkboxes.values():
            checkbox.blockSignals(True)
            checkbox.setChecked(False)
            checkbox.blockSignals(False)
        
        # Save preferences and emit signal once
        self._save_visibility_preferences()
        self._emit_visibility()

