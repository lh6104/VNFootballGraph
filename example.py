#!/usr/bin/env python3
"""
Example script demonstrating Vietnamese Football Graph usage.
"""

import logging
from src.crawl import WikiCrawler
from src.parse_infobox import InfoboxParser
from src import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def example_fetch_single_page():
    """Example: Fetch and parse a single Wikipedia page."""
    logger.info("=" * 60)
    logger.info("Example 1: Fetch Single Page")
    logger.info("=" * 60)
    
    crawler = WikiCrawler(max_depth=0)
    parser = InfoboxParser()
    
    # Fetch Nguyễn Quang Hải's page
    page_title = "Nguyễn Quang Hải (sinh 1997)"
    logger.info(f"Fetching: {page_title}")
    
    page_data = crawler.fetch_page(page_title)
    
    if page_data:
        logger.info(f"✓ Successfully fetched: {page_data['title']}")
        logger.info(f"  URL: {page_data['url']}")
        logger.info(f"  Links found: {len(page_data['links'])}")
        logger.info(f"  Categories: {len(page_data['categories'])}")
        
        # Parse infobox
        infobox_data = parser.parse(page_data['infobox'])
        logger.info(f"  Infobox fields: {len(infobox_data)}")
        
        if infobox_data:
            logger.info("\n  Parsed data:")
            for key, value in infobox_data.items():
                logger.info(f"    {key}: {value}")
        
        # Determine entity type
        entity_type = crawler.get_page_type(page_data)
        logger.info(f"\n  Entity type: {entity_type}")
        
    else:
        logger.error("✗ Failed to fetch page")


def example_crawl_with_depth():
    """Example: Crawl with depth limit."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 2: Crawl with Depth")
    logger.info("=" * 60)
    
    crawler = WikiCrawler(max_depth=1)
    
    seed_page = "Nguyễn Quang Hải (sinh 1997)"
    logger.info(f"Starting crawl from: {seed_page}")
    logger.info(f"Max depth: 1")
    
    pages_data = crawler.crawl(seed_page)
    
    logger.info(f"\n✓ Crawl complete!")
    logger.info(f"  Total pages visited: {len(pages_data)}")
    
    # Show page types
    parser = InfoboxParser()
    entity_types = {}
    
    for page_data in pages_data:
        entity_type = crawler.get_page_type(page_data)
        if entity_type:
            entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
    
    logger.info("\n  Entity types found:")
    for entity_type, count in entity_types.items():
        logger.info(f"    {entity_type}: {count}")


def example_parse_vietnamese_fields():
    """Example: Parse Vietnamese infobox fields."""
    logger.info("\n" + "=" * 60)
    logger.info("Example 3: Parse Vietnamese Fields")
    logger.info("=" * 60)
    
    parser = InfoboxParser()
    
    # Test date parsing
    test_dates = [
        "15 tháng 4 năm 1997",
        "15/4/1997",
        "1997"
    ]
    
    logger.info("Date parsing:")
    for date_str in test_dates:
        parsed = parser.parse_date(date_str)
        logger.info(f"  '{date_str}' -> '{parsed}'")
    
    # Test height parsing
    test_heights = [
        "1,68 m",
        "1.68 m",
        "168 cm"
    ]
    
    logger.info("\nHeight parsing:")
    for height_str in test_heights:
        parsed = parser.parse_height(height_str)
        logger.info(f"  '{height_str}' -> {parsed} cm")
    
    # Show field mappings
    logger.info("\nVietnamese field mappings (sample):")
    sample_mappings = list(config.FIELD_MAPPINGS.items())[:10]
    for vn_name, en_name in sample_mappings:
        logger.info(f"  '{vn_name}' -> '{en_name}'")


def main():
    """Run all examples."""
    logger.info("Vietnamese Football Graph - Examples")
    logger.info("=" * 60)
    
    try:
        # Example 1: Fetch single page
        example_fetch_single_page()
        
        # Example 2: Crawl with depth (commented out to save time)
        # example_crawl_with_depth()
        
        # Example 3: Parse Vietnamese fields
        example_parse_vietnamese_fields()
        
        logger.info("\n" + "=" * 60)
        logger.info("All examples completed!")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"Error running examples: {e}", exc_info=True)


if __name__ == '__main__':
    main()
