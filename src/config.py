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
    "quốc gia": "nationality",  # Alternative field name
    "nationality": "nationality",  # English field
    "country": "nationality",
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
    # Vietnamese terms
    "huấn luyện viên", "hlv", "huấn_luyện_viên",
    "huấn luyện viên trưởng", "hlv trưởng",
    "trợ lý huấn luyện viên", "trợ lý hlv",
    "giám đốc kỹ thuật",
    "nhà cầm quân", "chiến lược gia",
    "dẫn dắt", "dẫn_dắt",
    
    # English terms (for foreign coaches)
    "coach", "manager", "head coach", "assistant coach",
    "technical director", "tactician",
    "manages", "managed", "coaching",
    
    # Context phrases
    "huấn luyện tại việt nam", "làm việc tại việt nam",
    "được bổ nhiệm", "ký hợp đồng",
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

# Prefixes to skip when following links (including media files)
SKIP_PREFIXES: List[str] = [
    "Wikipedia:",
    "Thể loại:",
    "Category:",
    "File:",
    "Tập tin:",
    "Image:",
    "Hình:",
    "Media:",
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
    "Module:",
    "Mô-đun:",
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

# ============================================================================
# COMPREHENSIVE KEYWORD FILTERING SYSTEM
# ============================================================================

# Keywords to INCLUDE - pages with these keywords are highly relevant
# Covers: Players, Coaches, Clubs, Tournaments, Positions, Vietnamese context
INCLUDE_KEYWORDS: List[str] = [
    # Core football terms
    "bóng đá", "bóng_đá", "football", "soccer",
    
    # Player roles and positions
    "cầu thủ", "cầu_thủ", "vận động viên",
    "tiền vệ", "tiền_vệ", "midfielder",
    "tiền đạo", "tiền_đạo", "striker", "forward",
    "hậu vệ", "hậu_vệ", "defender",
    "thủ môn", "thủ_môn", "goalkeeper",
    "trung vệ", "biên vệ", "tiền vệ phòng ngự", "tiền vệ tấn công",
    
    # Coaching and management (including foreign coaches in Vietnam)
    "huấn luyện viên", "huấn_luyện_viên", "hlv", "coach", "manager",
    "huấn luyện viên trưởng", "hlv trưởng", "head coach",
    "trợ lý huấn luyện viên", "trợ_lý", "assistant coach",
    "giám đốc kỹ thuật", "giám_đốc_kỹ_thuật", "technical director",
    "trọng tài", "trọng_tài", "referee",
    "chủ tịch câu lạc bộ", "chủ_tịch",
    
    # Foreign coaches working in Vietnam
    "dẫn dắt", "dẫn_dắt", "leading", "managing",
    "huấn luyện tại việt nam", "huấn_luyện_tại_việt_nam",
    "làm việc tại việt nam", "làm_việc_tại_việt_nam",
    "ký hợp đồng với", "ký_hợp_đồng", "signed with",
    "được bổ nhiệm", "được_bổ_nhiệm", "appointed",
    "chiến lược gia", "chiến_lược_gia", "tactician",
    "nhà cầm quân", "nhà_cầm_quân",
    "thầy park", "hlv park", "park hang-seo", "park hang seo",
    
    # Clubs and teams
    "câu lạc bộ", "câu_lạc_bộ", "clb", "c.l.b", "club", "fc", "f.c",
    "câu lạc bộ bóng đá", "câu_lạc_bộ_bóng_đá",
    "đội bóng", "đội_bóng", "team",
    "đội tuyển", "đội_tuyển", "national team",
    "đội u23", "u23", "u20", "u19", "u17", "u16",
    
    # Leagues and tournaments
    "v.league", "v-league", "v league", "v_league",
    "giải bóng", "giải_bóng", "giải đấu", "giải_đấu",
    "afc", "aff cup", "aff_cup", "sea games", "sea_games",
    "asian cup", "asian_cup", "world cup", "world_cup",
    "champions league", "uefa", "copa",
    "hạng nhất", "hạng_nhất", "hạng nhì", "hạng_nhì",
    
    # Vietnamese context (high priority)
    "việt nam", "việt_nam", "vietnamese", "vietnam",
    "người việt", "người_việt",
    "quốc tịch việt nam", "quốc_tịch_việt_nam",
    "gốc việt", "gốc_việt", "vietnamese descent",
    "việt kiều", "việt_kiều", "overseas vietnamese",
    "nhập tịch", "nhập_tịch", "naturalized",
    "việt nam tại", "việt_nam_tại",
    "hải ngoại", "hải_ngoại",
    
    # Career and statistics
    "sự nghiệp", "sự_nghiệp", "career",
    "thành tích", "thành_tích", "achievement",
    "danh hiệu", "danh_hiệu", "title", "trophy",
    "bàn thắng", "bàn_thắng", "goal",
    "kiến tạo", "kiến_tạo", "assist",
    
    # ===== ENHANCED PERSON DETECTION KEYWORDS =====
    # Biographical indicators
    "sinh năm", "sinh ngày", "sinh tại", "sinh ra", "sinh ra tại",
    "quê quán", "quê ở", "quê tại",
    "cao", "chiều cao", "nặng", "cân nặng",
    "tuổi", "năm nay",
    "đang khoác áo", "đang chơi",
    "born", "born in", "born on", "born at",
    "age", "years old", "year old",
    "height", "weight",
    "currently plays", "currently playing", "currently manages",
    
    # Women's football
    "cầu thủ nữ", "tuyển thủ nữ", "danh thủ nữ",
    "huấn luyện viên nữ", "hlv nữ",
    "bóng đá nữ", "đội tuyển nữ",
    "women's football", "women's soccer", "women footballer",
    "female player", "female footballer", "female coach",
    "women's national team", "women's team",
    "ladies football", "ladies team",
    
    # Career stage - Active
    "đang chơi", "thi đấu tại",
    "gia nhập", "chuyển đến",
    "được cho mượn", "mượn đến",
    "ra mắt", "lần đầu ra sân", "lần đầu tiên",
    "khoác áo số", "mang áo số",
    "plays for", "playing for", "signed for",
    "joined", "transferred to", "loaned to",
    "debuted", "debut", "first appearance",
    "wears number", "shirt number",
    
    # Career stage - Former/Retired
    "cựu cầu thủ", "cựu tuyển thủ", "cựu danh thủ",
    "từng thi đấu", "từng khoác áo", "từng chơi",
    "đã giải nghệ", "treo giày",
    "kết thúc sự nghiệp", "nghỉ thi đấu",
    "ngôi sao một thời", "huyền thoại",
    "former player", "former footballer", "former soccer player",
    "retired player", "retired footballer",
    "ex-player", "ex-footballer",
    "used to play", "played for",
    "ended career", "retired from",
    "legend", "legendary",
    
    # Position-specific (natural phrases)
    "chơi ở vị trí", "thi đấu ở vị trí", "đá ở vị trí",
    "tiền đạo cắm", "tiền đạo lùi", "tiền đạo biên",
    "tiền vệ trung tâm", "tiền vệ tấn công", "tiền vệ phòng ngự",
    "tiền vệ cánh", "tiền vệ trụ",
    "hậu vệ trái", "hậu vệ phải", "hậu vệ cánh",
    "hậu vệ biên", "hậu vệ quét",
    "thủ thành",
    "plays as a", "plays as", "playing as",
    "position as", "positioned as",
    "center forward", "second striker", "winger",
    "attacking midfielder", "central midfielder", "defensive midfielder",
    "left back", "right back", "fullback", "wing back",
    "center back", "centre back", "sweeper",
    "keeper",
    
    # National team
    "tuyển thủ", "tuyển thủ quốc gia",
    "khoác áo đội tuyển", "mặc áo đội tuyển",
    "được triệu tập", "lên tuyển", "vào tuyển",
    "ra mắt đội tuyển", "debut đội tuyển",
    "ghi bàn cho đội tuyển", "lập công cho đội tuyển",
    "đội phó", "thủ quân",
    "vua phá lưới",
    "quả bóng vàng", "chiếc giày vàng",
    "international", "international player",
    "national squad",
    "capped", "caps", "cap",
    "international caps", "international goals",
    "called up", "selected for", "named in",
    "represented", "represents",
    "vice-captain", "skipper",
    "top scorer", "golden boot", "golden ball",
    
    # Coaching-specific (enhanced)
    "huấn luyện", "dẫn dắt đội", "điều hành",
    "chỉ đạo", "phương pháp huấn luyện",
    "triết lý bóng đá", "phong cách huấn luyện",
    "được bổ nhiệm làm", "nhận nhiệm vụ",
    "thay thế", "kế nhiệm",
    "từ chức", "bị sa thải", "bị cách chức",
    "gia hạn hợp đồng", "hết hợp đồng",
    "thành tích huấn luyện",
    "coaching career", "managerial career",
    "appointed manager", "appointed coach", "appointed as",
    "took charge", "took over", "took control",
    "succeeded", "replaced",
    "resigned", "sacked", "dismissed", "fired",
    "contract extension", "contract expired",
    "tactics", "philosophy", "style",
    
    # Statistics & achievements
    "ghi được", "lập công", "ghi tên",
    "kiến tạo bàn thắng", "hỗ trợ",
    "đá chính", "ra sân chính", "xuất phát",
    "dự bị", "vào sân", "thay người",
    "số trận", "trận đấu",
    "thi đấu", "trận", "ghi",
    "vô địch", "á quân", "hạng ba",
    "giành cúp", "đoạt cúp", "nâng cúp",
    "đoạt danh hiệu", "giành danh hiệu",
    "giải thưởng", "danh hiệu cá nhân",
    "scored", "goals", "goal", "strike",
    "assists", "assist", "assisted",
    "appearances", "appearance", "matches", "games",
    "started", "starts", "starting",
    "substitute", "came on", "subbed on",
    "champion", "championship", "winner",
    "runner-up", "third place",
    "trophy", "cup", "title",
    "award", "awards", "accolade", "honor", "honour",
    "player of", "best player",
    
    # Youth & development
    "lò đào tạo", "học viện", "học viện bóng đá",
    "đội trẻ", "đội u19", "đội u21", "đội u23",
    "đội trẻ quốc gia", "đội tuyển trẻ",
    "tài năng trẻ", "triển vọng", "sao mai",
    "được đào tạo tại", "đào tạo ở",
    "lên đội một", "thăng hạng", "thăng tiến",
    "cầu thủ trẻ", "cầu thủ trẻ triển vọng",
    "youth academy", "youth team", "youth career",
    "academy", "academy player",
    "trained at", "came through", "came up through",
    "promoted to", "promotion",
    "young player", "youngster",
    "prospect", "promising", "talent",
    "under-19", "under-21", "under-23",
    
    # Professional status
    "chuyên nghiệp", "bán chuyên", "nghiệp dư",
    "chuyển sang chuyên nghiệp",
    "hợp đồng chuyên nghiệp",
    "cầu thủ chuyên nghiệp",
    "sự nghiệp chuyên nghiệp",
    "professional", "professional player",
    "professional footballer", "professional career",
    "semi-professional", "semi-pro",
    "amateur", "amateur career",
    "turned professional", "went professional",
    "signed professional", "professional contract",
]

# Legacy KEEP_KEYWORDS for backward compatibility
KEEP_KEYWORDS: List[str] = INCLUDE_KEYWORDS

# Priority keywords - pages with these should be crawled first/always
PRIORITY_KEYWORDS: List[str] = [
    "v.league 1", "v.league_1",
    "đội tuyển bóng đá quốc gia việt nam",
    "câu lạc bộ bóng đá hà nội",
    "nguyễn quang hải",
    "park hang-seo", "park hang seo",  # Famous foreign coach
]

# Keywords to EXCLUDE - pages with these should be skipped
# Covers: Geography, Politics, History, Other sports, Media, Administrative
EXCLUDE_KEYWORDS: List[str] = [
    # Geographic and administrative divisions
    "đô thị", "đô_thị", "urban",
    "tỉnh", "province",
    "thành phố", "thành_phố", "city",
    "vùng", "region",
    "quận", "district",
    "huyện", "county",
    "phường", "ward",
    "xã", "commune", "village",
    "thị trấn", "thị_trấn", "town",
    "thị xã", "thị_xã",
    "khu vực", "khu_vực", "area",
    "miền", "vùng miền",
    
    # History, politics, culture (non-sport)
    "lịch sử", "lịch_sử", "history",
    "lịch sử việt nam", "lịch_sử_việt_nam",
    "kinh tế", "kinh_tế", "economy", "economic",
    "văn hóa", "văn_hóa", "culture", "cultural",
    "chính trị", "chính_trị", "politics", "political",
    "tôn giáo", "tôn_giáo", "religion", "religious",
    "giáo dục", "giáo_dục", "education",
    "triết học", "triết_học", "philosophy",
    "khoa học", "khoa_học", "science",
    "công nghệ", "công_nghệ", "technology",
    "y học", "y_học", "medicine", "medical",
    
    # Geography (natural features)
    "địa lý", "địa_lý", "geography",
    "sông", "river",
    "núi", "mountain",
    "biển", "sea", "ocean",
    "vịnh", "bay", "gulf",
    "hồ", "lake",
    "đảo", "island",
    "bán đảo", "bán_đảo", "peninsula",
    "di sản", "di_sản", "heritage",
    "danh lam", "danh_lam",
    
    # Lists and categories (usually not person pages)
    "danh sách", "danh_sách", "list of",
    "thể loại", "thể_loại", "category",
    "bảng", "table",
    "niên biểu", "niên_biểu", "timeline",
    "thống kê", "thống_kê", "statistics",
    
    # Other sports (non-football)
    "bóng rổ", "bóng_rổ", "basketball",
    "cầu lông", "cầu_lông", "badminton",
    "tennis", "quần vợt", "quần_vợt",
    "bơi lội", "bơi_lội", "swimming",
    "điền kinh", "điền_kinh", "athletics", "track and field",
    "võ thuật", "võ_thuật", "martial arts",
    "boxing", "quyền anh", "quyền_anh",
    "bóng chuyền", "bóng_chuyền", "volleyball",
    "cầu mây", "cầu_mây", "sepak takraw",
    "đua xe", "đua_xe", "racing",
    "golf",
    "cricket",
    "rugby",
    "hockey",
    
    # Entertainment and media
    "phim", "film", "movie", "cinema",
    "ca sĩ", "ca_sĩ", "singer",
    "diễn viên", "diễn_viên", "actor", "actress",
    "nghệ sĩ", "nghệ_sĩ", "artist",
    "nhạc sĩ", "nhạc_sĩ", "musician",
    "đạo diễn", "đạo_diễn", "director",
    "truyền hình", "truyền_hình", "television",
    "âm nhạc", "âm_nhạc", "music",
    
    # Military and war
    "quân đội", "quân_đội", "military", "army",
    "chiến tranh", "chiến_tranh", "war",
    "trận đánh", "trận_đánh", "battle",
    "tướng", "general",
    
    # Business and organizations (non-sport)
    "công ty", "công_ty", "company",
    "tập đoàn", "tập_đoàn", "corporation",
    "ngân hàng", "ngân_hàng", "bank",
    
    # Events (non-sport)
    "lễ hội", "lễ_hội", "festival",
    "hội nghị", "hội_nghị", "conference",
    
    # Misc irrelevant
    "thần thoại", "thần_thoại", "mythology",
    "truyền thuyết", "truyền_thuyết", "legend",
    "văn học", "văn_học", "literature",
]

# Legacy DROP_KEYWORDS for backward compatibility
DROP_KEYWORDS: List[str] = EXCLUDE_KEYWORDS

# ============================================================================
# Relevance Scoring System (Smart Enrichment)
# ============================================================================

# Weights for different signals in relevance scoring
# Higher weight = more important for determining if a page is relevant
RELEVANCE_WEIGHTS: Dict[str, int] = {
    "keyword_match": 3,           # Page title/content matches INCLUDE_KEYWORDS
    "infobox_valid": 3,            # Has valid football-related infobox (increased)
    "category_valid": 3,           # Belongs to valid football categories (increased)
    "contextual_text": 3,          # Lead paragraph contains football context (increased)
    "linked_by_core": 1,           # Linked from a high-quality core node
    "blacklist_hit": -4,           # Matches noise/blacklist patterns (increased penalty)
    "file_page": -5,               # Is a media/file page
    "exclude_keyword_hit": -3,     # Contains EXCLUDE_KEYWORDS (increased penalty)
}

# Filter toggles - enable/disable specific filtering strategies
ACTIVE_FILTERS: Dict[str, bool] = {
    "keyword_filter": True,        # Use INCLUDE/EXCLUDE keyword matching
    "semantic_filter": True,       # Use semantic pattern matching in text
    "category_filter": True,       # Validate Wikipedia categories
    "infobox_filter": True,        # Validate infobox types
    "neighbor_filter": True,       # Consider quality of linking pages
    "graph_filter": True,          # Use graph metrics (degree, distance)
    "ner_filter": False,           # Use NER (requires underthesea/spaCy)
}

# Relevance score thresholds
RELEVANCE_SCORE_THRESHOLD_CORE = 5      # Minimum score for "core" layer (expand links)
RELEVANCE_SCORE_THRESHOLD_CONTEXT = 2   # Minimum score for "context" layer (keep but don't expand)

# Graph-based filtering parameters
MAX_ALLOWED_DISTANCE = 6         # Maximum distance from seed node
MIN_NODE_DEGREE = 2              # Minimum connections to keep a node

# ============================================================================
# Semantic Context Detection
# ============================================================================

# Regex patterns to identify football-related content in lead paragraphs
# These help detect football entities even when title lacks clear keywords
SEMANTIC_PATTERNS: List[str] = [
    # Vietnamese patterns - Players
    r"là cầu thủ bóng đá",
    r"là một cầu thủ",
    r"thi đấu cho",
    r"chơi cho",
    r"khoác áo",
    r"gia nhập",
    r"chuyển đến",
    r"vị trí.*(?:tiền đạo|tiền vệ|hậu vệ|thủ môn)",
    
    # Vietnamese patterns - Coaches (including foreign coaches)
    r"là huấn luyện viên bóng đá",
    r"là một huấn luyện viên",
    r"là hlv",
    r"huấn luyện.*đội",
    r"dẫn dắt.*đội",
    r"dẫn dắt.*(?:câu lạc bộ|clb|đội tuyển)",
    r"được bổ nhiệm.*(?:huấn luyện viên|hlv)",
    r"ký hợp đồng.*(?:huấn luyện viên|hlv)",
    r"làm việc tại việt nam",
    r"huấn luyện tại việt nam",
    r"nhà cầm quân",
    r"chiến lược gia",
    
    # Common patterns
    r"đội tuyển quốc gia",
    r"đội tuyển",
    r"đội bóng",
    r"câu lạc bộ",
    
    # English patterns - Players
    r"football player",
    r"soccer player",
    r"plays for",
    r"played for",
    r"position.*(?:striker|midfielder|defender|goalkeeper)",
    
    # English patterns - Coaches (for foreign coaches)
    r"football coach",
    r"football manager",
    r"head coach",
    r"assistant coach",
    r"manages",
    r"managed",
    r"coaching",
    r"appointed.*coach",
    r"signed.*coach",
    r"working in vietnam",
    r"coaching in vietnam",
    
    # Common English patterns
    r"national team",
    r"football club",
    
    # ===== ENHANCED PERSON DETECTION PATTERNS =====
    # Biographical patterns - Vietnamese
    r"sinh năm \d{4}",
    r"sinh ngày \d{1,2}",
    r"sinh tại [A-ZĐÂĂÊÔƠƯ][a-zđâăêôơư\s]+",
    r"sinh ra (?:tại|ở) [A-ZĐÂĂÊÔƠƯ]",
    r"quê quán [A-ZĐÂĂÊÔƠƯ][a-zđâăêôơư\s]+",
    r"quê ở [A-ZĐÂĂÊÔƠƯ][a-zđâăêôơư\s]+",
    r"cao \d+[.,]?\d* m",
    r"cao \d+ cm",
    r"nặng \d+ kg",
    r"chiều cao \d+[.,]?\d* m",
    r"\d+ tuổi",
    r"hiện tại \d+ tuổi",
    r"năm nay \d+ tuổi",
    
    # Biographical patterns - English
    r"born \d{1,2} [A-Z][a-z]+ \d{4}",
    r"born in \d{4}",
    r"born in [A-Z][a-z]+",
    r"born on \d{1,2} [A-Z][a-z]+",
    r"\d+ years old",
    r"age \d+",
    r"aged \d+",
    r"height.*\d+.*cm",
    r"height.*\d+[.,]\d+.*m",
    
    # Career patterns - Vietnamese
    r"là (?:một )?vận động viên bóng đá",
    r"đang khoác áo [A-ZĐÂĂÊÔƠƯ]",
    r"thi đấu ở vị trí [a-zđâăêôơư\s]+",
    r"đá ở vị trí [a-zđâăêôơư\s]+",
    r"cựu (?:cầu thủ|tuyển thủ|danh thủ)",
    r"từng (?:thi đấu|khoác áo|chơi)",
    r"đã giải nghệ",
    r"giải nghệ năm \d{4}",
    r"dẫn dắt (?:đội|câu lạc bộ|clb)",
    r"huấn luyện (?:đội|câu lạc bộ)",
    
    # Career patterns - English
    r"is a (?:professional )?(?:football|soccer) player",
    r"is a (?:professional )?footballer",
    r"plays (?:for|as a) [A-Z]",
    r"currently plays (?:for|as)",
    r"playing for [A-Z]",
    r"former (?:player|footballer)",
    r"retired (?:player|footballer)",
    r"ex-(?:player|footballer)",
    r"used to play",
    r"retired in \d{4}",
    r"is a (?:football|soccer) (?:coach|manager)",
    r"(?:manages|managed) [A-Z]",
    r"coaching career",
    r"managerial career",
    r"appointed (?:coach|manager)",
    
    # National team patterns - Vietnamese
    r"tuyển thủ (?:quốc gia )?việt nam",
    r"khoác áo đội tuyển",
    r"được triệu tập (?:lên|vào) đội tuyển",
    r"ra mắt đội tuyển",
    r"ghi bàn cho đội tuyển",
    r"đội trưởng đội tuyển",
    r"thi đấu cho đội tuyển",
    
    # National team patterns - English
    r"(?:plays|played) for (?:the )?(?:Vietnam|Vietnamese) national team",
    r"(?:Vietnam|Vietnamese) international",
    r"\d+ caps for (?:Vietnam|Vietnamese)",
    r"represented (?:Vietnam|Vietnamese)",
    r"national team debut",
    r"international debut",
    r"capped \d+ times",
    
    # Diaspora & naturalization patterns - Vietnamese
    r"(?:người|cầu thủ) việt kiều",
    r"sinh (?:ra )?ở [A-Z][a-z]+.*(?:cha|mẹ|bố|mẹ|ông|bà).*việt",
    r"gốc việt(?:.*sinh.*[A-Z][a-z]+)?",
    r"có nguồn gốc việt",
    r"có dòng máu việt",
    r"nhập tịch việt nam",
    r"(?:có|mang) hai quốc tịch",
    r"chọn khoác áo (?:đội tuyển )?việt nam",
    r"đủ điều kiện thi đấu cho việt nam",
    
    # Diaspora & naturalization patterns - English
    r"(?:of )?vietnamese (?:descent|heritage|origin|ancestry)",
    r"born in [A-Z][a-z]+.*vietnamese (?:parents|mother|father)",
    r"(?:parents|mother|father) from vietnam",
    r"vietnamese (?:roots|background)",
    r"naturalized vietnamese",
    r"dual (?:citizen|nationality).*vietnam",
    r"eligible (?:to play )?for vietnam",
    r"chose to represent vietnam",
    
    # Statistics & achievements patterns - Vietnamese
    r"ghi (?:được )?\d+ bàn",
    r"có \d+ kiến tạo",
    r"thi đấu \d+ trận",
    r"ra sân \d+ lần",
    r"vô địch [A-ZĐÂĂÊÔƠƯ]",
    r"giành (?:cúp|danh hiệu) [A-ZĐÂĂÊÔƠƯ]",
    
    # Statistics & achievements patterns - English
    r"scored \d+ goals?",
    r"\d+ goals? (?:in|for)",
    r"\d+ assists?",
    r"\d+ appearances?",
    r"(?:won|winner of) (?:the )?[A-Z]",
    r"champion of [A-Z]",
]

# ============================================================================
# Infobox & Category Validation
# ============================================================================

# Valid infobox types that indicate football-related pages
VALID_INFOBOX_TYPES: List[str] = [
    "infobox football biography",
    "infobox sportsperson",
    "infobox football manager",
    "infobox football club",
    "infobox club",
    "infobox national football team",
    "infobox football tournament",
    "infobox football league",
]

# Valid Wikipedia categories for football domain
VALID_CATEGORIES: List[str] = [
    "cầu thủ bóng đá",
    "huấn luyện viên bóng đá",
    "đội tuyển bóng đá",
    "câu lạc bộ bóng đá",
    "v.league",
    "thể thao việt nam",
    "bóng đá việt nam",
    "giải bóng đá",
    "football players",
    "football managers",
    "football clubs",
    "national football teams",
]

# ============================================================================
# NER-based Entity Validation (Optional)
# ============================================================================

# Entity types to validate (requires underthesea or spaCy)
NER_ENTITY_TYPES: List[str] = ["PERSON", "ORG"]
NER_SCORE_WEIGHT: int = 2  # Bonus score if valid entities detected

# ============================================================================
# Noise Page Filtering
# ============================================================================

# Blacklist patterns for noise pages (lists, meta pages, etc.)
NOISE_PAGE_TITLES: List[str] = [
    "danh sách cầu thủ",
    "danh sách huấn luyện viên",
    "danh sách đội bóng",
    "danh sách câu lạc bộ",
    "danh sách giải đấu",
    "thể loại:",
    "wikipedia:",
    "trang định hướng",
    "bản mẫu:",
    "thảo luận:",
    "list of players",
    "list of coaches",
    "list of clubs",
    "disambiguation",
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
