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
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': config.USER_AGENT
        })
        
    def crawl(self, seed_page: str) -> List[Dict]:
        """
        Crawl from seed page up to max_depth.
        
        Args:
            seed_page: Starting Wikipedia page title
            
        Returns:
            List of page data dictionaries
        """
        logger.info(f"Starting crawl from seed: {seed_page}, max_depth: {self.max_depth}")
        
        pages_data = []
        queue = [(seed_page, 0)]  # (page_title, depth)
        
        while queue:
            page_title, depth = queue.pop(0)
            
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
                pages_data.append(page_data)
                
                # Add linked pages to queue if within depth limit
                if depth < self.max_depth:
                    for link in page_data.get('links', []):
                        if link not in self.visited:
                            queue.append((link, depth + 1))
                
                logger.info(f"Processed: {page_title} - Found {len(page_data.get('links', []))} links")
            else:
                logger.warning(f"Failed to fetch: {page_title}")
            
            # Rate limiting
            time.sleep(config.REQUEST_DELAY)
        
        logger.info(f"Crawl complete. Visited {len(self.visited)} pages.")
        return pages_data
    
    def fetch_page(self, page_title: str) -> Optional[Dict]:
        """
        Fetch a single Wikipedia page and extract data.
        
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
            
            # Extract page data
            page_data = {
                'title': page_title,
                'url': url,
                'html': response.text,
                'soup': soup,
                'infobox': self._extract_infobox(soup),
                'links': self._extract_links(soup),
                'categories': self._extract_categories(soup),
            }
            
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
        Check if a link should be skipped.
        
        Args:
            page_title: Wikipedia page title
            
        Returns:
            True if link should be skipped
        """
        # Check skip prefixes
        for prefix in config.SKIP_PREFIXES:
            if page_title.startswith(prefix):
                return True
        
        # Check skip keywords
        page_lower = page_title.lower()
        for keyword in config.SKIP_URL_KEYWORDS:
            if keyword in page_lower:
                return True
        
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
        
        # Check categories and title for keywords
        text = title + ' ' + ' '.join(categories)
        
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
