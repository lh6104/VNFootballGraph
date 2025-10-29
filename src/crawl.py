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

logger = logging.getLogger(__name__)


class WikiCrawler:
    """Crawls Vietnamese Wikipedia pages with depth control."""
    
    def __init__(self, max_depth: int = config.DEFAULT_MAX_DEPTH):
        """
        Initialize the crawler.
        
        Args:
            max_depth: Maximum depth to crawl from seed page
        """
        self.max_depth = max_depth
        self.visited: Set[str] = set()
        self.page_tree = {}  # Store parent-child relationships: {child: parent}
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
        
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
                if depth < self.max_depth:
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
            
            # Build page data WITHOUT storing html/soup (memory efficient)
            page_data = {
                'title': page_title,
                'url': url,
                'infobox': infobox,
                'links': links,
                'categories': categories,
                'first_paragraph': first_para,  # For entity detection
                'infobox_text': infobox_text,   # For entity detection
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
        Check if a link should be skipped using smart filtering strategy.
        
        Args:
            page_title: Wikipedia page title
            
        Returns:
            True if link should be skipped
        """
        # Check skip prefixes (highest priority)
        for prefix in config.SKIP_PREFIXES:
            if page_title.startswith(prefix):
                return True
        
        page_lower = page_title.lower().replace('_', ' ')
        
        # Check DROP keywords - skip if found
        for keyword in config.DROP_KEYWORDS:
            if keyword in page_lower:
                logger.debug(f"Skipping {page_title}: contains DROP keyword '{keyword}'")
                return True
        
        # Check skip URL keywords
        for keyword in config.SKIP_URL_KEYWORDS:
            if keyword in page_lower:
                return True
        
        # Check PRIORITY keywords - never skip
        for keyword in config.PRIORITY_KEYWORDS:
            if keyword in page_lower:
                logger.debug(f"Keeping {page_title}: contains PRIORITY keyword '{keyword}'")
                return False
        
        # Check KEEP keywords - keep if found
        for keyword in config.KEEP_KEYWORDS:
            if keyword in page_lower:
                return False
        
        # If no KEEP keyword found, skip (conservative approach)
        # Comment this out if you want to crawl everything not in DROP list
        # logger.debug(f"Skipping {page_title}: no KEEP keyword found")
        # return True
        
        # Default: don't skip (liberal approach)
        return False
    
    def get_page_type(self, page_data: Dict) -> Optional[str]:
        """
        Determine the type of entity from page data.
        
        Args:
            page_data: Page data dictionary
            
        Returns:
            Entity type ('player', 'coach', 'club', 'national_team') or None
        """
        title = page_data.get('title', '').lower()
        categories = [c.lower() for c in page_data.get('categories', [])]
        
        # Get infobox text (now pre-extracted)
        infobox_text = page_data.get('infobox_text', '').lower()
        
        # Get first paragraph text (now pre-extracted)
        first_para = page_data.get('first_paragraph', '').lower()
        
        # Combine all text sources for keyword matching
        text = title + ' ' + ' '.join(categories) + ' ' + infobox_text + ' ' + first_para
        
        # Check for player
        if any(keyword in text for keyword in config.PLAYER_KEYWORDS):
            return 'player'
        
        # Check for coach
        if any(keyword in text for keyword in config.COACH_KEYWORDS):
            return 'coach'
        
        # Check for club
        if any(keyword in text for keyword in config.CLUB_KEYWORDS):
            return 'club'
        
        # Check for national team
        if any(keyword in text for keyword in config.NATIONAL_TEAM_KEYWORDS):
            return 'national_team'
        
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
