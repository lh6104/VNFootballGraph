"""
Neo4j graph builder for Vietnamese football network.
Creates nodes and relationships in Neo4j database.
"""

import logging
from typing import Dict, List, Optional, Any

try:
    from neo4j import GraphDatabase, Driver, Session
    from neo4j.exceptions import ServiceUnavailable, AuthError
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False
    GraphDatabase = None
    Driver = None
    Session = None
    ServiceUnavailable = Exception
    AuthError = Exception

from . import config

logger = logging.getLogger(__name__)


class GraphBuilder:
    """Builds graph in Neo4j database."""
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize Neo4j connection.
        
        Args:
            uri: Neo4j URI (default from config)
            user: Neo4j username (default from config)
            password: Neo4j password (default from config)
        """
        if not NEO4J_AVAILABLE:
            raise ImportError(
                "neo4j package is not installed. "
                "Install it with: pip install neo4j"
            )
        
        self.uri = uri or config.NEO4J_URI
        self.user = user or config.NEO4J_USER
        self.password = password or config.NEO4J_PASSWORD
        self.driver: Optional[Driver] = None
        
        self._connect()
    
    def _connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"Connected to Neo4j at {self.uri}")
        except (ServiceUnavailable, AuthError) as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def create_constraints(self):
        """Create uniqueness constraints for nodes."""
        constraints = [
            "CREATE CONSTRAINT player_name IF NOT EXISTS FOR (p:Player) REQUIRE p.name IS UNIQUE",
            "CREATE CONSTRAINT coach_name IF NOT EXISTS FOR (c:Coach) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT club_name IF NOT EXISTS FOR (c:Club) REQUIRE c.name IS UNIQUE",
            "CREATE CONSTRAINT national_team_name IF NOT EXISTS FOR (n:NationalTeam) REQUIRE n.name IS UNIQUE",
        ]
        
        with self.driver.session() as session:
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.debug(f"Created constraint: {constraint}")
                except Exception as e:
                    logger.warning(f"Constraint may already exist: {e}")
    
    def create_player(self, name: str, properties: Dict[str, Any]) -> bool:
        """
        Create or update a Player node.
        
        Args:
            name: Player name
            properties: Additional properties
            
        Returns:
            True if successful
        """
        query = """
        MERGE (p:Player {name: $name})
        SET p += $properties
        RETURN p
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, name=name, properties=properties)
                result.single()
                logger.info(f"Created/updated Player: {name}")
                return True
        except Exception as e:
            logger.error(f"Error creating Player {name}: {e}")
            return False
    
    def create_coach(self, name: str, properties: Dict[str, Any]) -> bool:
        """
        Create or update a Coach node.
        
        Args:
            name: Coach name
            properties: Additional properties
            
        Returns:
            True if successful
        """
        query = """
        MERGE (c:Coach {name: $name})
        SET c += $properties
        RETURN c
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, name=name, properties=properties)
                result.single()
                logger.info(f"Created/updated Coach: {name}")
                return True
        except Exception as e:
            logger.error(f"Error creating Coach {name}: {e}")
            return False
    
    def create_club(self, name: str, properties: Dict[str, Any]) -> bool:
        """
        Create or update a Club node.
        
        Args:
            name: Club name
            properties: Additional properties
            
        Returns:
            True if successful
        """
        query = """
        MERGE (c:Club {name: $name})
        SET c += $properties
        RETURN c
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, name=name, properties=properties)
                result.single()
                logger.info(f"Created/updated Club: {name}")
                return True
        except Exception as e:
            logger.error(f"Error creating Club {name}: {e}")
            return False
    
    def create_national_team(self, name: str, properties: Dict[str, Any]) -> bool:
        """
        Create or update a NationalTeam node.
        
        Args:
            name: National team name
            properties: Additional properties
            
        Returns:
            True if successful
        """
        query = """
        MERGE (n:NationalTeam {name: $name})
        SET n += $properties
        RETURN n
        """
        
        try:
            with self.driver.session() as session:
                result = session.run(query, name=name, properties=properties)
                result.single()
                logger.info(f"Created/updated NationalTeam: {name}")
                return True
        except Exception as e:
            logger.error(f"Error creating NationalTeam {name}: {e}")
            return False
    
    def create_played_for(self, player_name: str, club_name: str, 
                          properties: Dict[str, Any] = None) -> bool:
        """
        Create PLAYED_FOR relationship between Player and Club.
        
        Args:
            player_name: Player name
            club_name: Club name
            properties: Relationship properties (e.g., start_year, end_year)
            
        Returns:
            True if successful
        """
        query = """
        MATCH (p:Player {name: $player_name})
        MATCH (c:Club {name: $club_name})
        MERGE (p)-[r:PLAYED_FOR]->(c)
        SET r += $properties
        RETURN r
        """
        
        properties = properties or {}
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    player_name=player_name,
                    club_name=club_name,
                    properties=properties
                )
                result.single()
                logger.info(f"Created PLAYED_FOR: {player_name} -> {club_name}")
                return True
        except Exception as e:
            logger.error(f"Error creating PLAYED_FOR relationship: {e}")
            return False
    
    def create_coached(self, coach_name: str, club_name: str,
                       properties: Dict[str, Any] = None) -> bool:
        """
        Create COACHED relationship between Coach and Club.
        
        Args:
            coach_name: Coach name
            club_name: Club name
            properties: Relationship properties
            
        Returns:
            True if successful
        """
        query = """
        MATCH (coach:Coach {name: $coach_name})
        MATCH (club:Club {name: $club_name})
        MERGE (coach)-[r:COACHED]->(club)
        SET r += $properties
        RETURN r
        """
        
        properties = properties or {}
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    coach_name=coach_name,
                    club_name=club_name,
                    properties=properties
                )
                result.single()
                logger.info(f"Created COACHED: {coach_name} -> {club_name}")
                return True
        except Exception as e:
            logger.error(f"Error creating COACHED relationship: {e}")
            return False
    
    def create_trained_under(self, player_name: str, coach_name: str,
                             properties: Dict[str, Any] = None) -> bool:
        """
        Create TRAINED_UNDER relationship between Player and Coach.
        
        Args:
            player_name: Player name
            coach_name: Coach name
            properties: Relationship properties
            
        Returns:
            True if successful
        """
        query = """
        MATCH (p:Player {name: $player_name})
        MATCH (c:Coach {name: $coach_name})
        MERGE (p)-[r:TRAINED_UNDER]->(c)
        SET r += $properties
        RETURN r
        """
        
        properties = properties or {}
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    player_name=player_name,
                    coach_name=coach_name,
                    properties=properties
                )
                result.single()
                logger.info(f"Created TRAINED_UNDER: {player_name} -> {coach_name}")
                return True
        except Exception as e:
            logger.error(f"Error creating TRAINED_UNDER relationship: {e}")
            return False
    
    def create_member_of(self, player_name: str, team_name: str,
                         properties: Dict[str, Any] = None) -> bool:
        """
        Create MEMBER_OF relationship between Player and NationalTeam.
        
        Args:
            player_name: Player name
            team_name: National team name
            properties: Relationship properties
            
        Returns:
            True if successful
        """
        query = """
        MATCH (p:Player {name: $player_name})
        MATCH (n:NationalTeam {name: $team_name})
        MERGE (p)-[r:MEMBER_OF]->(n)
        SET r += $properties
        RETURN r
        """
        
        properties = properties or {}
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    player_name=player_name,
                    team_name=team_name,
                    properties=properties
                )
                result.single()
                logger.info(f"Created MEMBER_OF: {player_name} -> {team_name}")
                return True
        except Exception as e:
            logger.error(f"Error creating MEMBER_OF relationship: {e}")
            return False
    
    def create_teammate_with(self, player1_name: str, player2_name: str,
                             properties: Dict[str, Any] = None) -> bool:
        """
        Create TEAMMATE_WITH relationship between two Players.
        
        Args:
            player1_name: First player name
            player2_name: Second player name
            properties: Relationship properties
            
        Returns:
            True if successful
        """
        query = """
        MATCH (p1:Player {name: $player1_name})
        MATCH (p2:Player {name: $player2_name})
        MERGE (p1)-[r:TEAMMATE_WITH]-(p2)
        SET r += $properties
        RETURN r
        """
        
        properties = properties or {}
        
        try:
            with self.driver.session() as session:
                result = session.run(
                    query,
                    player1_name=player1_name,
                    player2_name=player2_name,
                    properties=properties
                )
                result.single()
                logger.info(f"Created TEAMMATE_WITH: {player1_name} <-> {player2_name}")
                return True
        except Exception as e:
            logger.error(f"Error creating TEAMMATE_WITH relationship: {e}")
            return False
    
    def get_stats(self) -> Dict[str, int]:
        """
        Get statistics about the graph.
        
        Returns:
            Dictionary with node and relationship counts
        """
        stats = {}
        
        queries = {
            'players': "MATCH (p:Player) RETURN count(p) as count",
            'coaches': "MATCH (c:Coach) RETURN count(c) as count",
            'clubs': "MATCH (c:Club) RETURN count(c) as count",
            'national_teams': "MATCH (n:NationalTeam) RETURN count(n) as count",
            'played_for': "MATCH ()-[r:PLAYED_FOR]->() RETURN count(r) as count",
            'coached': "MATCH ()-[r:COACHED]->() RETURN count(r) as count",
            'trained_under': "MATCH ()-[r:TRAINED_UNDER]->() RETURN count(r) as count",
            'member_of': "MATCH ()-[r:MEMBER_OF]->() RETURN count(r) as count",
            'teammate_with': "MATCH ()-[r:TEAMMATE_WITH]-() RETURN count(r) as count",
        }
        
        with self.driver.session() as session:
            for key, query in queries.items():
                try:
                    result = session.run(query)
                    record = result.single()
                    stats[key] = record['count'] if record else 0
                except Exception as e:
                    logger.error(f"Error getting stats for {key}: {e}")
                    stats[key] = 0
        
        return stats
    
    def clear_database(self):
        """Clear all nodes and relationships from database."""
        query = "MATCH (n) DETACH DELETE n"
        
        try:
            with self.driver.session() as session:
                session.run(query)
                logger.warning("Database cleared!")
        except Exception as e:
            logger.error(f"Error clearing database: {e}")
