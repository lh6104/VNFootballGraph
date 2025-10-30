#!/bin/bash
# Multi-seed crawler for better coverage with lower depth

# Colors
BLUE='\033[0;34m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}🚀 VN Football Graph Crawler${NC}"
echo -e "${BLUE}   Multi-Seed Strategy${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Parse arguments
DEPTH=${1:-2}  # Default depth = 2 (balanced for multi-seed)

# Optimized seed list for maximum coverage (10 seeds)
# Balanced: 2 coaches, 4 players (male/female, active/retired), 2 teams, 2 clubs
SEED_PAGES=(
    # === Coaches (2) ===
    "Park_Hang-seo"                              # Foreign coach (Korean), VN national team
    "Mai_Đức_Chung"                              # Vietnamese coach, women's team
    
    # === Players (4) ===
    "Nguyễn_Quang_Hải_(sinh_1997)"               # Star midfielder, current generation
    "Nguyễn_Công_Phượng"                         # Star forward, HAGL academy
    "Lê_Công_Vinh"                               # Retired legend, top scorer
    "Huỳnh_Như"                                  # Female star player, World Cup 2023
    
    # === National Teams (2) ===
    "Đội_tuyển_bóng_đá_quốc_gia_Việt_Nam"        # Men's national team hub
    "Đội_tuyển_bóng_đá_nữ_quốc_gia_Việt_Nam"     # Women's national team hub
    
    # === Clubs (2) ===
    "Câu_lạc_bộ_bóng_đá_Hoàng_Anh_Gia_Lai"       # Top academy club (HAGL)
    "Câu_lạc_bộ_bóng_đá_Hà_Nội"                  # Top V.League club
)

echo -e "${GREEN}📊 Configuration:${NC}"
echo -e "   Depth:  ${YELLOW}$DEPTH${NC}"
echo -e "   Seeds:  ${YELLOW}${#SEED_PAGES[@]}${NC} curated pages"
echo -e "   Strategy: ${YELLOW}Multi-seed (wide coverage)${NC}"
echo ""

echo -e "${CYAN}🌱 Seed pages:${NC}"
for seed in "${SEED_PAGES[@]}"; do
    echo -e "   - $seed"
done
echo ""

# Remove old checkpoint
if [ -f "data/checkpoint.json" ]; then
    echo -e "${YELLOW}⚠️  Removing old checkpoint...${NC}"
    rm -f data/checkpoint.json
fi

# Create temp directory for individual results
TEMP_DIR="data/temp_multi_seed"
mkdir -p "$TEMP_DIR"

echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}🏃 Starting multi-seed crawl...${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Crawl each seed
for i in "${!SEED_PAGES[@]}"; do
    seed="${SEED_PAGES[$i]}"
    num=$((i+1))
    
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${CYAN}🌱 Seed $num/${#SEED_PAGES[@]}: ${YELLOW}$seed${NC}"
    echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    
    # Clean checkpoint before each seed
    rm -f data/checkpoint.json
    
    # Run crawler (suppress verbose output)
    stdbuf -oL -eL conda run -n datamining python -u -m src.main --depth "$DEPTH" --seed "$seed" 2>&1 | \
        grep -E "(Crawling:|Processed:|DEPTH|extracted|Success|ERROR)" || true
    
    # Save result with seed index
    if [ -f "data/vn_football_graph.json" ]; then
        cp data/vn_football_graph.json "$TEMP_DIR/seed_${num}.json"
        echo -e "${GREEN}✅ Saved results for seed $num${NC}"
    else
        echo -e "${RED}❌ No results for seed $num${NC}"
    fi
    
    echo ""
done

echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📊 Merging results...${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Merge all results using Python
python3 << 'PYTHON_SCRIPT'
import json
import os
from collections import defaultdict

temp_dir = "data/temp_multi_seed"
merged_entities = {}
merged_relationships = []
seen_rels = set()

# Load all seed results
seed_count = 0
for i in range(1, 100):  # Support up to 100 seeds
    file_path = f"{temp_dir}/seed_{i}.json"
    if not os.path.exists(file_path):
        continue
    
    seed_count += 1
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Merge entities (deduplicate by name)
    for entity in data.get('entities', []):
        name = entity['name']
        if name not in merged_entities:
            merged_entities[name] = entity
    
    # Merge relationships (deduplicate)
    for rel in data.get('relationships', []):
        rel_key = (rel['type'], rel['from'], rel['to'])
        if rel_key not in seen_rels:
            seen_rels.add(rel_key)
            merged_relationships.append(rel)

# Save merged result
merged_data = {
    'entities': list(merged_entities.values()),
    'relationships': merged_relationships
}

with open('data/vn_football_graph.json', 'w', encoding='utf-8') as f:
    json.dump(merged_data, f, ensure_ascii=False, indent=2)

print(f"✅ Merged {len(merged_entities)} unique entities from {seed_count} seeds")
print(f"✅ Merged {len(merged_relationships)} unique relationships")
PYTHON_SCRIPT

# Analyze final results
echo ""
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${CYAN}📊 FINAL RESULTS${NC}"
echo -e "${MAGENTA}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

python3 << 'PYTHON_SCRIPT'
import json

with open('data/vn_football_graph.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

entities = data.get('entities', [])
relationships = data.get('relationships', [])

# Count by type
by_type = {}
by_gender = {'male': 0, 'female': 0, 'unknown': 0}

for e in entities:
    t = e.get('type', 'unknown')
    by_type[t] = by_type.get(t, 0) + 1
    
    gender = e.get('properties', {}).get('gender', 'unknown')
    by_gender[gender] = by_gender.get(gender, 0) + 1

print(f"\n📈 Total entities: {len(entities)}")
print(f"📈 Total relationships: {len(relationships)}")

print(f"\n🔍 By type:")
for t, count in sorted(by_type.items(), key=lambda x: -x[1]):
    print(f"   {t:15s}: {count}")

print(f"\n⚧ By gender:")
print(f"   👨 Male:    {by_gender['male']}")
print(f"   👩 Female:  {by_gender['female']}")
print(f"   ❓ Unknown: {by_gender['unknown']}")

# Check coverage
players = [e for e in entities if e.get('type') == 'player']
coaches = [e for e in entities if e.get('type') == 'coach']
male_players = [e for e in players if e.get('properties', {}).get('gender') == 'male']
female_players = [e for e in players if e.get('properties', {}).get('gender') == 'female']

print(f"\n👤 Players: {len(players)} total")
print(f"   👨 Male: {len(male_players)}")
print(f"   👩 Female: {len(female_players)}")

print(f"\n👔 Coaches: {len(coaches)} total")
PYTHON_SCRIPT

# Cleanup
rm -rf "$TEMP_DIR"

echo ""
echo -e "${BLUE}================================${NC}"
echo -e "${GREEN}✅ Multi-seed crawl complete!${NC}"
echo -e "${BLUE}================================${NC}"
echo ""
echo -e "${CYAN}📁 Output: data/vn_football_graph.json${NC}"
echo -e "${CYAN}📝 Logs: logs/${NC}"
echo ""
