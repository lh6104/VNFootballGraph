"""
Advanced filtering module with relevance scoring system.
Evaluates page relevance using multiple signals and assigns layer (core/context).
"""

import re
import logging
from typing import Dict, List, Optional, Tuple, Set
from bs4 import BeautifulSoup

from . import config

logger = logging.getLogger(__name__)


class AdvancedFilter:
    """
    Advanced filtering system with multi-signal relevance scoring.
    Determines if a page should be crawled and at what layer (core/context).
    """
    
    def __init__(self):
        """Initialize the advanced filter."""
        self.core_nodes: Set[str] = set()  # Track high-quality core nodes
        self.compiled_patterns = [re.compile(p, re.IGNORECASE) for p in config.SEMANTIC_PATTERNS]
        
    def evaluate_page(
        self,
        title: str,
        text: str = "",
        categories: List[str] = None,
        infobox_type: str = "",
        infobox: Optional[BeautifulSoup] = None,
        neighbors: List[str] = None,
        distance_from_seed: int = 0
    ) -> Tuple[int, str]:
        """
        Evaluate page relevance using multiple signals.
        
        Args:
            title: Page title
            text: Lead paragraph or full text
            categories: List of Wikipedia categories
            infobox_type: Type of infobox (e.g., "infobox football biography")
            infobox: BeautifulSoup infobox object
            neighbors: List of pages that link to this page
            distance_from_seed: Graph distance from seed node
            
        Returns:
            Tuple of (relevance_score, layer) where layer is "core", "context", or "skip"
        """
        score = 0
        signals = []
        
        # Normalize inputs
        categories = categories or []
        neighbors = neighbors or []
        title_lower = title.lower().replace('_', ' ')
        text_lower = text.lower()
        
        # ========================================================================
        # SIGNAL 1: File/Media Page Check (Highest Priority)
        # ========================================================================
        if config.ACTIVE_FILTERS.get("keyword_filter", True):
            for prefix in config.SKIP_PREFIXES:
                if title.startswith(prefix):
                    score += config.RELEVANCE_WEIGHTS["file_page"]
                    signals.append(f"file_page:{prefix}")
                    logger.debug(f"⛔ {title}: File/meta page detected")
                    return (score, "skip")
        
        # ========================================================================
        # SIGNAL 2: Blacklist/Noise Page Check
        # ========================================================================
        if config.ACTIVE_FILTERS.get("keyword_filter", True):
            for noise_pattern in config.NOISE_PAGE_TITLES:
                if noise_pattern in title_lower:
                    score += config.RELEVANCE_WEIGHTS["blacklist_hit"]
                    signals.append(f"blacklist:{noise_pattern}")
                    logger.debug(f"⛔ {title}: Blacklist hit '{noise_pattern}'")
        
        # ========================================================================
        # SIGNAL 3: Keyword Matching (INCLUDE vs EXCLUDE)
        # ========================================================================
        if config.ACTIVE_FILTERS.get("keyword_filter", True):
            include_count = 0
            exclude_count = 0
            
            # Check INCLUDE keywords
            for keyword in config.INCLUDE_KEYWORDS:
                if keyword in title_lower or keyword in text_lower:
                    include_count += 1
            
            # Check EXCLUDE keywords
            for keyword in config.EXCLUDE_KEYWORDS:
                if keyword in title_lower or keyword in text_lower:
                    exclude_count += 1
            
            # Net keyword score
            if include_count > 0:
                score += config.RELEVANCE_WEIGHTS["keyword_match"]
                signals.append(f"keyword_match:+{include_count}")
            
            if exclude_count > 0:
                score += config.RELEVANCE_WEIGHTS["exclude_keyword_hit"] * exclude_count
                signals.append(f"exclude_hit:-{exclude_count}")
        
        # ========================================================================
        # SIGNAL 4: Semantic Pattern Matching
        # ========================================================================
        if config.ACTIVE_FILTERS.get("semantic_filter", True) and text:
            pattern_matches = 0
            for pattern in self.compiled_patterns:
                if pattern.search(text_lower):
                    pattern_matches += 1
            
            if pattern_matches > 0:
                score += config.RELEVANCE_WEIGHTS["contextual_text"]
                signals.append(f"semantic:+{pattern_matches}")
                logger.debug(f"✅ {title}: Semantic patterns matched ({pattern_matches})")
        
        # ========================================================================
        # SIGNAL 5: Category Validation
        # ========================================================================
        if config.ACTIVE_FILTERS.get("category_filter", True) and categories:
            valid_category_count = 0
            for category in categories:
                category_lower = category.lower()
                for valid_cat in config.VALID_CATEGORIES:
                    if valid_cat in category_lower:
                        valid_category_count += 1
                        break
            
            if valid_category_count > 0:
                score += config.RELEVANCE_WEIGHTS["category_valid"]
                signals.append(f"category:+{valid_category_count}")
                logger.debug(f"✅ {title}: Valid categories ({valid_category_count})")
        
        # ========================================================================
        # SIGNAL 6: Infobox Validation
        # ========================================================================
        if config.ACTIVE_FILTERS.get("infobox_filter", True):
            if infobox_type:
                infobox_type_lower = infobox_type.lower()
                for valid_type in config.VALID_INFOBOX_TYPES:
                    if valid_type in infobox_type_lower:
                        score += config.RELEVANCE_WEIGHTS["infobox_valid"]
                        signals.append(f"infobox:{valid_type}")
                        logger.debug(f"✅ {title}: Valid infobox type")
                        break
            elif infobox:
                # Try to detect infobox type from class or content
                infobox_classes = infobox.get('class', [])
                if any('infobox' in str(c).lower() for c in infobox_classes):
                    score += config.RELEVANCE_WEIGHTS["infobox_valid"]
                    signals.append("infobox:detected")
        
        # ========================================================================
        # SIGNAL 7: Neighbor Quality (Linked by Core Nodes)
        # ========================================================================
        if config.ACTIVE_FILTERS.get("neighbor_filter", True) and neighbors:
            core_neighbor_count = sum(1 for n in neighbors if n in self.core_nodes)
            if core_neighbor_count > 0:
                score += config.RELEVANCE_WEIGHTS["linked_by_core"] * core_neighbor_count
                signals.append(f"linked_by_core:+{core_neighbor_count}")
                logger.debug(f"✅ {title}: Linked by {core_neighbor_count} core nodes")
        
        # ========================================================================
        # SIGNAL 8: Graph Distance Check
        # ========================================================================
        if config.ACTIVE_FILTERS.get("graph_filter", True):
            if distance_from_seed > config.MAX_ALLOWED_DISTANCE:
                score -= 2  # Penalty for being too far from seed
                signals.append(f"distance:-{distance_from_seed}")
                logger.debug(f"⚠️ {title}: Too far from seed ({distance_from_seed})")
        
        # ========================================================================
        # SIGNAL 9: NER Entity Detection (Optional)
        # ========================================================================
        if config.ACTIVE_FILTERS.get("ner_filter", False) and text:
            try:
                # Try to import underthesea
                from underthesea import ner
                entities = ner(text[:500])  # Only check first 500 chars
                
                valid_entities = [e for e in entities if e[3] in config.NER_ENTITY_TYPES]
                if valid_entities:
                    score += config.NER_SCORE_WEIGHT
                    signals.append(f"ner:+{len(valid_entities)}")
                    logger.debug(f"✅ {title}: NER entities detected ({len(valid_entities)})")
            except ImportError:
                logger.warning("NER filter enabled but underthesea not installed")
            except Exception as e:
                logger.warning(f"NER processing failed: {e}")
        
        # ========================================================================
        # Determine Layer Based on Score
        # ========================================================================
        if score >= config.RELEVANCE_SCORE_THRESHOLD_CORE:
            layer = "core"
            self.core_nodes.add(title)  # Track as core node
            logger.info(f"⭐ {title}: CORE node (score={score}, signals={signals})")
        elif score >= config.RELEVANCE_SCORE_THRESHOLD_CONTEXT:
            layer = "context"
            logger.info(f"📌 {title}: CONTEXT node (score={score}, signals={signals})")
        else:
            layer = "skip"
            logger.debug(f"⛔ {title}: SKIP (score={score}, signals={signals})")
        
        return (score, layer)
    
    def should_expand_links(self, layer: str) -> bool:
        """
        Determine if links from this page should be expanded.
        Only expand links from "core" layer pages.
        
        Args:
            layer: Node layer ("core", "context", or "skip")
            
        Returns:
            True if links should be expanded
        """
        return layer == "core"
    
    def get_infobox_type(self, infobox: Optional[BeautifulSoup]) -> str:
        """
        Extract infobox type from BeautifulSoup infobox object.
        
        Args:
            infobox: BeautifulSoup infobox object
            
        Returns:
            Infobox type string (lowercase)
        """
        if not infobox:
            return ""
        
        # Try to get from class attribute
        classes = infobox.get('class', [])
        for cls in classes:
            if 'infobox' in str(cls).lower():
                return str(cls).lower()
        
        # Try to get from data attributes
        for attr in ['data-type', 'data-template']:
            if infobox.has_attr(attr):
                return infobox[attr].lower()
        
        # Default: just "infobox"
        return "infobox"


# ============================================================================
# Convenience Functions
# ============================================================================

def evaluate_page_simple(
    title: str,
    text: str = "",
    categories: List[str] = None,
    infobox: Optional[BeautifulSoup] = None
) -> Tuple[int, str]:
    """
    Simplified evaluation function for quick filtering.
    
    Args:
        title: Page title
        text: Lead paragraph or full text
        categories: List of Wikipedia categories
        infobox: BeautifulSoup infobox object
        
    Returns:
        Tuple of (relevance_score, layer)
    """
    filter_instance = AdvancedFilter()
    infobox_type = filter_instance.get_infobox_type(infobox) if infobox else ""
    
    return filter_instance.evaluate_page(
        title=title,
        text=text,
        categories=categories,
        infobox_type=infobox_type,
        infobox=infobox
    )


def is_noise_page(title: str) -> bool:
    """
    Quick check if a page title matches noise patterns.
    
    Args:
        title: Page title
        
    Returns:
        True if page is noise/meta page
    """
    title_lower = title.lower().replace('_', ' ')
    
    # Check skip prefixes
    for prefix in config.SKIP_PREFIXES:
        if title.startswith(prefix):
            return True
    
    # Check noise patterns
    for pattern in config.NOISE_PAGE_TITLES:
        if pattern in title_lower:
            return True
    
    return False
