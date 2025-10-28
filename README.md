# Vietnamese Football Knowledge Graph

> A Python-based web crawler that builds a comprehensive knowledge graph of Vietnamese football by extracting structured data from Vietnamese Wikipedia.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-active-success.svg)]()

---

## Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Output Format](#-output-format)
- [Configuration](#-configuration)
- [Project Structure](#-project-structure)
- [Advanced Features](#-advanced-features)
- [Examples](#-examples)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## Overview

This project crawls Vietnamese Wikipedia to extract information about football players, coaches, clubs, and national teams, then constructs a knowledge graph showing their relationships. The output is a structured JSON file containing nodes (entities) and edges (relationships) that can be used for analysis and visualization.

### What it does:

1. **Crawls** Vietnamese Wikipedia pages starting from a seed page
2. **Parses** infobox data (the information tables on Wikipedia pages)
3. **Extracts** entities (players, coaches, clubs, national teams)
4. **Identifies** relationships (who played for which club, who coached whom, etc.)
5. **Outputs** structured JSON with complete graph data

---

## Features

### Core Functionality
- **Intelligent Crawling**: Depth-limited BFS crawling with visited page tracking
- **Vietnamese Language Support**: Handles Vietnamese field names and date formats
- **Entity Recognition**: Automatically identifies players, coaches, clubs, and national teams
- **Relationship Extraction**: Extracts PLAYED_FOR, COACHED, TRAINED_UNDER, MEMBER_OF relationships
- **JSON Output**: Clean, structured output with full graph information

### Advanced Features
- **Auto-Checkpoint**: Saves progress every 5 pages, resume from where you left off
- **Graceful Ctrl+C**: Press Ctrl+C anytime to save and exit safely
- **Detailed Logging**: Automatic logging to timestamped files in `logs/` folder
- **Configurable**: Easy-to-customize field mappings and entity keywords
- **Rate Limiting**: Respects Wikipedia's rate limits (1 second delay between requests)


---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/VNFootballGraph.git
cd VNFootballGraph
```

2. **Install dependencies**

**Full installation (includes all features):**
```bash
pip install -r requirements.txt
```

**Minimal installation (JSON output only):**
```bash
pip install -r requirements-minimal.txt
```

### Core Dependencies

The project uses the following main packages:

| Package | Version | Purpose |
|---------|---------|---------|
| `beautifulsoup4` | 4.14.2 | HTML parsing |
| `requests` | 2.32.5 | HTTP requests |
| `lxml` | 6.0.2 | XML/HTML parser |
| `mwparserfromhell` | 0.7.2 | MediaWiki parsing |
| `python-dateutil` | 2.9.0 | Date parsing |
| `tqdm` | 4.67.1 | Progress bars |

### Optional Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `networkx` | 3.4.2 | Network analysis (optional) |
| `pandas` | 2.3.3 | Data analysis (optional) |
| `matplotlib` | 3.10.7 | Visualization (optional) |

> **Note**: The `requirements.txt` file includes additional packages for development and analysis. For minimal installation (JSON output only), you only need the core dependencies listed above.

---

## Quick Start

### Basic Usage

Crawl Wikipedia and save to JSON:

```bash
python -m src.main --depth 1
```

This will:
- Start from the default seed page (Nguyễn Quang Hải)
- Crawl to depth 1 (seed page + linked pages)
- Save results to `data/vn_football_graph.json`
- Save logs to `logs/crawl_YYYYMMDD_HHMMSS.log`

### View Results

```bash
# Pretty print JSON
cat data/vn_football_graph.json | python -m json.tool | less

# Or open in your favorite text editor
code data/vn_football_graph.json
```

---

## Usage

### Command Line Options

```bash
python -m src.main [OPTIONS]
```

| Option | Description | Default |
|--------|-------------|---------|
| `--seed` | Starting Wikipedia page title | "Nguyễn Quang Hải (sinh 1997)" |
| `--depth` | Maximum crawl depth (0-3 recommended) | 2 |

### Examples

**Test with a single page (depth 0):**
```bash
python -m src.main --depth 0
```

**Crawl with custom seed:**
```bash
python -m src.main --seed "Văn Quyết" --depth 1
```

**Crawl deeper (more pages, takes longer):**
```bash
python -m src.main --depth 2
```


---

## Output Format

### JSON Structure

The output file `data/vn_football_graph.json` contains:

```json
{
  "entities": [
    {
      "name": "Nguyễn Quang Hải (sinh 1997)",
      "type": "player",
      "url": "https://vi.wikipedia.org/wiki/Nguyễn_Quang_Hải_(sinh_1997)",
      "properties": {
        "name": "Nguyễn Quang Hải",
        "birth_date": "12 tháng 4, 1997 (28 tuổi)",
        "birth_place": "Đông Anh, Hà Nội, Việt Nam",
        "height": "1,68 m (5 ft 6 in)",
        "position": "Tiền vệ tấn công, Tiền vệ cánh",
        "current_club": "Công an Hà Nội",
        "jersey_number": "19"
      },
      "categories": []
    }
  ],
  "relationships": [
    {
      "type": "PLAYED_FOR",
      "from": "Nguyễn Quang Hải (sinh 1997)",
      "from_type": "player",
      "to": "Hà Nội",
      "to_type": "club"
    }
  ],
  "metadata": {
    "max_depth": 1,
    "total_entities": 25,
    "total_relationships": 50,
    "pages_visited": 30
  }
}
```

### Entity Types

| Type | Description | Example |
|------|-------------|---------|
| `player` | Football players | Nguyễn Quang Hải |
| `coach` | Coaches/managers | Park Hang-seo |
| `club` | Football clubs | Hà Nội FC |
| `national_team` | National teams | Đội tuyển Việt Nam |

### Relationship Types

| Type | Direction | Description |
|------|-----------|-------------|
| `PLAYED_FOR` | Player → Club | Player played for a club |
| `COACHED` | Coach → Club | Coach managed a club |
| `TRAINED_UNDER` | Player → Coach | Player was trained by a coach |
| `MEMBER_OF` | Player → National Team | Player is member of national team |

---

## Configuration

### Field Mappings

Edit `src/config.py` to customize Vietnamese → English field mappings:

```python
FIELD_MAPPINGS = {
    "ngày sinh": "birth_date",
    "chiều cao": "height",
    "vị trí": "position",
    # Add your custom mappings here
    "cân nặng": "weight",
    "chân thuận": "preferred_foot",
}
```

### Entity Keywords

Customize how entities are recognized:

```python
PLAYER_KEYWORDS = [
    "cầu thủ", "tiền đạo", "tiền vệ", "hậu vệ", "thủ môn",
    # Add more keywords
    "tuyển thủ", "cầu thủ quốc tế",
]
```

### Crawl Settings

```python
DEFAULT_MAX_DEPTH = 2           # Default crawl depth
REQUEST_DELAY = 1.0             # Seconds between requests
REQUEST_TIMEOUT = 10            # Request timeout in seconds
```

### Logging

```python
LOG_LEVEL = "INFO"              # DEBUG, INFO, WARNING, ERROR
JSON_OUTPUT_FILE = "data/vn_football_graph.json"
```

Or set via environment variable:
```bash
export LOG_LEVEL=DEBUG
python -m src.main
```

---

## Project Structure

```
VNFootballGraph/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration and constants
│   ├── crawl.py              # Wikipedia crawler
│   ├── parse_infobox.py      # Infobox parser
│   ├── graph_builder.py      # Graph builder utilities
│   └── main.py               # CLI entry point
├── data/
│   ├── .gitkeep
│   ├── checkpoint.json       # Auto-saved checkpoint (temporary)
│   └── vn_football_graph.json # Final output
├── logs/
│   ├── .gitkeep
│   └── crawl_*.log           # Timestamped log files
├── example.py                # Usage examples
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
└── README.md                # This file
```

---

## Advanced Features

### Checkpoint System

The crawler automatically saves progress every 5 pages. If interrupted (Ctrl+C or crash), simply run the same command again to resume:

```bash
# Start crawling
python -m src.main --depth 2

# Press Ctrl+C to interrupt
^C
⚠️  Interrupt received! Saving checkpoint...
✅ Checkpoint saved. You can resume later.

# Resume by running the same command
python -m src.main --depth 2
📂 Loaded checkpoint: 15 entities, 30 relationships
   Already visited: 20 pages
# Continues from where it left off
```

**Checkpoint file:** `data/checkpoint.json` (automatically deleted when crawl completes)

### Logging System

Every run creates a timestamped log file in `logs/`:

```
logs/
├── crawl_20251028_155900.log
├── crawl_20251028_160230.log
└── crawl_20251028_161545.log
```

**Console output:** INFO level only (clean, concise)  
**Log file:** All levels including DEBUG (detailed for debugging)

**View logs:**
```bash
# View latest log
cat logs/crawl_*.log | tail -100

# Follow log in real-time
tail -f logs/crawl_*.log

# Search for errors
grep "ERROR" logs/crawl_*.log
```

### Rate Limiting

The crawler respects Wikipedia's rate limits:
- 1 second delay between requests
- Custom User-Agent for identification
- Configurable timeout and delay

---

## Examples

### Example 1: Quick Test

```bash
# Crawl just one page to test
python -m src.main --depth 0 --seed "Nguyễn Quang Hải (sinh 1997)"
```

### Example 2: Analyze a Specific Player

```bash
# Crawl data about Văn Quyết and related pages
python -m src.main --depth 1 --seed "Văn Quyết"
```

### Example 3: Build Large Dataset

```bash
# Crawl depth 2 (may take 10-20 minutes)
python -m src.main --depth 2
```

### Example 4: Use in Python

```python
import json

# Load the graph data
with open('data/vn_football_graph.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Access entities and relationships
entities = data['entities']
relationships = data['relationships']
metadata = data['metadata']

# Filter players
players = [e for e in entities if e['type'] == 'player']
print(f"Total players: {len(players)}")

# Find all clubs a player played for
player_name = "Nguyễn Quang Hải (sinh 1997)"
clubs = [r['to'] for r in relationships 
         if r['from'] == player_name and r['type'] == 'PLAYED_FOR']
print(f"Clubs: {clubs}")
```

### Example 5: Convert to NetworkX

```python
import json
import networkx as nx

# Load data
with open('data/vn_football_graph.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Create directed graph
G = nx.DiGraph()

# Add nodes
for entity in data['entities']:
    G.add_node(entity['name'], 
               type=entity['type'],
               **entity['properties'])

# Add edges
for rel in data['relationships']:
    G.add_edge(rel['from'], rel['to'], 
               type=rel['type'])

print(f"Nodes: {G.number_of_nodes()}")
print(f"Edges: {G.number_of_edges()}")

# Analyze
print(f"Density: {nx.density(G)}")
print(f"Average degree: {sum(dict(G.degree()).values()) / G.number_of_nodes()}")
```

### Example 6: Export to CSV

```python
import json
import csv

with open('data/vn_football_graph.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Export nodes
with open('data/nodes.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'type', 'url'])
    for entity in data['entities']:
        writer.writerow([entity['name'], entity['type'], entity['url']])

# Export edges
with open('data/edges.csv', 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['from', 'to', 'type', 'from_type', 'to_type'])
    for rel in data['relationships']:
        writer.writerow([rel['from'], rel['to'], rel['type'], 
                        rel['from_type'], rel['to_type']])

print("Exported to nodes.csv and edges.csv")
```

---

## Troubleshooting

### Issue: `ModuleNotFoundError`

**Solution:** Make sure all dependencies are installed:
```bash
pip install -r requirements.txt
```

### Issue: Checkpoint file corrupted

**Solution:** Delete checkpoint and start fresh:
```bash
rm data/checkpoint.json
python -m src.main --depth 1
```

### Issue: Crawl is too slow

**Explanation:** The 1-second delay is intentional to respect Wikipedia's rate limits. Do not increase speed.

**Alternative:** Use smaller depth:
```bash
python -m src.main --depth 0  # Just seed page
```

### Issue: No infobox found for some pages

**Explanation:** Not all Wikipedia pages have infoboxes. This is normal. The crawler will skip these pages and continue.

### Issue: Log file not created

**Solution:** Make sure `logs/` directory exists:
```bash
mkdir -p logs
python -m src.main --depth 1
```

---

## Contributing

Contributions are welcome! Here are some ways you can contribute:

### Ideas for Contributions

- Add more entity types (stadiums, referees, competitions)
- Improve entity recognition algorithms
- Add temporal data (career timeline)
- Create visualization tools
- Add data validation and cleaning
- Support for other Wikipedia languages
- Web interface for browsing the graph

### How to Contribute

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Acknowledgments

- Built on top of the [Kapok](https://github.com/aaasen/kapok) Wikipedia graph project
- Uses [Vietnamese Wikipedia](https://vi.wikipedia.org) as data source
- Powered by [BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/) for HTML parsing

---

## Contact

For questions, issues, or suggestions, please [open an issue](https://github.com/yourusername/VNFootballGraph/issues) on GitHub.

---

## Project Status

**Current Status:** Active and ready to use

**Last Updated:** October 2025

**Python Version:** 3.8+

**Tested On:** Linux, macOS, Windows

---

<div align="center">

**Built for Vietnamese Football Analytics**

[Report Bug](https://github.com/yourusername/VNFootballGraph/issues) · [Request Feature](https://github.com/yourusername/VNFootballGraph/issues)

</div>
