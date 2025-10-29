# ⚽ VN Football Graph

**Xây dựng mạng lưới bóng đá Việt Nam từ Wikipedia tiếng Việt**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.x-green.svg)](https://neo4j.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📋 Tổng quan

**VN Football Graph** là hệ thống Data Engineering pipeline thu thập, xử lý và xây dựng mạng lưới quan hệ bóng đá Việt Nam từ Wikipedia tiếng Việt. Project tập trung vào việc xây dựng một graph database chất lượng cao với các nodes và edges có ý nghĩa rõ ràng.

### 🎯 Mục tiêu

- Thu thập >1,000 entities từ Wikipedia tiếng Việt
- Xây dựng graph network với nodes (Cầu thủ, HLV, CLB, Đội tuyển) và edges (PLAYED_FOR, COACHED, TRAINED_UNDER, MEMBER_OF)
- Phát hiện tự động cầu thủ Việt kiều/nhập tịch/gốc Việt
- Cung cấp dữ liệu chất lượng cao cho phân tích và truy vấn

### ✨ Đặc điểm nổi bật

- **Data Engineering Pipeline hoàn chỉnh**: Crawl → Extract → Transform → Load
- **Smart Filtering**: 3-tier strategy (DROP/PRIORITY/KEEP) với 72% efficiency
- **Vietnamese Diaspora Detection**: Tự động phát hiện cầu thủ Việt kiều với 70% accuracy
- **High Data Quality**: 74% completeness cho các fields quan trọng
- **Scalable Architecture**: Modular design, dễ mở rộng

---

## 🏗️ Kiến trúc

### Graph Schema

```
┌─────────┐     PLAYED_FOR      ┌──────┐
│ Player  │────────────────────>│ Club │
└─────────┘                     └──────┘
     │                               ▲
     │ TRAINED_UNDER                 │
     │                               │ COACHED
     ▼                               │
┌─────────┐                     ┌───────┐
│ Coach   │─────────────────────┤       │
└─────────┘                     └───────┘
     │
     │ MEMBER_OF
     ▼
┌──────────────┐
│ NationalTeam │
└──────────────┘
```

### Nodes

| Type | Properties | Example |
|------|------------|---------|
| **Player** | name, birth_date, position, height, is_vietnamese_diaspora | Nguyễn Quang Hải |
| **Coach** | name, birth_date, nationality | Park Hang-seo |
| **Club** | name, founded, stadium, league | Hà Nội FC |
| **NationalTeam** | name, level, confederation | Đội tuyển Việt Nam |

### Edges

| Type | From → To | Properties | Meaning |
|------|-----------|------------|---------|
| **PLAYED_FOR** | Player → Club | years, position | Cầu thủ chơi cho CLB |
| **COACHED** | Coach → Club | years, achievements | HLV dẫn dắt CLB |
| **TRAINED_UNDER** | Player → Coach | years, team | Cầu thủ được HLV huấn luyện |
| **MEMBER_OF** | Player → NationalTeam | years, caps, goals | Cầu thủ khoác áo đội tuyển |

---

## 🚀 Cài đặt

### Requirements

- Python 3.10+
- Neo4j 5.x (optional, for graph database)
- Conda (recommended)

### Setup

```bash
# Clone repository
git clone https://github.com/[username]/VNFootballGraph.git
cd VNFootballGraph

# Create conda environment
conda create -n datamining python=3.10
conda activate datamining

# Install dependencies
pip install -r requirements.txt

# (Optional) Setup Neo4j
docker run -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:5.13
```

---

## 💻 Sử dụng

### Basic Crawling

```bash
# Crawl depth 1 (quick test)
python -m src.main --depth 1

# Crawl depth 2 (recommended for >1,000 nodes)
python -m src.main --depth 2

# Custom seed page
python -m src.main --seed "Đội_tuyển_bóng_đá_quốc_gia_Việt_Nam" --depth 2
```

### Output Formats

#### 1. JSON Output (Default)

```bash
python -m src.main --depth 1
# → data/vn_football_graph.json
```

**Contains:**
- 251 entities (players, clubs, coaches, national teams)
- 611 relationships (PLAYED_FOR, MEMBER_OF, COACHED, TRAINED_UNDER)
- Metadata (statistics, diaspora info)

#### 2. CSV Export (3 Formats)

**Format A: Normalized (Recommended for Analysis)**
```bash
python scripts/export_to_csv.py --format normalized
```

**Output files:**
```
data/csv/
├── players.csv                        (132 players)
├── clubs.csv                          (53 clubs)
├── coaches.csv                        (50 coaches)
├── national_teams.csv                 (16 teams)
├── relationships.csv                  (611 relationships) ⭐
└── vietnamese_diaspora_players.csv    (10 players)
```

**Use case:** Data analysis, SQL queries, pandas, Excel

---

**Format B: Graph (Neo4j Import)**
```bash
python scripts/export_to_csv.py --format graph
```

**Output structure:**
```
data/csv/
├── nodes/
│   ├── players.csv       (Neo4j format: :ID, properties)
│   ├── clubs.csv
│   ├── coaches.csv
│   └── national_teams.csv
└── relationships/
    ├── played_for.csv    (Neo4j format: :START_ID, :END_ID, :TYPE)
    ├── member_of.csv
    ├── coached.csv
    └── trained_under.csv
```

**Use case:** Direct Neo4j import

---

**Format C: Flat (Simple)**
```bash
python scripts/export_to_csv.py --format flat
```

**Output:** `data/csv/players_flat.csv` (single file, all player info)

**Use case:** Quick Excel analysis

---

**Export All Formats**
```bash
python scripts/export_to_csv.py --format all
```

---

#### Quick Comparison

| Feature | Normalized | Graph | Flat |
|---------|------------|-------|------|
| **Files** | 6 files | 2 folders | 1 file |
| **Relationships** | ✅ relationships.csv | ✅ Separate files | ❌ |
| **Use case** | Analysis, SQL | Neo4j import | Excel |
| **Recommended** | ✅ **Yes** | For Neo4j only | Quick view |

**💡 Recommendation:** Use `--format normalized` for most cases (analysis, báo cáo)

---

### Neo4j Integration

#### Option 1: Direct from Python

```bash
# Configure Neo4j connection
export NEO4J_URI=bolt://localhost:7687
export NEO4J_USER=neo4j
export NEO4J_PASSWORD=password

# Run with Neo4j output
python -m src.main --depth 1 --output both
```

#### Option 2: Import from CSV

```bash
# 1. Export graph format
python scripts/export_to_csv.py --format graph

# 2. Import to Neo4j
neo4j-admin import \
  --nodes=Player=data/csv/nodes/players.csv \
  --nodes=Club=data/csv/nodes/clubs.csv \
  --nodes=Coach=data/csv/nodes/coaches.csv \
  --nodes=NationalTeam=data/csv/nodes/national_teams.csv \
  --relationships=data/csv/relationships/played_for.csv \
  --relationships=data/csv/relationships/member_of.csv \
  --relationships=data/csv/relationships/coached.csv \
  --relationships=data/csv/relationships/trained_under.csv
```

---

## 📊 Kết quả (Depth 1)

### Performance Metrics

| Metric | Value |
|--------|-------|
| **Pages visited** | 349 |
| **Entities parsed** | 251 |
| **Crawl efficiency** | 71.9% |
| **Crawl time** | 7 min 8 sec |
| **Speed** | 1.23 sec/page |

### Entity Distribution

| Entity Type | Count | Percentage |
|-------------|-------|------------|
| Player | 132 | 52.6% |
| Club | 53 | 21.1% |
| Coach | 50 | 19.9% |
| National Team | 16 | 6.4% |
| **Total** | **251** | **100%** |

### Relationships (Graph Network)

| Relationship Type | Count | Description |
|-------------------|-------|-------------|
| **PLAYED_FOR** | 391 | Player → Club |
| **MEMBER_OF** | 210 | Player → National Team |
| **COACHED** | 9 | Coach → Club |
| **TRAINED_UNDER** | 1 | Player → Coach |
| **Total** | **611** | **Complete graph network** ✅ |

**Sample relationships:**
```
(Nguyễn Quang Hải) -[PLAYED_FOR]-> (Hà Nội FC)
(Nguyễn Quang Hải) -[PLAYED_FOR]-> (Pau)
(Nguyễn Quang Hải) -[MEMBER_OF]-> (Việt Nam)
```

### Data Quality

| Field | Coverage |
|-------|----------|
| birth_date | 74.2% |
| birth_place | 74.2% |
| position | 75.0% |
| height | 72.7% |

### Vietnamese Diaspora

- **Total identified**: 7 players (70% accuracy)
- **Notable players**:
  - Filip Nguyễn (Thụy Điển, gốc Việt)
  - Rafaelson (Brazil, nhập tịch)
  - Jason Quang-Vinh Pendant (Pháp, gốc Việt)

---

## 🔧 Configuration

### Smart Filtering

Edit `src/config.py` to customize filtering strategy:

```python
# DROP keywords - Skip these pages
DROP_KEYWORDS = [
    "phim", "xã", "huyện", "bóng rổ", "cầu lông"
]

# PRIORITY keywords - Always keep
PRIORITY_KEYWORDS = [
    "v.league 1", "đội tuyển bóng đá quốc gia việt nam"
]

# KEEP keywords - Keep if match
KEEP_KEYWORDS = [
    "bóng đá", "cầu thủ", "clb", "đội tuyển"
]
```

### Vietnamese Diaspora Keywords

```python
VIETNAMESE_DIASPORA_KEYWORDS = [
    "việt kiều", "nhập tịch", "gốc việt",
    "overseas vietnamese", "naturalized", "dual citizenship"
]
```

---

## 📁 Project Structure

```
VNFootballGraph/
├── src/
│   ├── main.py              # Main orchestration
│   ├── crawl.py             # Web crawler (BFS, filtering)
│   ├── parse_infobox.py     # Infobox parser & relationship extraction
│   ├── graph_builder.py     # Neo4j integration
│   └── config.py            # Configuration & keywords
├── scripts/
│   └── export_to_csv.py     # CSV export utility
├── data/
│   ├── vn_football_graph.json    # JSON output
│   └── csv/                      # CSV exports
├── logs/                    # Timestamped logs
├── README.md
├── STRATEGY.md              # Technical strategy & decisions
└── requirements.txt
```

---

## 🎓 Technical Stack

### Data Engineering

- **Crawling**: Python, requests, BeautifulSoup4
- **Processing**: pandas, json, re
- **Pipeline**: Modular ETL architecture
- **Storage**: JSON, CSV, Neo4j

### Key Features

1. **BFS Crawling** with depth limit
2. **Rate Limiting** (1s delay)
3. **Checkpoint System** (save every 5 pages)
4. **Smart Filtering** (3-tier strategy)
5. **Multi-source Entity Detection** (infobox + content)
6. **Career History Parsing** (year ranges)
7. **Diaspora Detection** (20+ keywords)

---

## 📈 Roadmap

### Short-term (1-2 weeks)

- [ ] Fix relationship extraction (currently 0 edges)
- [ ] Crawl depth 2 (target: >1,000 nodes)
- [ ] Preprocessing pipeline for misclassified entities
- [ ] Improve diaspora detection accuracy (>80%)

### Mid-term (1-2 months)

- [ ] Add entity types: Tournament, Award, Season
- [ ] Graph algorithms: PageRank, Community Detection
- [ ] Web visualization interface
- [ ] Real-time updates from Wikipedia

### Long-term (3-6 months)

- [ ] Machine Learning for entity classification
- [ ] Recommendation system (similar players)
- [ ] Predictive analytics (transfer predictions)
- [ ] Multi-language support

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details

---

## 👥 Authors

- **Data Engineering Team** - Initial work

---

## 📚 Documentation

- **[STRATEGY.md](STRATEGY.md)** - Technical strategy, architecture decisions, and optimization details
- **Code Documentation** - Inline comments and docstrings

---

## 🙏 Acknowledgments

- Wikipedia tiếng Việt for data source
- Neo4j for graph database
- BeautifulSoup for HTML parsing
- Python community for excellent libraries

---

## 📞 Contact

For questions or feedback, please open an issue on GitHub.

---

**⚽ Built with ❤️ for Vietnamese Football**
