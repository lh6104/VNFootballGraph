"""
Infobox parser for Vietnamese Wikipedia pages.
Extracts and normalizes structured data from infobox tables.
"""

import re
import logging
from typing import Dict, Optional, List
from bs4 import BeautifulSoup, Tag

from . import config

logger = logging.getLogger(__name__)


class InfoboxParser:
    """Parses Vietnamese Wikipedia infobox tables."""
    
    def __init__(self):
        """Initialize the parser."""
        self.field_mappings = config.FIELD_MAPPINGS
    
    def parse(self, infobox: Optional[BeautifulSoup]) -> Dict[str, str]:
        """
        Parse infobox table into structured data.
        
        Args:
            infobox: BeautifulSoup object of infobox table
            
        Returns:
            Dictionary of normalized field data
        """
        if not infobox:
            return {}
        
        data = {}
        
        # Extract rows from infobox
        rows = infobox.find_all('tr')
        
        for row in rows:
            # Find header and data cells
            header = row.find('th')
            value_cell = row.find('td')
            
            if not header or not value_cell:
                continue
            
            # Extract field name and value
            field_name = self._clean_text(header.get_text())
            field_value = self._extract_value(value_cell)
            
            if not field_name or not field_value:
                continue
            
            # Normalize field name
            normalized_name = self._normalize_field_name(field_name)
            
            if normalized_name:
                data[normalized_name] = field_value
                logger.debug(f"Parsed field: {field_name} -> {normalized_name} = {field_value}")
        
        return data
    
    def _normalize_field_name(self, field_name: str) -> Optional[str]:
        """
        Normalize Vietnamese field name to English key.
        
        Args:
            field_name: Vietnamese field name
            
        Returns:
            Normalized English key or None
        """
        field_lower = field_name.lower().strip()
        
        # Direct mapping
        if field_lower in self.field_mappings:
            return self.field_mappings[field_lower]
        
        # Partial matching for compound fields
        for vn_name, en_name in self.field_mappings.items():
            if vn_name in field_lower:
                return en_name
        
        # Return original if no mapping found (for custom fields)
        return field_lower.replace(' ', '_')
    
    def _extract_value(self, cell: Tag) -> str:
        """
        Extract text value from table cell, handling links and formatting.
        
        Args:
            cell: BeautifulSoup Tag object
            
        Returns:
            Cleaned text value
        """
        # Handle links - extract both text and linked pages
        links = cell.find_all('a')
        if links:
            # Get text from all links
            link_texts = []
            for link in links:
                text = self._clean_text(link.get_text())
                if text:
                    link_texts.append(text)
            
            if link_texts:
                return ', '.join(link_texts)
        
        # Fall back to full cell text
        return self._clean_text(cell.get_text())
    
    def _clean_text(self, text: str) -> str:
        """
        Clean and normalize text.
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if not text:
            return ""
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove reference markers [1], [2], etc.
        text = re.sub(r'\[\d+\]', '', text)
        
        # Remove citation needed markers
        text = re.sub(r'\[cần dẫn nguồn\]', '', text, flags=re.IGNORECASE)
        
        # Strip whitespace
        text = text.strip()
        
        return text
    
    def extract_links_from_field(self, infobox: Optional[BeautifulSoup], 
                                  field_name: str) -> List[str]:
        """
        Extract Wikipedia links from a specific infobox field.
        
        Args:
            infobox: BeautifulSoup object of infobox table
            field_name: Field name to extract links from
            
        Returns:
            List of linked page titles
        """
        if not infobox:
            return []
        
        links = []
        rows = infobox.find_all('tr')
        
        for row in rows:
            header = row.find('th')
            value_cell = row.find('td')
            
            if not header or not value_cell:
                continue
            
            # Check if this is the field we're looking for
            header_text = self._clean_text(header.get_text()).lower()
            normalized = self._normalize_field_name(header_text)
            
            if normalized != field_name:
                continue
            
            # Extract links from this field
            for link in value_cell.find_all('a', href=True):
                href = link['href']
                
                if href.startswith('/wiki/'):
                    page_title = href.replace('/wiki/', '')
                    
                    # Remove URL encoding
                    from urllib.parse import unquote
                    page_title = unquote(page_title)
                    
                    # Remove anchor
                    if '#' in page_title:
                        page_title = page_title.split('#')[0]
                    
                    if page_title:
                        links.append(page_title)
        
        return links
    
    def parse_date(self, date_str: str) -> Optional[str]:
        """
        Parse Vietnamese date string to ISO format.
        
        Args:
            date_str: Vietnamese date string
            
        Returns:
            ISO format date (YYYY-MM-DD) or original string
        """
        if not date_str:
            return None
        
        # Common Vietnamese date patterns
        # Example: "15 tháng 4 năm 1997"
        pattern1 = r'(\d{1,2})\s+tháng\s+(\d{1,2})\s+năm\s+(\d{4})'
        match = re.search(pattern1, date_str)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Example: "15/4/1997"
        pattern2 = r'(\d{1,2})/(\d{1,2})/(\d{4})'
        match = re.search(pattern2, date_str)
        if match:
            day, month, year = match.groups()
            return f"{year}-{month.zfill(2)}-{day.zfill(2)}"
        
        # Example: "1997"
        pattern3 = r'(\d{4})'
        match = re.search(pattern3, date_str)
        if match:
            return match.group(1)
        
        # Return original if no pattern matches
        return date_str
    
    def parse_height(self, height_str: str) -> Optional[float]:
        """
        Parse height string to centimeters.
        
        Args:
            height_str: Height string (e.g., "1,68 m", "168 cm")
            
        Returns:
            Height in centimeters or None
        """
        if not height_str:
            return None
        
        # Remove spaces
        height_str = height_str.replace(' ', '')
        
        # Pattern for meters: "1,68m" or "1.68m"
        pattern_m = r'(\d+)[,.](\d+)\s*m'
        match = re.search(pattern_m, height_str, re.IGNORECASE)
        if match:
            meters = float(f"{match.group(1)}.{match.group(2)}")
            return meters * 100
        
        # Pattern for centimeters: "168cm"
        pattern_cm = r'(\d+)\s*cm'
        match = re.search(pattern_cm, height_str, re.IGNORECASE)
        if match:
            return float(match.group(1))
        
        return None
    
    def extract_relationships(self, infobox_data: Dict) -> Dict[str, List[str]]:
        """
        Extract relationship information from parsed infobox data.
        
        Args:
            infobox_data: Parsed infobox dictionary
            
        Returns:
            Dictionary mapping relationship types to entity names
        """
        relationships = {
            'clubs': [],
            'coaches': [],
            'national_teams': [],
        }
        
        # Extract clubs
        if 'current_club' in infobox_data:
            relationships['clubs'].append(infobox_data['current_club'])
        
        if 'club' in infobox_data:
            clubs = infobox_data['club'].split(',')
            relationships['clubs'].extend([c.strip() for c in clubs])
        
        # Extract coaches
        if 'coach' in infobox_data:
            coaches = infobox_data['coach'].split(',')
            relationships['coaches'].extend([c.strip() for c in coaches])
        
        # Extract national teams
        if 'national_team' in infobox_data:
            teams = infobox_data['national_team'].split(',')
            relationships['national_teams'].extend([t.strip() for t in teams])
        
        # Remove duplicates
        for key in relationships:
            relationships[key] = list(set(relationships[key]))
        
        return relationships
