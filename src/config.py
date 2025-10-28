"""
Configuration module for Vietnamese Football Graph crawler.
Contains constants, settings, and field mappings.
"""

import os
from typing import Dict, List

# ============================================================================
# Wikipedia Settings
# ============================================================================

WIKI_BASE_URL = "https://vi.wikipedia.org"
WIKI_API_URL = f"{WIKI_BASE_URL}/w/api.php"
WIKI_PAGE_URL = f"{WIKI_BASE_URL}/wiki/"

# Default seed page for testing
DEFAULT_SEED_PAGE = "Nguyễn Quang Hải (sinh 1997)"

# Crawl settings
DEFAULT_MAX_DEPTH = 2
REQUEST_DELAY = 1.0  # seconds between requests to respect rate limits
REQUEST_TIMEOUT = 10  # seconds

# User agent for requests
USER_AGENT = "VNFootballGraphBot/1.0 (Educational Research Project)"

# ============================================================================
# Neo4j Settings
# ============================================================================

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "neo4j")

# ============================================================================
# Vietnamese Field Mappings
# ============================================================================

# Map Vietnamese infobox field names to English keys
FIELD_MAPPINGS: Dict[str, str] = {
    # Personal info
    "họ tên": "name",
    "tên đầy đủ": "full_name",
    "tên": "name",
    "ngày sinh": "birth_date",
    "nơi sinh": "birth_place",
    "quốc tịch": "nationality",
    "chiều cao": "height",
    "vị trí": "position",
    
    # Career info
    "câu lạc bộ hiện tại": "current_club",
    "câu lạc bộ": "club",
    "số áo": "jersey_number",
    "đội tuyển quốc gia": "national_team",
    "đội tuyển": "national_team",
    
    # Coach info
    "huấn luyện viên": "coach",
    "hlv": "coach",
    "đội bóng hiện tại": "current_team",
    
    # Club info
    "giải đấu": "league",
    "sân vận động": "stadium",
    "thành lập": "founded",
    "huấn luyện viên trưởng": "head_coach",
}

# Keywords to identify entity types from page content
PLAYER_KEYWORDS: List[str] = [
    "cầu thủ", "tiền đạo", "tiền vệ", "hậu vệ", "thủ môn",
    "footballer", "striker", "midfielder", "defender", "goalkeeper"
]

COACH_KEYWORDS: List[str] = [
    "huấn luyện viên", "hlv", "coach", "manager", "giám đốc kỹ thuật"
]

CLUB_KEYWORDS: List[str] = [
    "câu lạc bộ", "clb", "club", "đội bóng", "football club"
]

NATIONAL_TEAM_KEYWORDS: List[str] = [
    "đội tuyển", "national team", "đội tuyển quốc gia"
]

# ============================================================================
# Link Filtering
# ============================================================================

# Prefixes to skip when following links
SKIP_PREFIXES: List[str] = [
    "Wikipedia:",
    "Thể loại:",
    "Category:",
    "File:",
    "Tập tin:",
    "Template:",
    "Bản mẫu:",
    "Help:",
    "Trợ giúp:",
    "Portal:",
    "Cổng thông tin:",
    "Special:",
    "Đặc biệt:",
    "Talk:",
    "Thảo luận:",
    "User:",
    "Thành viên:",
]

# Keywords in URLs to skip
SKIP_URL_KEYWORDS: List[str] = [
    "disambiguation",
    "định hướng",
    "trang định hướng",
]

# ============================================================================
# Graph Schema
# ============================================================================

# Node labels
NODE_LABELS = {
    "player": "Player",
    "coach": "Coach",
    "club": "Club",
    "national_team": "NationalTeam",
}

# Relationship types
RELATIONSHIP_TYPES = {
    "played_for": "PLAYED_FOR",
    "coached": "COACHED",
    "trained_under": "TRAINED_UNDER",
    "teammate_with": "TEAMMATE_WITH",
    "member_of": "MEMBER_OF",
    "managed_by": "MANAGED_BY",
}

# ============================================================================
# Output Settings
# ============================================================================

OUTPUT_MODES = ["neo4j", "json", "both"]
DEFAULT_OUTPUT_MODE = "json"

# JSON output file
JSON_OUTPUT_FILE = "data/vn_football_graph.json"

# ============================================================================
# Logging Settings
# ============================================================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
