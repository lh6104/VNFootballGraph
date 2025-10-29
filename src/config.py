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
    "tên đầy đủ": "full_name",
    "ngày sinh": "birth_date",
    "nơi sinh": "birth_place",
    "quốc tịch": "nationality",
    "chiều cao": "height",
    "cân nặng": "weight",
    "vị trí": "position",
    
    # Player career info
    "câu lạc bộ hiện tại": "current_club",
    "câu lạc bộ": "current_club",
    "các câu lạc bộ": "former_clubs",
    "clb trước đây": "former_clubs",
    "clb trẻ": "youth_clubs",
    "số áo": "shirt_number",
    "áo số": "shirt_number",
    "đội tuyển quốc gia": "national_team",
    "đội tuyển": "national_team",
    "số trận": "caps",
    "bàn thắng": "goals",
    "ra mắt": "debut_date",
    "giải nghệ": "retirement_date",
    
    # Coach info
    "huấn luyện viên": "coach",
    "hlv": "coach",
    "đội bóng hiện tại": "current_team",
    "đội đang dẫn dắt": "current_team",
    "các đội đã dẫn dắt": "former_teams",
    "đội trước đây": "former_teams",
    "thành tích": "achievements",
    "danh hiệu": "achievements",
    "bắt đầu sự nghiệp hlv": "coaching_career_start",
    "phong cách huấn luyện": "coaching_style",
    
    # Club info
    "giải đấu": "league",
    "sân vận động": "stadium",
    "sân nhà": "stadium",
    "thành lập": "founded_year",
    "năm thành lập": "founded_year",
    "huấn luyện viên trưởng": "head_coach",
    "hlv trưởng": "head_coach",
    "chủ tịch": "chairman",
    "chủ sở hữu": "owner",
    "danh hiệu": "titles",
    "thành tích": "titles",
    
    # National team info
    "liên đoàn": "confederation",
    "fifa": "fifa_ranking",
    "xếp hạng fifa": "fifa_ranking",
    "huấn luyện viên": "head_coach",
    
    # Nationality and origin info
    "quốc tịch kép": "dual_nationality",
    "quốc tịch thứ hai": "second_nationality",
    "nguồn gốc": "origin",
    "gốc": "origin",
    "xuất thân": "origin",
    "cha mẹ": "parents",
    "bố mẹ": "parents",
}

# Keywords to identify entity types from page content
PLAYER_KEYWORDS: List[str] = [
    "cầu thủ", "tiền đạo", "tiền vệ", "hậu vệ", "thủ môn",
    "footballer", "striker", "midfielder", "defender", "goalkeeper",
    # Vietnamese diaspora and naturalized players
    "việt kiều", "cầu thủ việt kiều", "nhập tịch", "cầu thủ nhập tịch",
    "gốc việt", "gốc việt nam", "người gốc việt", "có gốc việt",
    "quốc tịch việt nam", "quốc tịch kép", "hai quốc tịch",
    "sinh tại nước ngoài", "sinh ở nước ngoài",
    "overseas vietnamese", "vietnamese descent", "naturalized",
    "dual citizenship", "dual nationality"
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

# Keywords for Vietnamese diaspora/naturalized players (for categorization)
VIETNAMESE_DIASPORA_KEYWORDS: List[str] = [
    "việt kiều", "cầu thủ việt kiều", "người việt kiều",
    "nhập tịch", "cầu thủ nhập tịch", "nhập tịch việt nam",
    "gốc việt", "gốc việt nam", "người gốc việt", "có gốc việt",
    "cha mẹ người việt", "bố mẹ người việt", "ông bà người việt",
    "quốc tịch kép", "hai quốc tịch", "quốc tịch việt nam",
    "sinh tại", "sinh ở", "lớn lên ở",
    "overseas vietnamese", "vietnamese descent", "vietnamese origin",
    "naturalized vietnamese", "dual citizenship", "dual nationality",
    "born in", "raised in", "vietnamese heritage"
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
# Smart Filtering Strategy
# ============================================================================

# Keywords to KEEP - pages with these keywords should be crawled
KEEP_KEYWORDS: List[str] = [
    "bóng đá", "bóng_đá",
    "cầu thủ", "cầu_thủ",
    "tiền vệ", "tiền_vệ",
    "tiền đạo", "tiền_đạo",
    "hậu vệ", "hậu_vệ",
    "thủ môn", "thủ_môn",
    "huấn luyện viên", "huấn_luyện_viên",
    "câu lạc bộ bóng đá", "câu_lạc_bộ_bóng_đá",
    "clb", "c.l.b",
    "đội tuyển", "đội_tuyển",
    "v.league", "v-league",
    "việt nam", "việt_nam",
]

# Priority keywords - pages with these should be crawled first/always
PRIORITY_KEYWORDS: List[str] = [
    "v.league 1", "v.league_1",
    "đội tuyển bóng đá quốc gia việt nam",
    "câu lạc bộ bóng đá hà nội",
    "nguyễn quang hải",
]

# Keywords to DROP - pages with these should be skipped
DROP_KEYWORDS: List[str] = [
    "phim",
    "xã",
    "huyện", 
    "tỉnh",
    "bóng rổ", "bóng_rổ",
    "cầu lông", "cầu_lông",
    "tennis",
    "bơi lội", "bơi_lội",
    "điền kinh", "điền_kinh",
    "võ thuật", "võ_thuật",
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
