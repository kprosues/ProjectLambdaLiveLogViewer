"""
CSV Parser for tuner log files
Handles parsing of header row with units and data rows
"""
import csv
import re
from typing import List, Dict, Tuple, Optional


class CSVParser:
    """Parser for CSV log files with column names and units"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.column_names: List[str] = []
        self.column_units: List[str] = []
        self.column_count: int = 0
        self._parse_header()
    
    def _parse_header(self):
        """Parse the header row to extract column names and units"""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header_row = next(reader)
                
                self.column_names = []
                self.column_units = []
                
                for header in header_row:
                    # Extract column name and unit from format like "Time (s)" or "Air/Fuel Sensor #1 (λ)"
                    match = re.match(r'^(.+?)\s*\(([^)]+)\)\s*$', header.strip())
                    if match:
                        name = match.group(1).strip()
                        unit = match.group(2).strip()
                    else:
                        # No unit found, use entire header as name
                        name = header.strip()
                        unit = ""
                    
                    self.column_names.append(name)
                    self.column_units.append(unit)
                
                self.column_count = len(self.column_names)
        except Exception as e:
            raise ValueError(f"Failed to parse CSV header: {e}")
    
    def parse_row(self, row_data: str) -> Optional[Dict[str, str]]:
        """
        Parse a single CSV row into a dictionary
        
        Args:
            row_data: CSV row as string
            
        Returns:
            Dictionary mapping column names to values, or None if parsing fails
        """
        try:
            reader = csv.reader([row_data])
            values = next(reader)
            
            if len(values) != self.column_count:
                return None
            
            result = {}
            for i, name in enumerate(self.column_names):
                result[name] = values[i].strip()
            
            return result
        except Exception:
            return None
    
    def get_column_info(self) -> List[Tuple[str, str]]:
        """
        Get list of (column_name, unit) tuples
        
        Returns:
            List of tuples containing column name and unit
        """
        return list(zip(self.column_names, self.column_units))

