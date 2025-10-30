"""
Wikipedia crawler module for Vietnamese football pages.
Handles page fetching, link extraction, and depth-limited crawling.
"""

import time
import logging
from typing import Set, List, Dict, Optional, Tuple
from urllib.parse import unquote, urljoin
import requests
from bs4 import BeautifulSoup

from . import config
from .filters_advanced import AdvancedFilter

logger = logging.getLogger(__name__)


class WikiCrawler:
    """Crawls Vietnamese Wikipedia pages with depth control."""
    
    def __init__(self, max_depth: int = config.DEFAULT_MAX_DEPTH, use_advanced_filter: bool = True):
        """
        Initialize the crawler.
        
        Args:
            max_depth: Maximum depth to crawl from seed page
            use_advanced_filter: Use advanced relevance scoring filter
        """
        self.max_depth = max_depth
        self.visited: Set[str] = set()
        self.page_tree = {}  # Store parent-child relationships: {child: parent}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
        
        # Advanced filtering
        self.use_advanced_filter = use_advanced_filter
        self.advanced_filter = AdvancedFilter() if use_advanced_filter else None
        self.node_layers = {}  # Track node layers: {page_title: "core"|"context"|"skip"}
        self.node_scores = {}  # Track relevance scores: {page_title: score}
        
    def crawl(self, seed_page: str):
        """
        Crawl from seed page up to max_depth using generator pattern.
        Yields pages one at a time to reduce memory usage.
        
        Args:
            seed_page: Starting Wikipedia page title
            
        Yields:
            Dict: Page data dictionary for each crawled page
        """
        logger.info(f"Starting crawl from seed: {seed_page}, max_depth: {self.max_depth}")
        
        # Mark seed page as CORE to ensure it's always processed
        if self.use_advanced_filter:
            self.node_layers[seed_page] = "core"
            self.advanced_filter.core_nodes.add(seed_page)
            logger.info(f"Seed page '{seed_page}' marked as CORE (always process)")
        
        queue = [(seed_page, 0)]  # (page_title, depth)
        current_depth = 0
        depth_counts = {}  # Track pages per depth
        total_pages = 0
        
        while queue:
            page_title, depth = queue.pop(0)
            
            # Log when moving to a new depth level
            if depth > current_depth:
                pages_at_depth = depth_counts.get(current_depth, 0)
                logger.info("=" * 60)
                logger.info(f"DEPTH {current_depth} COMPLETE: Crawled {pages_at_depth} pages")
                logger.info("=" * 60)
                current_depth = depth
            
            # Skip if already visited
            if page_title in self.visited:
                continue
                
            # Skip if max depth exceeded
            if depth > self.max_depth:
                continue
                
            logger.info(f"Crawling: {page_title} (depth: {depth})")
            
            # Fetch and parse page
            page_data = self.fetch_page(page_title)
            
            if page_data:
                self.visited.add(page_title)
                depth_counts[depth] = depth_counts.get(depth, 0) + 1
                total_pages += 1
                
                # Extract links before yielding (we need them for queue)
                links = page_data.get('links', [])
                
                # Add linked pages to queue if within depth limit
                # With advanced filter: only expand from "core" layer nodes
                should_expand = True
                if self.use_advanced_filter and page_title in self.node_layers:
                    layer = self.node_layers[page_title]
                    should_expand = self.advanced_filter.should_expand_links(layer)
                    if not should_expand:
                        logger.debug(f"Not expanding links from {page_title} (layer={layer})")
                
                if depth < self.max_depth and should_expand:
                    for link in links:
                        if link not in self.visited:
                            queue.append((link, depth + 1))
                            # Track parent-child relationship
                            if link not in self.page_tree:
                                self.page_tree[link] = page_title
                
                logger.info(f"Processed: {page_title} - Found {len(links)} links")
                
                # Yield page for processing (memory efficient)
                yield page_data
            else:
                logger.warning(f"Failed to fetch: {page_title}")
            
            # Rate limiting
            time.sleep(config.REQUEST_DELAY)
        
        # Log final depth completion
        if current_depth in depth_counts:
            logger.info("=" * 60)
            logger.info(f"DEPTH {current_depth} COMPLETE: Crawled {depth_counts[current_depth]} pages")
            logger.info("=" * 60)
        
        # Summary
        logger.info("=" * 60)
        logger.info("CRAWL SUMMARY:")
        for d in sorted(depth_counts.keys()):
            logger.info(f"  Depth {d}: {depth_counts[d]} pages")
        logger.info(f"  Total: {total_pages} pages")
        logger.info("=" * 60)
    
    def fetch_page(self, page_title: str) -> Optional[Dict]:
        """
        Fetch a single Wikipedia page and extract data.
        Memory-efficient: Only stores extracted data, not raw HTML/soup.
        
        Args:
            page_title: Wikipedia page title
            
        Returns:
            Dictionary with page data or None if fetch failed
        """
        url = self._build_page_url(page_title)
        
        try:
            response = self.session.get(url, timeout=config.REQUEST_TIMEOUT)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract all needed data while soup is in memory
            infobox = self._extract_infobox(soup)
            links = self._extract_links(soup)
            categories = self._extract_categories(soup)
            
            # Get page type info (needed for entity detection)
            first_para = ""
            content = soup.find('div', {'id': 'mw-content-text'})
            if content:
                para = content.find('p')
                if para:
                    first_para = para.get_text()
            
            # Get infobox text for entity type detection
            infobox_text = ""
            if infobox:
                infobox_text = infobox.get_text()
            
            # Advanced filtering: Evaluate page relevance
            relevance_score = 0
            layer = "context"  # Default layer
            
            if self.use_advanced_filter:
                # Check if already marked as CORE (e.g., seed page)
                if page_title in self.node_layers:
                    layer = self.node_layers[page_title]
                    relevance_score = 10  # High score for pre-marked pages
                    logger.debug(f"Page {page_title} already marked as {layer}")
                else:
                    infobox_type = self.advanced_filter.get_infobox_type(infobox)
                    neighbors = [self.page_tree.get(page_title, "")]  # Parent page
                    
                    relevance_score, layer = self.advanced_filter.evaluate_page(
                        title=page_title,
                        text=first_para,
                        categories=categories,
                        infobox_type=infobox_type,
                        infobox=infobox,
                        neighbors=neighbors,
                        distance_from_seed=0  # TODO: Calculate actual distance
                    )
                    
                    # Store layer and score
                    self.node_layers[page_title] = layer
                    self.node_scores[page_title] = relevance_score
                
                # Skip if layer is "skip" (but not for pre-marked pages)
                if layer == "skip":
                    logger.info(f"Skipping {page_title}: relevance score too low ({relevance_score})")
                    return None
            
            # Build page data WITHOUT storing html/soup (memory efficient)
            page_data = {
                'title': page_title,
                'url': url,
                'infobox': infobox,
                'links': links,
                'categories': categories,
                'first_paragraph': first_para,  # For entity detection
                'infobox_text': infobox_text,   # For entity detection
                'relevance_score': relevance_score,  # Advanced filtering score
                'layer': layer,  # Node layer (core/context/skip)
            }
            
            # soup and response.text are now garbage collected
            return page_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    def _build_page_url(self, page_title: str) -> str:
        """Build full Wikipedia URL from page title."""
        # URL encode the title
        encoded_title = page_title.replace(' ', '_')
        return f"{config.WIKI_PAGE_URL}{encoded_title}"
    
    def _extract_infobox(self, soup: BeautifulSoup) -> Optional[BeautifulSoup]:
        """
        Extract infobox table from page.
        
        Args:
            soup: BeautifulSoup object of page
            
        Returns:
            BeautifulSoup object of infobox or None
        """
        # Find infobox table
        infobox = soup.find('table', {'class': 'infobox'})
        
        if not infobox:
            # Try alternative class names
            infobox = soup.find('table', {'class': 'infobox vcard'})
        
        if not infobox:
            infobox = soup.find('table', class_=lambda x: x and 'infobox' in x)
        
        return infobox
    
    def _extract_links(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract internal Wikipedia links from page content.
        
        Args:
            soup: BeautifulSoup object of page
            
        Returns:
            List of linked page titles
        """
        links = []
        
        # Find main content area
        content = soup.find('div', {'id': 'mw-content-text'})
        if not content:
            return links
        
        # Extract all internal links
        for link in content.find_all('a', href=True):
            href = link['href']
            
            # Only process internal wiki links
            if not href.startswith('/wiki/'):
                continue
            
            # Extract page title from URL
            page_title = href.replace('/wiki/', '')
            page_title = unquote(page_title)
            
            # Skip if contains anchor
            if '#' in page_title:
                page_title = page_title.split('#')[0]
            
            # Skip empty titles
            if not page_title:
                continue
            
            # Filter out unwanted pages
            if self._should_skip_link(page_title):
                continue
            
            links.append(page_title)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_links = []
        for link in links:
            if link not in seen:
                seen.add(link)
                unique_links.append(link)
        
        return unique_links
    
    def _extract_categories(self, soup: BeautifulSoup) -> List[str]:
        """
        Extract categories from page.
        
        Args:
            soup: BeautifulSoup object of page
            
        Returns:
            List of category names
        """
        categories = []
        
        # Find category links
        cat_links = soup.find('div', {'id': 'mw-normal-catlinks'})
        if cat_links:
            for link in cat_links.find_all('a'):
                if link.get('href', '').startswith('/wiki/Thể_loại:'):
                    category = link.text.strip()
                    categories.append(category)
        
        return categories
    
    def _should_skip_link(self, page_title: str) -> bool:
        """
        Check if a link should be skipped using enhanced multi-tier filtering strategy.
        
        Strategy:
        1. SKIP_PREFIXES: Immediate skip (Wikipedia meta pages, media files)
        2. PRIORITY_KEYWORDS: Never skip (high-value pages)
        3. EXCLUDE_KEYWORDS: Skip if found (irrelevant topics)
        4. INCLUDE_KEYWORDS: Keep if found (relevant topics)
        5. Default: Skip if no INCLUDE keyword (conservative)
        
        Args:
            page_title: Wikipedia page title
            
        Returns:
            True if link should be skipped
        """
        # TIER 1: Check skip prefixes (highest priority - media files, meta pages)
        for prefix in config.SKIP_PREFIXES:
            if page_title.startswith(prefix):
                logger.debug(f"⛔ Skipping {page_title}: matches SKIP_PREFIX '{prefix}'")
                return True
        
        # Normalize page title for keyword matching
        page_lower = page_title.lower().replace('_', ' ')
        
        # TIER 2: Check PRIORITY keywords - never skip these (highest value)
        for keyword in config.PRIORITY_KEYWORDS:
            if keyword in page_lower:
                logger.debug(f"⭐ Keeping {page_title}: contains PRIORITY keyword '{keyword}'")
                return False
        
        # TIER 3: Check EXCLUDE keywords - skip if found (irrelevant topics)
        # Use scoring to avoid false positives (e.g., "Lịch sử câu lạc bộ" should not be skipped)
        exclude_score = 0
        exclude_matches = []
        for keyword in config.EXCLUDE_KEYWORDS:
            if keyword in page_lower:
                exclude_score += 1
                exclude_matches.append(keyword)
        
        # TIER 4: Check INCLUDE keywords - keep if found (relevant topics)
        include_score = 0
        include_matches = []
        for keyword in config.INCLUDE_KEYWORDS:
            if keyword in page_lower:
                include_score += 1
                include_matches.append(keyword)
        
        # TIER 5: Check skip URL keywords (disambiguation pages)
        for keyword in config.SKIP_URL_KEYWORDS:
            if keyword in page_lower:
                logger.debug(f"⛔ Skipping {page_title}: contains SKIP_URL keyword '{keyword}'")
                return True
        
        # Decision logic: Compare INCLUDE vs EXCLUDE scores
        # If INCLUDE score > EXCLUDE score: Keep (relevant)
        # If EXCLUDE score > INCLUDE score: Skip (irrelevant)
        # If tied or no matches: Use conservative approach (skip)
        
        if include_score > 0 and exclude_score > 0:
            # Both found - compare scores
            if include_score > exclude_score:
                logger.debug(f"✅ Keeping {page_title}: INCLUDE({include_score}) > EXCLUDE({exclude_score})")
                return False
            else:
                logger.debug(f"⛔ Skipping {page_title}: EXCLUDE({exclude_score}) >= INCLUDE({include_score})")
                return True
        elif include_score > 0:
            # Only INCLUDE keywords found - keep
            logger.debug(f"✅ Keeping {page_title}: contains INCLUDE keywords {include_matches[:3]}")
            return False
        elif exclude_score > 0:
            # Only EXCLUDE keywords found - skip
            logger.debug(f"⛔ Skipping {page_title}: contains EXCLUDE keywords {exclude_matches[:3]}")
            return True
        else:
            # No keywords found - conservative approach: skip
            # This prevents crawling completely irrelevant pages
            logger.debug(f"⚠️  Skipping {page_title}: no INCLUDE/EXCLUDE keywords found (conservative)")
            return True
    
    def get_page_type(self, page_data: Dict) -> Optional[str]:
        """
        Determine the type of entity from page data.
        
        Args:
            page_data: Page data dictionary
            
        Returns:
            Entity type ('player', 'coach', 'club', 'national_team') or None
        """
        title = page_data.get('title', '').lower().replace('_', ' ')  # Normalize underscores
        categories = [c.lower() for c in page_data.get('categories', [])]
        
        # Get infobox text (now pre-extracted)
        infobox_text = page_data.get('infobox_text', '').lower()
        
        # Get first paragraph text (now pre-extracted)
        first_para = page_data.get('first_paragraph', '').lower()
        
        # Combine all text sources for keyword matching
        text = title + ' ' + ' '.join(categories) + ' ' + infobox_text + ' ' + first_para
        
        # EXCLUSION RULES - Skip non-person pages
        
        # 1. Skip pure position pages (e.g., "Tiền_đạo_(bóng_đá)")
        # These have position name + "(bóng_đá)" pattern
        if "_(bóng_đá)" in page_data.get('title', ''):
            position_terms = ["tiền_vệ", "tiền_đạo", "hậu_vệ", "thủ_môn", "trung_vệ"]
            if any(pos in page_data.get('title', '').lower() for pos in position_terms):
                logger.debug(f"Skipping position concept page: {title}")
                return None
        
        # 2. Skip organizations/institutions/tournaments
        org_indicators = [
            "trung_tâm", "trung tâm", "center", "academy",
            "quỹ", "fund", "foundation",
            "giải_thưởng", "giải thưởng", "award", "prize",
            "chiếc_giày", "golden boot", "golden ball"
        ]
        if any(org in title for org in org_indicators):
            logger.debug(f"Skipping organization/award page: {title}")
            return None
        
        # 2b. Skip tournaments/competitions
        tournament_indicators = [
            "giải bóng đá", "giải vô địch", "giải u-", "giải u21", "giải u23",
            "vòng loại", "vòng chung kết", "vòng bảng",
            "cup", "championship", "tournament",
            "aff cup", "sea games", "asian games",
            "world cup", "fifa"
        ]
        # Exception: Don't skip if it's a person name with tournament in disambiguation
        # e.g., "Nguyễn_Văn_A_(cầu_thủ_tại_World_Cup_2022)"
        has_person_name_tournament = any(name_part in title for name_part in ["nguyễn", "trần", "lê", "phạm", "hoàng", "phan", "vũ", "đặng", "bùi", "đỗ", "hồ", "cao"])
        
        if any(tournament in title for tournament in tournament_indicators) and not has_person_name_tournament:
            logger.debug(f"Skipping tournament/competition page: {title}")
            return None
        
        # 3. Skip position pages (general check)
        position_indicators = [
            "tiền vệ", "tiền đạo", "hậu vệ", "thủ môn",
            "midfielder", "forward", "striker", "defender", "goalkeeper",
            "vị trí", "position"
        ]
        # Exception: If it's a person page with position in name (e.g., "Bùi_Tiến_Dũng_(thủ_môn)")
        # Check if it has person name pattern (Vietnamese name + disambiguation)
        has_person_name = any(name_part in title for name_part in ["nguyễn", "trần", "lê", "phạm", "hoàng", "phan", "vũ", "đặng", "bùi", "đỗ", "hồ", "cao"])
        has_disambiguation = '(' in page_data.get('title', '') and ')' in page_data.get('title', '')
        is_person_with_position = has_person_name and has_disambiguation
        
        if any(pos in title for pos in position_indicators) and not is_person_with_position:
            logger.debug(f"Skipping position page: {title}")
            return None
        
        # Skip team/club pages when checking for individuals
        team_indicators = ["đội tuyển", "national team", "câu lạc bộ", "football club"]
        if any(team in title for team in team_indicators):
            # This is a team/club, not a person
            if "câu lạc bộ" in title or "football club" in title:
                return 'club'
            elif "đội tuyển" in title or "national team" in title:
                return 'national_team'
            return None
        
        # PERSON DETECTION - Must have biographical indicators
        person_indicators = [
            # Vietnamese
            "sinh năm", "sinh ngày", "sinh tại", "sinh ra",
            "là cầu thủ", "là huấn luyện viên", "là một cầu thủ", "là một huấn luyện viên",
            "người việt nam", "người hàn quốc", "người pháp", "người nhật",
            # English
            "born", "born in", "born on",
            "is a player", "is a footballer", "is a coach", "is a manager",
            "football player", "football coach", "football manager",
            "soccer player", "soccer coach",
            "vietnamese", "korean", "french", "japanese", "thai"
        ]
        is_person = any(indicator in first_para for indicator in person_indicators)
        
        if not is_person:
            # Not a person page, might be concept/position/tournament
            logger.debug(f"Not a person page: {title}")
            return None
        
        # Now check specific types for PERSON pages only
        # Check for player
        if any(keyword in text for keyword in config.PLAYER_KEYWORDS):
            # Additional validation: should NOT be a coach
            if "huấn luyện viên" not in first_para and "coach" not in first_para:
                return 'player'
        
        # Check for coach
        if any(keyword in text for keyword in config.COACH_KEYWORDS):
            return 'coach'
        
        return None
    
    def is_vietnamese_diaspora(self, page_data: Dict) -> bool:
        """
        Check if a player is Vietnamese diaspora, naturalized, or of Vietnamese descent.
        
        Args:
            page_data: Page data dictionary
            
        Returns:
            True if player is Vietnamese diaspora/naturalized/Vietnamese descent
        """
        title = page_data.get('title', '').lower()
        categories = [c.lower() for c in page_data.get('categories', [])]
        
        # Get page content text (now pre-extracted)
        first_para = page_data.get('first_paragraph', '').lower()
        infobox_text = page_data.get('infobox_text', '').lower()
        
        # Combine all text sources
        full_text = title + ' ' + ' '.join(categories) + ' ' + first_para + ' ' + infobox_text
        
        # Check for Vietnamese diaspora keywords
        return any(keyword in full_text for keyword in config.VIETNAMESE_DIASPORA_KEYWORDS)
