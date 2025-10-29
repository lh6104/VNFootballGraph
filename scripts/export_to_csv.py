#!/usr/bin/env python3
"""
Export JSON data to CSV format with relationships support.

Usage:
    python scripts/export_to_csv.py --format flat
    python scripts/export_to_csv.py --format normalized
    python scripts/export_to_csv.py --format all
"""

import json
import csv
import argparse
from pathlib import Path
from typing import Dict, List


def export_normalized_csv(data: Dict, output_dir: Path):
    """
    Export to normalized CSV files (recommended format).
    
    Args:
        data: JSON data
        output_dir: Output directory
    """
    entities = data['entities']
    relationships = data.get('relationships', [])
    
    print(f"\n📊 Exporting normalized CSV format...")
    print(f"   Entities: {len(entities)}")
    print(f"   Relationships: {len(relationships)}")
    
    # 1. Export players.csv
    players = [e for e in entities if e['type'] == 'player']
    
    players_file = output_dir / 'players.csv'
    with open(players_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow([
            'player_id', 'name', 'display_name', 'url',
            'birth_date', 'birth_place', 'height', 'position',
            'current_team', 'shirt_number',
            'is_vietnamese_diaspora'
        ])
        
        for idx, player in enumerate(players, 1):
            props = player['properties']
            writer.writerow([
                idx,
                player['name'],
                props.get('name', player['name']),
                player['url'],
                props.get('birth_date', ''),
                props.get('birth_place', ''),
                props.get('height', ''),
                props.get('position', ''),
                props.get('đội_hiện_nay', props.get('current_team', '')),
                props.get('shirt_number', ''),
                props.get('is_vietnamese_diaspora', False)
            ])
    
    print(f"✓ Exported {len(players)} players to: {players_file}")
    
    # 2. Export clubs.csv
    clubs = [e for e in entities if e['type'] == 'club']
    
    clubs_file = output_dir / 'clubs.csv'
    with open(clubs_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow([
            'club_id', 'name', 'display_name', 'url',
            'founded', 'stadium', 'league'
        ])
        
        for idx, club in enumerate(clubs, 1):
            props = club['properties']
            writer.writerow([
                idx,
                club['name'],
                props.get('name', club['name']),
                club['url'],
                props.get('founded', props.get('thành_lập', '')),
                props.get('stadium', props.get('sân_vận_động', '')),
                props.get('league', props.get('giải_đấu', ''))
            ])
    
    print(f"✓ Exported {len(clubs)} clubs to: {clubs_file}")
    
    # 3. Export coaches.csv
    coaches = [e for e in entities if e['type'] == 'coach']
    
    coaches_file = output_dir / 'coaches.csv'
    with open(coaches_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow([
            'coach_id', 'name', 'display_name', 'url',
            'birth_date', 'birth_place', 'nationality'
        ])
        
        for idx, coach in enumerate(coaches, 1):
            props = coach['properties']
            writer.writerow([
                idx,
                coach['name'],
                props.get('name', coach['name']),
                coach['url'],
                props.get('birth_date', ''),
                props.get('birth_place', ''),
                props.get('nationality', '')
            ])
    
    print(f"✓ Exported {len(coaches)} coaches to: {coaches_file}")
    
    # 4. Export national_teams.csv
    teams = [e for e in entities if e['type'] == 'national_team']
    
    teams_file = output_dir / 'national_teams.csv'
    with open(teams_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow([
            'team_id', 'name', 'display_name', 'url'
        ])
        
        for idx, team in enumerate(teams, 1):
            props = team['properties']
            writer.writerow([
                idx,
                team['name'],
                props.get('name', team['name']),
                team['url']
            ])
    
    print(f"✓ Exported {len(teams)} national teams to: {teams_file}")
    
    # 5. Export relationships.csv (NEW!)
    if relationships:
        rels_file = output_dir / 'relationships.csv'
        with open(rels_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            writer.writerow([
                'relationship_id', 'type', 
                'from_entity', 'from_type',
                'to_entity', 'to_type'
            ])
            
            for idx, rel in enumerate(relationships, 1):
                writer.writerow([
                    idx,
                    rel['type'],
                    rel['from'],
                    rel['from_type'],
                    rel['to'],
                    rel['to_type']
                ])
        
        print(f"✓ Exported {len(relationships)} relationships to: {rels_file}")
        
        # Breakdown by type
        rel_types = {}
        for r in relationships:
            rel_types[r['type']] = rel_types.get(r['type'], 0) + 1
        
        print(f"\n  Relationship breakdown:")
        for rtype, count in sorted(rel_types.items(), key=lambda x: x[1], reverse=True):
            print(f"    - {rtype}: {count}")
    
    # 6. Export vietnamese_diaspora_players.csv
    diaspora = [e for e in entities if e['type'] == 'player' and e.get('properties', {}).get('is_vietnamese_diaspora')]
    
    if diaspora:
        diaspora_file = output_dir / 'vietnamese_diaspora_players.csv'
        with open(diaspora_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            writer.writerow([
                'player_id', 'name', 'display_name', 'url',
                'birth_date', 'birth_place', 'position'
            ])
            
            for player in diaspora:
                # Find player_id from main players list
                player_id = next((idx for idx, p in enumerate(players, 1) if p['name'] == player['name']), None)
                props = player['properties']
                
                writer.writerow([
                    player_id,
                    player['name'],
                    props.get('name', player['name']),
                    player['url'],
                    props.get('birth_date', ''),
                    props.get('birth_place', ''),
                    props.get('position', '')
                ])
        
        print(f"✓ Exported {len(diaspora)} Vietnamese diaspora players to: {diaspora_file}")


def export_flat_csv(data: Dict, output_dir: Path):
    """
    Export to single flat CSV file (simple format).
    
    Args:
        data: JSON data
        output_dir: Output directory
    """
    entities = data['entities']
    players = [e for e in entities if e['type'] == 'player']
    
    output_file = output_dir / 'players_flat.csv'
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        
        writer.writerow([
            'name', 'display_name', 'url',
            'birth_date', 'birth_place', 'height', 'position',
            'current_team', 'shirt_number',
            'is_vietnamese_diaspora'
        ])
        
        for player in players:
            props = player['properties']
            
            writer.writerow([
                player['name'],
                props.get('name', player['name']),
                player['url'],
                props.get('birth_date', ''),
                props.get('birth_place', ''),
                props.get('height', ''),
                props.get('position', ''),
                props.get('đội_hiện_nay', props.get('current_team', '')),
                props.get('shirt_number', ''),
                props.get('is_vietnamese_diaspora', False)
            ])
    
    print(f"✓ Exported {len(players)} players to: {output_file}")


def export_graph_csv(data: Dict, output_dir: Path):
    """
    Export graph-ready CSV files (for Neo4j import).
    
    Args:
        data: JSON data
        output_dir: Output directory
    """
    entities = data['entities']
    relationships = data.get('relationships', [])
    
    print(f"\n📊 Exporting graph-ready CSV format...")
    
    # Create nodes and relationships subdirectories
    nodes_dir = output_dir / 'nodes'
    rels_dir = output_dir / 'relationships'
    nodes_dir.mkdir(exist_ok=True)
    rels_dir.mkdir(exist_ok=True)
    
    # Define core properties for each entity type (exclude year ranges)
    core_properties = {
        'player': ['name', 'birth_date', 'birth_place', 'height', 'position', 
                   'current_team', 'shirt_number', 'is_vietnamese_diaspora'],
        'club': ['name', 'founded', 'stadium', 'league', 'thành_lập', 'sân_vận_động', 'giải_đấu'],
        'coach': ['name', 'birth_date', 'birth_place', 'nationality'],
        'national_team': ['name', 'confederation', 'fifa_code']
    }
    
    # Export nodes by type
    for entity_type in ['player', 'club', 'coach', 'national_team']:
        entities_of_type = [e for e in entities if e['type'] == entity_type]
        
        if not entities_of_type:
            continue
        
        output_file = nodes_dir / f'{entity_type}s.csv'
        
        with open(output_file, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            
            # Get core properties for this entity type
            props_to_export = core_properties.get(entity_type, ['name'])
            
            # Header: :ID, url, ...core properties
            header = [':ID', 'url:string'] + [f'{p}:string' for p in props_to_export]
            writer.writerow(header)
            
            # Rows
            for e in entities_of_type:
                props = e['properties']
                row = [
                    e['name'],
                    e['url']
                ]
                # Add core properties only
                for p in props_to_export:
                    row.append(props.get(p, ''))
                
                writer.writerow(row)
        
        print(f"✓ Exported {len(entities_of_type)} {entity_type}s to: {output_file}")
    
    # Export relationships by type
    if relationships:
        for rel_type in ['PLAYED_FOR', 'COACHED', 'MEMBER_OF', 'TRAINED_UNDER']:
            rels_of_type = [r for r in relationships if r['type'] == rel_type]
            
            if not rels_of_type:
                continue
            
            output_file = rels_dir / f'{rel_type.lower()}.csv'
            
            with open(output_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f)
                
                # Header: :START_ID, :END_ID, :TYPE
                writer.writerow([':START_ID', ':END_ID', ':TYPE'])
                
                # Rows
                for r in rels_of_type:
                    writer.writerow([
                        r['from'],
                        r['to'],
                        r['type']
                    ])
            
            print(f"✓ Exported {len(rels_of_type)} {rel_type} relationships to: {output_file}")


def main():
    parser = argparse.ArgumentParser(description='Export JSON to CSV')
    parser.add_argument(
        '--format',
        choices=['flat', 'normalized', 'graph', 'all'],
        default='normalized',
        help='Export format (default: normalized)'
    )
    parser.add_argument(
        '--input',
        default='data/vn_football_graph.json',
        help='Input JSON file'
    )
    parser.add_argument(
        '--output-dir',
        default='data/csv',
        help='Output directory for CSV files'
    )
    
    args = parser.parse_args()
    
    # Load data
    print(f"Loading data from: {args.input}")
    with open(args.input, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Export based on format
    if args.format == 'flat':
        export_flat_csv(data, output_dir)
    elif args.format == 'normalized':
        export_normalized_csv(data, output_dir)
    elif args.format == 'graph':
        export_graph_csv(data, output_dir)
    elif args.format == 'all':
        export_flat_csv(data, output_dir)
        export_normalized_csv(data, output_dir)
        export_graph_csv(data, output_dir)
    
    print(f"\n✅ Export complete! Files saved to: {output_dir}")
    print(f"\nMetadata:")
    print(f"  Total entities: {data['metadata']['total_entities']}")
    print(f"  Total relationships: {data['metadata']['total_relationships']}")
    print(f"  Total players: {data['metadata']['total_players']}")
    print(f"  Vietnamese diaspora: {data['metadata']['vietnamese_diaspora_players']}")


if __name__ == '__main__':
    main()
