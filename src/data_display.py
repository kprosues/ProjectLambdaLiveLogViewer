"""
Live data display widget
Shows the latest row of data with column names, values, and units
"""
from typing import Dict, Optional, List
from collections import defaultdict
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
        # Track all observed values for each column to calculate averages
        self.observed_values: Dict[str, List[float]] = defaultdict(list)
        # Font sizes (in points)
        self.title_font_size = 60
        self.value_font_size = 100
        self.header_font_size = 34
        self.theme = None
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
        self.grid_layout.setColumnStretch(2, 3)  # Average value - more space for large numbers
        self.grid_layout.setSpacing(5)  # Reduced spacing between rows
        
        scroll.setWidget(self.data_container)
        layout.addWidget(scroll)
        
        # Initial message
        self._show_no_data_message()
    
    def apply_theme(self, theme: 'Theme'):
        """Apply theme to this widget"""
        self.theme = theme
        if hasattr(self, 'title_label') and self.title_label:
            title_color = theme.get_color('label_text')
            self.title_label.setStyleSheet(f"font-weight: bold; font-size: 18pt; margin-bottom: 15px; color: {title_color};")
        self.update_display()
    
    def _show_no_data_message(self):
        """Show message when no data is available"""
        self._clear_display()
        label = QLabel("No data available. Select a log file to begin.")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if self.theme:
            secondary_color = self.theme.get_color('label_secondary')
            label.setStyleSheet(f"color: {secondary_color}; font-size: 18pt; padding: 50px;")
        else:
            label.setStyleSheet("color: gray; font-size: 18pt; padding: 50px;")
        self.grid_layout.addWidget(label, 0, 0, 1, 3)
    
    def _clear_display(self):
        """Clear all widgets from the display"""
        while self.grid_layout.count():
            child = self.grid_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
    
    def set_column_info(self, column_info: list):
        """
        Set column information
        
        Args:
            column_info: List of (column_name, unit) tuples
        """
        self.column_info = column_info
        # Reset observed values when column info changes (new file loaded)
        self.observed_values.clear()
        self.update_display()
    
    def set_visible_columns(self, visible_columns: Dict[str, bool]):
        """
        Set which columns should be visible
        
        Args:
            visible_columns: Dictionary mapping column names to visibility
        """
        self.visible_columns = {name for name, visible in visible_columns.items() if visible}
        self.update_display()
    
    def update_data(self, data: Dict[str, str], update_display: bool = True, track_values: bool = True):
        """
        Update the displayed data
        
        Args:
            data: Dictionary mapping column names to values
            update_display: Whether to update the display immediately (default: True)
            track_values: Whether to track values for average calculation (default: True)
        """
        self.current_data = data
        
        # Track observed values for average calculation only if requested
        if track_values:
            self._track_observed_values(data)
        
        if update_display:
            self.update_display()
    
    def _track_observed_values(self, data: Dict[str, str]):
        """
        Track observed values for average calculation without updating display
        
        Args:
            data: Dictionary mapping column names to values
        """
        for column_name, value_str in data.items():
            try:
                # Try to convert to float for numeric columns
                value = float(value_str)
                self.observed_values[column_name].append(value)
            except (ValueError, TypeError):
                # Skip non-numeric values
                pass
    
    def update_display(self):
        """Update the display with current data and visibility settings"""
        self._clear_display()
        
        if not self.current_data or not self.column_info:
            self._show_no_data_message()
            return
        
        row = 0
        
        # Add header row for current and average values
        header_text_color = self.theme.get_color('header_text') if self.theme else '#000000'
        name_header = QLabel("Parameter")
        name_header.setStyleSheet(f"font-size: {self.header_font_size}pt; padding: 2px; font-weight: bold; color: {header_text_color};")
        current_header = QLabel("Current")
        current_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        current_header.setStyleSheet(f"font-size: {self.header_font_size}pt; padding: 2px; font-weight: bold; color: {header_text_color};")
        average_header = QLabel("Average")
        average_header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        average_header.setStyleSheet(f"font-size: {self.header_font_size}pt; padding: 2px; font-weight: bold; color: {header_text_color};")
        
        self.grid_layout.addWidget(name_header, row, 0)
        self.grid_layout.addWidget(current_header, row, 1)
        self.grid_layout.addWidget(average_header, row, 2)
        row += 1
        
        # Add data rows for visible columns
        for column_name, unit in self.column_info:
            if column_name in self.visible_columns:
                value = self.current_data.get(column_name, "N/A")
                
                # Format column label
                if unit:
                    label_text = f"{column_name} ({unit})"
                else:
                    label_text = column_name
                
                label_text_color = self.theme.get_color('label_text') if self.theme else '#000000'
                name_label = QLabel(label_text)
                name_label.setStyleSheet(f"font-size: {self.title_font_size}pt; padding: 2px; color: {label_text_color};")
                
                value_label = QLabel(str(value))
                value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                # Use very large font for values - easy to read at a glance
                normal_color = self.theme.get_color('value_normal') if self.theme else '#000000'
                value_label.setStyleSheet(f"font-size: {self.value_font_size}pt; padding: 2px; font-weight: bold; color: {normal_color};")
                
                # Apply color coding for certain parameters
                self._apply_color_coding(column_name, value, value_label)
                
                # Calculate and display average
                average_value = self._calculate_average(column_name)
                average_label = QLabel(average_value)
                average_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                average_color = self.theme.get_color('value_average') if self.theme else '#0000FF'
                average_label.setStyleSheet(f"font-size: {self.value_font_size}pt; padding: 2px; font-weight: bold; color: {average_color};")
                
                self.grid_layout.addWidget(name_label, row, 0)
                self.grid_layout.addWidget(value_label, row, 1)
                self.grid_layout.addWidget(average_label, row, 2)
                row += 1
    
    def _calculate_average(self, column_name: str) -> str:
        """
        Calculate average for a column based on observed values
        
        Args:
            column_name: Name of the column
            
        Returns:
            Average value as string, or "N/A" if no data
        """
        values = self.observed_values.get(column_name, [])
        if not values:
            return "N/A"
        
        average = sum(values) / len(values)
        # Format with reasonable precision
        return f"{average:.2f}"
    
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

