"""
Main entry point for Vietnamese Football Graph crawler.
Orchestrates crawling, parsing, and graph building.
"""

import argparse
import json
import logging
import sys
import signal
import psutil
import os
from typing import Dict, List
from pathlib import Path
from datetime import datetime

from . import config
from .crawl import WikiCrawler
from .parse_infobox import InfoboxParser
from .graph_builder import GraphBuilder

# Configure logging with file handler
def setup_logging():
    """Setup logging to both console and file."""
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Generate log filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = logs_dir / f"crawl_{timestamp}.log"
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, config.LOG_LEVEL))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler (INFO and above)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (all levels including DEBUG)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_formatter = logging.Formatter(
        config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)
    
    # Log the log file location
    root_logger.info(f"Log file: {log_file}")
    
    return log_file

logger = logging.getLogger(__name__)


class VNFootballGraphBuilder:
    """Main orchestrator for building Vietnamese football graph."""
    
    def __init__(self, max_depth: int = config.DEFAULT_MAX_DEPTH,
                 output_mode: str = config.DEFAULT_OUTPUT_MODE,
                 checkpoint_file: str = None):
        """
        Initialize the graph builder.
        
        Args:
            max_depth: Maximum crawl depth
            output_mode: Output mode ('neo4j', 'json', or 'both')
            checkpoint_file: Path to checkpoint file for resume
        """
        self.max_depth = max_depth
        self.output_mode = output_mode
        self.checkpoint_file = checkpoint_file or "data/checkpoint.json"
        self.interrupted = False
        
        self.crawler = WikiCrawler(max_depth=max_depth)
        self.parser = InfoboxParser()
        self.graph_builder = None
        
        if output_mode in ['neo4j', 'both']:
            try:
                self.graph_builder = GraphBuilder()
                self.graph_builder.create_constraints()
            except Exception as e:
                logger.error(f"Failed to initialize Neo4j: {e}")
                if output_mode == 'neo4j':
                    raise
        
        self.entities = []
        self.relationships = []
        
        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        
        # Load checkpoint if exists
        self._load_checkpoint()
    
    def _signal_handler(self, signum, frame):
        """Handle Ctrl+C gracefully."""
        logger.warning("\nInterrupt received! Saving checkpoint...")
        self.interrupted = True
        self._save_checkpoint()
        logger.info("Checkpoint saved. You can resume later.")
        sys.exit(0)
    
    def _load_checkpoint(self):
        """Load checkpoint if exists."""
        checkpoint_path = Path(self.checkpoint_file)
        if checkpoint_path.exists():
            try:
                with open(checkpoint_path, 'r', encoding='utf-8') as f:
                    checkpoint = json.load(f)
                
                self.entities = checkpoint.get('entities', [])
                self.relationships = checkpoint.get('relationships', [])
                visited = checkpoint.get('visited', [])
                page_tree = checkpoint.get('page_tree', {})
                
                # Validate checkpoint: if no entities but has visited pages, it's corrupted
                if len(visited) > 0 and len(self.entities) == 0:
                    logger.warning(f"Checkpoint appears corrupted ({len(visited)} visited pages but 0 entities). Ignoring checkpoint.")
                    return
                
                self.crawler.visited = set(visited)
                self.crawler.page_tree = page_tree
                
                logger.info(f"Loaded checkpoint: {len(self.entities)} entities, {len(self.relationships)} relationships")
                logger.info(f"   Already visited: {len(self.crawler.visited)} pages")
            except Exception as e:
                logger.warning(f"Failed to load checkpoint: {e}")
    
    def _save_checkpoint(self):
        """Save current progress to checkpoint file."""
        try:
            checkpoint_path = Path(self.checkpoint_file)
            checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
            
            checkpoint = {
                'entities': self.entities,
                'relationships': self.relationships,
                'visited': list(self.crawler.visited),
                'page_tree': self.crawler.page_tree,
                'metadata': {
                    'max_depth': self.max_depth,
                    'total_entities': len(self.entities),
                    'total_relationships': len(self.relationships),
                    'pages_visited': len(self.crawler.visited),
                }
            }
            
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(checkpoint, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"Checkpoint saved: {len(self.entities)} entities")
        except Exception as e:
            logger.error(f"Failed to save checkpoint: {e}")
    
    def _log_memory_usage(self):
        """Log current memory usage."""
        try:
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            mem_mb = mem_info.rss / 1024 / 1024
            logger.info(f"Memory usage: {mem_mb:.1f} MB")
        except Exception as e:
            logger.debug(f"Could not get memory info: {e}")
    
    def _check_memory_limit(self, limit_mb: int = 8192) -> bool:
        """
        Check if memory usage exceeds limit.
        
        Args:
            limit_mb: Memory limit in MB (default: 8GB)
            
        Returns:
            True if limit exceeded
        """
        try:
            process = psutil.Process(os.getpid())
            mem_info = process.memory_info()
            mem_mb = mem_info.rss / 1024 / 1024
            
            if mem_mb > limit_mb:
                logger.warning(f"Memory usage ({mem_mb:.1f} MB) exceeds limit ({limit_mb} MB)")
                return True
            return False
        except Exception as e:
            logger.debug(f"Could not check memory limit: {e}")
            return False
    
    def build(self, seed_page: str):
        """
        Build graph from seed page.
        
        Args:
            seed_page: Starting Wikipedia page title
        """
        logger.info(f"Starting graph build from: {seed_page}")
        logger.info(f"Max depth: {self.max_depth}, Output mode: {self.output_mode}")
        
        # Step 1 & 2: Crawl and parse pages (streaming)
        logger.info("=" * 60)
        logger.info("STEP 1 & 2: Crawling and parsing Wikipedia pages (streaming)")
        logger.info("=" * 60)
        
        # Process pages as they are yielded (memory efficient)
        page_count = 0
        for page_data in self.crawler.crawl(seed_page):
            page_count += 1
            self._parse_page(page_data)
            
            # Monitor memory and save checkpoint every 10 pages
            if page_count % 10 == 0:
                self._save_checkpoint()
                self._log_memory_usage()
            
            # Safety check: stop if memory usage is too high
            if page_count % 50 == 0:
                if self._check_memory_limit():
                    logger.warning("Memory limit reached! Stopping crawl.")
                    break
        
        logger.info(f"Processed {page_count} pages, extracted {len(self.entities)} entities")
        
        # Step 3: Build graph
        logger.info("=" * 60)
        logger.info("STEP 3: Building graph")
        logger.info("=" * 60)
        self._build_graph()
        
        # Step 4: Output results
        logger.info("=" * 60)
        logger.info("STEP 4: Outputting results")
        logger.info("=" * 60)
        self._output_results()
        
        logger.info("=" * 60)
        logger.info("Graph build complete!")
        logger.info("=" * 60)
    
    def _parse_page(self, page_data: Dict):
        """Parse a single page and extract entity."""
        title = page_data['title']
        logger.debug(f"Parsing: {title}")
        
        # Determine entity type
        entity_type = self.crawler.get_page_type(page_data)
        
        if not entity_type:
            logger.debug(f"Could not determine type for: {title}")
            return
        
        # Parse infobox
        infobox = page_data.get('infobox')
        infobox_data = self.parser.parse(infobox)
        
        # Check if player is Vietnamese diaspora/naturalized
        is_diaspora = False
        if entity_type == 'player':
            is_diaspora = self.crawler.is_vietnamese_diaspora(page_data)
            if is_diaspora:
                logger.info(f"  → {title}: Vietnamese diaspora/naturalized player")
                infobox_data['is_vietnamese_diaspora'] = True
        
        # Create entity
        entity = {
            'name': title,
            'type': entity_type,
            'url': page_data['url'],
            'properties': infobox_data,
            'categories': page_data.get('categories', []),
        }
        
        self.entities.append(entity)
        
        # Extract relationships
        self._extract_relationships(entity, infobox, infobox_data)
    
    def _extract_relationships(self, entity: Dict, infobox, infobox_data: Dict):
        """Extract relationships from entity data."""
        entity_name = entity['name']
        entity_type = entity['type']
        
        # Extract relationship data
        rel_data = self.parser.extract_relationships(infobox_data)
        
        # Player relationships
        if entity_type == 'player':
            # Player -> Club
            for club in rel_data['clubs']:
                if club:
                    self.relationships.append({
                        'type': 'PLAYED_FOR',
                        'from': entity_name,
                        'from_type': 'player',
                        'to': club,
                        'to_type': 'club',
                    })
            
            # Player -> Coach
            for coach in rel_data['coaches']:
                if coach:
                    self.relationships.append({
                        'type': 'TRAINED_UNDER',
                        'from': entity_name,
                        'from_type': 'player',
                        'to': coach,
                        'to_type': 'coach',
                    })
            
            # Player -> National Team
            for team in rel_data['national_teams']:
                if team:
                    self.relationships.append({
                        'type': 'MEMBER_OF',
                        'from': entity_name,
                        'from_type': 'player',
                        'to': team,
                        'to_type': 'national_team',
                    })
        
        # Coach relationships
        elif entity_type == 'coach':
            # Coach -> Club
            for club in rel_data['clubs']:
                if club:
                    self.relationships.append({
                        'type': 'COACHED',
                        'from': entity_name,
                        'from_type': 'coach',
                        'to': club,
                        'to_type': 'club',
                    })
    
    def _build_graph(self):
        """Build graph in Neo4j."""
        if not self.graph_builder:
            logger.info("Skipping Neo4j graph building (not configured)")
            return
        
        # Create nodes
        logger.info("Creating nodes...")
        for entity in self.entities:
            name = entity['name']
            entity_type = entity['type']
            properties = entity['properties'].copy()
            properties['url'] = entity['url']
            
            if entity_type == 'player':
                self.graph_builder.create_player(name, properties)
            elif entity_type == 'coach':
                self.graph_builder.create_coach(name, properties)
            elif entity_type == 'club':
                self.graph_builder.create_club(name, properties)
            elif entity_type == 'national_team':
                self.graph_builder.create_national_team(name, properties)
        
        # Create relationships
        logger.info("Creating relationships...")
        for rel in self.relationships:
            rel_type = rel['type']
            from_name = rel['from']
            to_name = rel['to']
            
            # Ensure target nodes exist
            to_type = rel['to_type']
            if to_type == 'club':
                self.graph_builder.create_club(to_name, {'url': ''})
            elif to_type == 'coach':
                self.graph_builder.create_coach(to_name, {'url': ''})
            elif to_type == 'national_team':
                self.graph_builder.create_national_team(to_name, {'url': ''})
            
            # Create relationship
            if rel_type == 'PLAYED_FOR':
                self.graph_builder.create_played_for(from_name, to_name)
            elif rel_type == 'COACHED':
                self.graph_builder.create_coached(from_name, to_name)
            elif rel_type == 'TRAINED_UNDER':
                self.graph_builder.create_trained_under(from_name, to_name)
            elif rel_type == 'MEMBER_OF':
                self.graph_builder.create_member_of(from_name, to_name)
        
        # Print statistics
        stats = self.graph_builder.get_stats()
        logger.info("Graph statistics:")
        for key, value in stats.items():
            logger.info(f"  {key}: {value}")
    
    def _output_results(self):
        """Output results based on output mode."""
        if self.output_mode in ['json', 'both']:
            self._output_json()
        
        if self.graph_builder:
            logger.info("Graph created in Neo4j")
            logger.info(f"Neo4j URI: {config.NEO4J_URI}")
    
    def _output_json(self):
        """Output results to JSON file."""
        # Calculate statistics
        total_players = sum(1 for e in self.entities if e['type'] == 'player')
        diaspora_players = sum(
            1 for e in self.entities 
            if e['type'] == 'player' and e['properties'].get('is_vietnamese_diaspora', False)
        )
        
        output_data = {
            'entities': self.entities,
            'relationships': self.relationships,
            'metadata': {
                'max_depth': self.max_depth,
                'total_entities': len(self.entities),
                'total_relationships': len(self.relationships),
                'pages_visited': len(self.crawler.visited),
                'total_players': total_players,
                'vietnamese_diaspora_players': diaspora_players,
            }
        }
        
        output_file = config.JSON_OUTPUT_FILE
        
        # Create output directory if it doesn't exist
        output_dir = Path(output_file).parent
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"JSON output saved to: {output_file}")
        logger.info(f"  Total players: {total_players}")
        logger.info(f"  Vietnamese diaspora/naturalized players: {diaspora_players}")
        
        # Clean up checkpoint file after successful completion
        checkpoint_path = Path(self.checkpoint_file)
        if checkpoint_path.exists():
            checkpoint_path.unlink()
            logger.info("Checkpoint file removed (crawl completed)")
    
    def close(self):
        """Clean up resources."""
        if self.graph_builder:
            self.graph_builder.close()


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description='Build Vietnamese Football Network Graph from Wikipedia'
    )
    
    parser.add_argument(
        '--seed',
        type=str,
        default=config.DEFAULT_SEED_PAGE,
        help=f'Seed Wikipedia page title (default: {config.DEFAULT_SEED_PAGE})'
    )
    
    parser.add_argument(
        '--depth',
        type=int,
        default=config.DEFAULT_MAX_DEPTH,
        help=f'Maximum crawl depth (default: {config.DEFAULT_MAX_DEPTH})'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        choices=config.OUTPUT_MODES,
        default=config.DEFAULT_OUTPUT_MODE,
        help=f'Output mode (default: {config.DEFAULT_OUTPUT_MODE})'
    )
    
    parser.add_argument(
        '--neo4j-uri',
        type=str,
        help='Neo4j URI (default: from config or env)'
    )
    
    parser.add_argument(
        '--neo4j-user',
        type=str,
        help='Neo4j username (default: from config or env)'
    )
    
    parser.add_argument(
        '--neo4j-password',
        type=str,
        help='Neo4j password (default: from config or env)'
    )
    
    parser.add_argument(
        '--clear-db',
        action='store_true',
        help='Clear Neo4j database before building'
    )
    
    args = parser.parse_args()
    
    # Setup logging first
    log_file = setup_logging()
    
    # Override Neo4j settings if provided
    if args.neo4j_uri:
        config.NEO4J_URI = args.neo4j_uri
    if args.neo4j_user:
        config.NEO4J_USER = args.neo4j_user
    if args.neo4j_password:
        config.NEO4J_PASSWORD = args.neo4j_password
    
    try:
        # Clear database if requested
        if args.clear_db and args.output in ['neo4j', 'both']:
            logger.warning("Clearing Neo4j database...")
            gb = GraphBuilder()
            gb.clear_database()
            gb.close()
        
        # Build graph
        builder = VNFootballGraphBuilder(
            max_depth=args.depth,
            output_mode=args.output
        )
        
        builder.build(args.seed)
        builder.close()
        
        logger.info("Success!")
        return 0
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
