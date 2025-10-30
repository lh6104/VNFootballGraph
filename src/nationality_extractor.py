"""
Nationality extraction module.
Extracts nationality from multiple sources: infobox, birth_place, categories, text.
"""

import re
import logging
from typing import Optional, Dict, List

logger = logging.getLogger(__name__)


# Country name mappings (Vietnamese <-> English)
COUNTRY_MAPPINGS = {
    # Southeast Asia
    "việt nam": "Vietnam",
    "vietnam": "Vietnam",
    "thái lan": "Thailand",
    "thailand": "Thailand",
    "singapore": "Singapore",
    "malaysia": "Malaysia",
    "indonesia": "Indonesia",
    "philippines": "Philippines",
    "myanmar": "Myanmar",
    "lào": "Laos",
    "campuchia": "Cambodia",
    "cambodia": "Cambodia",
    
    # East Asia
    "hàn quốc": "South Korea",
    "south korea": "South Korea",
    "korea": "South Korea",
    "nhật bản": "Japan",
    "japan": "Japan",
    "trung quốc": "China",
    "china": "China",
    
    # Europe
    "pháp": "France",
    "france": "France",
    "anh": "England",
    "england": "England",
    "tây ban nha": "Spain",
    "spain": "Spain",
    "đức": "Germany",
    "germany": "Germany",
    "ý": "Italy",
    "italy": "Italy",
    "bồ đào nha": "Portugal",
    "portugal": "Portugal",
    "hà lan": "Netherlands",
    "netherlands": "Netherlands",
    "bỉ": "Belgium",
    "belgium": "Belgium",
    
    # Americas
    "brazil": "Brazil",
    "brasil": "Brazil",
    "argentina": "Argentina",
    "mỹ": "United States",
    "united states": "United States",
    "usa": "United States",
    
    # Middle East
    "ả rập xê út": "Saudi Arabia",
    "saudi arabia": "Saudi Arabia",
    "các tiểu vương quốc ả rập thống nhất": "UAE",
    "uae": "UAE",
    "iran": "Iran",
    "iraq": "Iraq",
    
    # Others
    "úc": "Australia",
    "australia": "Australia",
    "ấn độ": "India",
    "india": "India",
}


def extract_nationality(
    properties: Dict,
    categories: List[str] = None,
    text: str = ""
) -> Optional[str]:
    """
    Extract nationality from multiple sources.
    
    Priority:
    1. Direct nationality field in properties
    2. Parse from birth_place
    3. Parse from categories
    4. Parse from text
    
    Args:
        properties: Infobox properties dict
        categories: List of Wikipedia categories
        text: Page text (first paragraph)
        
    Returns:
        Nationality string (standardized English name) or None
    """
    categories = categories or []
    
    # 1. Check direct nationality field
    nationality = properties.get('nationality')
    if nationality:
        standardized = _standardize_country_name(nationality)
        if standardized:
            logger.debug(f"Nationality from infobox: {standardized}")
            return standardized
    
    # 2. Parse from birth_place
    birth_place = properties.get('birth_place', '')
    if birth_place:
        nationality = _extract_from_birth_place(birth_place)
        if nationality:
            logger.debug(f"Nationality from birth_place: {nationality}")
            return nationality
    
    # 3. Parse from categories
    for category in categories:
        nationality = _extract_from_category(category)
        if nationality:
            logger.debug(f"Nationality from category: {nationality}")
            return nationality
    
    # 4. Parse from text (last resort)
    if text:
        nationality = _extract_from_text(text)
        if nationality:
            logger.debug(f"Nationality from text: {nationality}")
            return nationality
    
    return None


def _standardize_country_name(country: str) -> Optional[str]:
    """Standardize country name to English."""
    country_lower = country.lower().strip()
    
    # Direct mapping
    if country_lower in COUNTRY_MAPPINGS:
        return COUNTRY_MAPPINGS[country_lower]
    
    # Partial match
    for key, value in COUNTRY_MAPPINGS.items():
        if key in country_lower or country_lower in key:
            return value
    
    # Return as-is if not found (might be already in English)
    return country.strip()


def _extract_from_birth_place(birth_place: str) -> Optional[str]:
    """
    Extract nationality from birth_place.
    E.g., "Đông Anh, Hà Nội, Việt Nam" -> "Vietnam"
    """
    birth_place_lower = birth_place.lower()
    
    # Check each country name
    for key, value in COUNTRY_MAPPINGS.items():
        if key in birth_place_lower:
            return value
    
    # Try to get last part (usually country)
    parts = birth_place.split(',')
    if len(parts) >= 2:
        last_part = parts[-1].strip().lower()
        return _standardize_country_name(last_part)
    
    return None


def _extract_from_category(category: str) -> Optional[str]:
    """
    Extract nationality from category.
    E.g., "Cầu thủ bóng đá Hàn Quốc" -> "South Korea"
    """
    category_lower = category.lower()
    
    # Check each country name
    for key, value in COUNTRY_MAPPINGS.items():
        if key in category_lower:
            return value
    
    return None


def _extract_from_text(text: str) -> Optional[str]:
    """
    Extract nationality from text using patterns.
    E.g., "là cầu thủ người Hàn Quốc" -> "South Korea"
    """
    text_lower = text.lower()
    
    # Patterns to match
    patterns = [
        r"người\s+(\w+)",  # "người Hàn Quốc"
        r"quốc tịch\s+(\w+)",  # "quốc tịch Việt Nam"
        r"(\w+)\s+national",  # "Korean national"
        r"from\s+(\w+)",  # "from France"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            country = match.group(1)
            standardized = _standardize_country_name(country)
            if standardized:
                return standardized
    
    # Check each country name in text
    for key, value in COUNTRY_MAPPINGS.items():
        if key in text_lower:
            return value
    
    return None


def add_nationality_to_entities(entities: List[Dict]) -> List[Dict]:
    """
    Add nationality field to all entities that don't have it.
    
    Args:
        entities: List of entity dicts
        
    Returns:
        Updated entities list
    """
    updated_count = 0
    
    for entity in entities:
        props = entity.get('properties', {})
        
        # Skip if already has nationality
        if props.get('nationality'):
            continue
        
        # Extract nationality
        nationality = extract_nationality(
            properties=props,
            categories=entity.get('categories', []),
            text=entity.get('first_paragraph', '')
        )
        
        if nationality:
            props['nationality'] = nationality
            updated_count += 1
    
    logger.info(f"Added nationality to {updated_count}/{len(entities)} entities")
    return entities
