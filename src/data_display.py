"""
Live data display widget
Shows the latest row of data with column names, values, and units
"""
from typing import Dict, Optional
import random
import colorsys
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QScrollArea, QGridLayout
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor, QPalette
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from theme import Theme


class DataDisplayWidget(QWidget):
    """Widget for displaying live data from the log file"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.current_data: Optional[Dict[str, str]] = None
        self.visible_columns: set = set()
        self.column_info: list = []
        # Track maximum absolute value for each column (efficient - only stores max, not all values)
        self.maximum_values: Dict[str, float] = {}
        # Store random color for each column (by row)
        self.column_colors: Dict[str, str] = {}
        # Font sizes (in points)
        self.title_font_size = 60
        self.value_font_size = 100
        self.header_font_size = 34
        self.theme = None
        # Store widget references to avoid recreating them
        self.name_labels: Dict[str, QLabel] = {}
        self.value_labels: Dict[str, QLabel] = {}
        self.maximum_labels: Dict[str, QLabel] = {}
        self.header_labels: Dict[str, QLabel] = {}
        self.no_data_label: Optional[QLabel] = None
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        title = QLabel("Live Data")
        # Title style will be updated when theme is applied
        title.setStyleSheet("font-weight: bold; font-size: 18pt; margin-bottom: 15px;")
        self.title_label = title
        layout.addWidget(title)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        self.data_container = QWidget()
        self.grid_layout = QGridLayout(self.data_container)
        self.grid_layout.setColumnStretch(0, 2)  # Column name - less space
        self.grid_layout.setColumnStretch(1, 3)  # Current value - more space for large numbers
        self.grid_layout.setColumnStretch(2, 3)  # Maximum value - more space for large numbers
        self.grid_layout.setSpacing(5)  # Reduced spacing between rows
        
        scroll.setWidget(self.data_container)
        layout.addWidget(scroll)
        
        # Initial message
        self._show_no_data_message()
    
    def apply_theme(self, theme: 'Theme'):
        """Apply theme to this widget"""
        self.theme = theme
        # Regenerate colors when theme changes to ensure they work with the new theme
        self.column_colors.clear()
        if hasattr(self, 'title_label') and self.title_label:
            title_color = theme.get_color('label_text')
            self.title_label.setStyleSheet(f"font-weight: bold; font-size: 18pt; margin-bottom: 15px; color: {title_color};")
        self.update_display()
    
    def _show_no_data_message(self):
        """Show message when no data is available"""
        self._hide_all_data_widgets()
        if self.no_data_label is None:
            self.no_data_label = QLabel("No data available. Select a log file to begin.")
            self.no_data_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            if self.theme:
                secondary_color = self.theme.get_color('label_secondary')
                self.no_data_label.setStyleSheet(f"color: {secondary_color}; font-size: 18pt; padding: 50px;")
            else:
                self.no_data_label.setStyleSheet("color: gray; font-size: 18pt; padding: 50px;")
            self.grid_layout.addWidget(self.no_data_label, 0, 0, 1, 3)
        else:
            self.no_data_label.show()
    
    def _hide_all_data_widgets(self):
        """Hide all data widgets"""
        if self.no_data_label:
            self.no_data_label.hide()
        for label in self.name_labels.values():
            label.hide()
        for label in self.value_labels.values():
            label.hide()
        for label in self.maximum_labels.values():
            label.hide()
        for label in self.header_labels.values():
            label.hide()
    
    def _clear_display(self):
        """Clear all widgets from the display (used when structure changes)"""
        # Hide all widgets
        self._hide_all_data_widgets()
        # Remove from layout
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        # Clear references
        self.name_labels.clear()
        self.value_labels.clear()
        self.maximum_labels.clear()
        self.header_labels.clear()
        self.no_data_label = None
    
    def set_column_info(self, column_info: list):
        """
        Set column information
        
        Args:
            column_info: List of (column_name, unit) tuples
        """
        self.column_info = column_info
        # Reset maximum values when column info changes (new file loaded)
        self.maximum_values.clear()
        # Reset column colors when column info changes
        self.column_colors.clear()
        self.update_display()
    
    def set_visible_columns(self, visible_columns: Dict[str, bool]):
        """
        Set which columns should be visible
        
        Args:
            visible_columns: Dictionary mapping column names to visibility
        """
        self.visible_columns = {name for name, visible in visible_columns.items() if visible}
        self.update_display()
    
    def update_data(self, data: Dict[str, str], update_display: bool = True):
        """
        Update the displayed data
        
        Args:
            data: Dictionary mapping column names to values
            update_display: Whether to update the display immediately (default: True)
        """
        self.current_data = data
        
        # Update maximum values efficiently (only track max, not all values)
        for column_name, value_str in data.items():
            try:
                value = float(value_str)
                abs_value = abs(value)
                if column_name not in self.maximum_values or abs_value > abs(self.maximum_values[column_name]):
                    self.maximum_values[column_name] = value
            except (ValueError, TypeError):
                # Skip non-numeric values
                pass
        
        if update_display:
            self.update_display()
    
    def update_display(self):
        """Update the display with current data and visibility settings"""
        if not self.current_data or not self.column_info:
            self._show_no_data_message()
            return
        
        # Hide no data message if showing
        if self.no_data_label:
            self.no_data_label.hide()
        
        row = 0
        
        # Create or update header row
        header_text_color = self.theme.get_color('header_text') if self.theme else '#000000'
        
        if 'name_header' not in self.header_labels:
            name_header = QLabel("Parameter")
            name_header.setStyleSheet(f"font-size: {self.header_font_size}pt; padding: 2px; font-weight: bold; color: {header_text_color};")
            self.grid_layout.addWidget(name_header, row, 0)
            self.header_labels['name_header'] = name_header
        else:
            self.header_labels['name_header'].show()
        
        if 'current_header' not in self.header_labels:
            current_header = QLabel("Current")
            current_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            current_header.setStyleSheet(f"font-size: {self.header_font_size}pt; padding: 2px; font-weight: bold; color: {header_text_color};")
            self.grid_layout.addWidget(current_header, row, 1)
            self.header_labels['current_header'] = current_header
        else:
            self.header_labels['current_header'].show()
        
        if 'maximum_header' not in self.header_labels:
            maximum_header = QLabel("Maximum")
            maximum_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
            maximum_header.setStyleSheet(f"font-size: {self.header_font_size}pt; padding: 2px; font-weight: bold; color: {header_text_color};")
            self.grid_layout.addWidget(maximum_header, row, 2)
            self.header_labels['maximum_header'] = maximum_header
        else:
            self.header_labels['maximum_header'].show()
        
        row += 1
        
        # Track which columns we've processed
        processed_columns = set()
        
        # Update or create data rows for visible columns
        for column_name, unit in self.column_info:
            if column_name in self.visible_columns:
                processed_columns.add(column_name)
                value = self.current_data.get(column_name, "N/A")
                
                # Format column label
                if unit:
                    label_text = f"{column_name} ({unit})"
                else:
                    label_text = column_name
                
                # Get or generate color for this column (row)
                row_color = self._get_column_color(column_name)
                
                # Update or create name label
                if column_name not in self.name_labels:
                    name_label = QLabel(label_text)
                    name_label.setStyleSheet(f"font-size: {self.title_font_size}pt; padding: 2px; color: {row_color};")
                    self.grid_layout.addWidget(name_label, row, 0)
                    self.name_labels[column_name] = name_label
                else:
                    # Update text if unit changed
                    self.name_labels[column_name].setText(label_text)
                    # Update color
                    self.name_labels[column_name].setStyleSheet(f"font-size: {self.title_font_size}pt; padding: 2px; color: {row_color};")
                    self.name_labels[column_name].show()
                
                # Update or create value label
                if column_name not in self.value_labels:
                    value_label = QLabel(str(value))
                    value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    value_label.setStyleSheet(f"font-size: {self.value_font_size}pt; padding: 2px; font-weight: bold; color: {row_color};")
                    self.grid_layout.addWidget(value_label, row, 1)
                    self.value_labels[column_name] = value_label
                else:
                    # Update value text
                    self.value_labels[column_name].setText(str(value))
                    # Update color
                    self.value_labels[column_name].setStyleSheet(f"font-size: {self.value_font_size}pt; padding: 2px; font-weight: bold; color: {row_color};")
                    self.value_labels[column_name].show()
                
                # Update or create maximum label
                maximum_value = self._calculate_maximum(column_name)
                if column_name not in self.maximum_labels:
                    maximum_label = QLabel(maximum_value)
                    maximum_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    maximum_label.setStyleSheet(f"font-size: {self.value_font_size}pt; padding: 2px; font-weight: bold; color: {row_color};")
                    self.grid_layout.addWidget(maximum_label, row, 2)
                    self.maximum_labels[column_name] = maximum_label
                else:
                    # Update maximum value
                    self.maximum_labels[column_name].setText(maximum_value)
                    # Update color
                    self.maximum_labels[column_name].setStyleSheet(f"font-size: {self.value_font_size}pt; padding: 2px; font-weight: bold; color: {row_color};")
                    self.maximum_labels[column_name].show()
                
                row += 1
        
        # Hide columns that are no longer visible
        for column_name in list(self.name_labels.keys()):
            if column_name not in processed_columns:
                self.name_labels[column_name].hide()
                if column_name in self.value_labels:
                    self.value_labels[column_name].hide()
                if column_name in self.maximum_labels:
                    self.maximum_labels[column_name].hide()
    
    def _calculate_maximum(self, column_name: str) -> str:
        """
        Get the maximum absolute value for a column
        Returns the value with the largest absolute value (either positive or negative) seen so far
        
        Args:
            column_name: Name of the column
            
        Returns:
            Maximum absolute value as string, or "N/A" if no data
        """
        if column_name not in self.maximum_values:
            return "N/A"
        
        max_value = self.maximum_values[column_name]
        # Format with reasonable precision
        return f"{max_value:.2f}"
    
    def _get_column_color(self, column_name: str) -> str:
        """
        Get or generate a random color for a column (row).
        Colors are consistent per column and work well in both light and dark modes.
        
        Args:
            column_name: Name of the column
            
        Returns:
            Hex color string (e.g., '#FF5733')
        """
        if column_name not in self.column_colors:
            # Generate a random color that works well in both light and dark modes
            # Use HSV color space for better control
            is_dark = self.theme.is_dark_mode if self.theme else True
            
            if is_dark:
                # For dark mode: use bright, saturated colors
                # Hue: 0-360 (full spectrum), Saturation: 0.6-1.0, Value: 0.7-1.0
                h = random.uniform(0, 360)
                s = random.uniform(0.6, 1.0)
                v = random.uniform(0.7, 1.0)
            else:
                # For light mode: use darker, saturated colors
                # Hue: 0-360 (full spectrum), Saturation: 0.7-1.0, Value: 0.3-0.7
                h = random.uniform(0, 360)
                s = random.uniform(0.7, 1.0)
                v = random.uniform(0.3, 0.7)
            
            # Convert HSV to RGB
            r, g, b = colorsys.hsv_to_rgb(h / 360.0, s, v)
            # Convert to hex
            hex_color = f"#{int(r * 255):02X}{int(g * 255):02X}{int(b * 255):02X}"
            self.column_colors[column_name] = hex_color
        
        return self.column_colors[column_name]
    
    def _apply_color_coding(self, column_name: str, value: str, label: QLabel):
        """
        Apply color coding to value labels based on parameter type
        
        Args:
            column_name: Name of the column
            value: Value as string
            label: QLabel to apply styling to
        """
        try:
            num_value = float(value)
        except (ValueError, TypeError):
            return
        
        # Get theme colors or fallback to defaults
        if self.theme:
            error_color = self.theme.get_color('value_error')
            warning_color = self.theme.get_color('value_warning')
            caution_color = self.theme.get_color('value_caution')
            normal_color = self.theme.get_color('value_normal')
        else:
            error_color = '#FF0000'
            warning_color = '#FF8800'
            caution_color = '#FFAA00'
            normal_color = '#000000'
        
        # Base style with large font - will be overridden by color conditions
        base_style = f"font-size: {self.value_font_size}pt; padding: 0px; font-weight: bold;"
        color_applied = False
        
        # Temperature columns - red for high temps
        if "Temperature" in column_name:
            if num_value > 100:
                label.setStyleSheet(f"{base_style} color: {error_color};")
                color_applied = True
            elif num_value > 80:
                label.setStyleSheet(f"{base_style} color: {warning_color};")
                color_applied = True
        
        # Air/Fuel Ratio - color based on lambda value
        elif "Air/Fuel" in column_name or "Fuel Ratio" in column_name:
            if num_value < 0.85:  # Very rich
                label.setStyleSheet(f"{base_style} color: {error_color};")
                color_applied = True
            elif num_value < 0.95:  # Rich
                label.setStyleSheet(f"{base_style} color: {warning_color};")
                color_applied = True
            elif num_value > 1.05:  # Lean
                label.setStyleSheet(f"{base_style} color: {caution_color};")
                color_applied = True
        
        # Knock Retard - red if any knock
        elif "Knock" in column_name:
            if num_value > 0:
                label.setStyleSheet(f"{base_style} color: {error_color};")
                color_applied = True
        
        # Boost/MAP - color for high boost
        elif "Boost" in column_name or "Manifold" in column_name:
            if num_value > 200:  # High boost (kPa)
                label.setStyleSheet(f"{base_style} color: {warning_color};")
                color_applied = True
        
        # If no color coding applied, ensure base style is set (already set by default, but explicit is good)
        if not color_applied:
            label.setStyleSheet(f"{base_style} color: {normal_color};")
    
    def set_title_font_size(self, size: int):
        """
        Set the font size for column titles
        
        Args:
            size: Font size in points
        """
        self.title_font_size = size
        self.update_display()
    
    def set_value_font_size(self, size: int):
        """
        Set the font size for values
        
        Args:
            size: Font size in points
        """
        self.value_font_size = size
        self.update_display()
    
    def set_header_font_size(self, size: int):
        """
        Set the font size for headers
        
        Args:
            size: Font size in points
        """
        self.header_font_size = size
        self.update_display()

