#!/usr/bin/env python3
"""Test nationality extraction."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.nationality_extractor import extract_nationality

print("=" * 80)
print("NATIONALITY EXTRACTION TEST")
print("=" * 80)
print()

# Test cases
test_cases = [
    # Vietnamese player
    {
        "name": "Nguyễn Quang Hải",
        "properties": {"birth_place": "Đông Anh, Hà Nội, Việt Nam"},
        "categories": ["Cầu thủ bóng đá Việt Nam"],
        "text": "Nguyễn Quang Hải là cầu thủ bóng đá người Việt Nam",
        "expected": "Vietnam"
    },
    # Korean coach
    {
        "name": "Park Hang-seo",
        "properties": {"birth_place": "Seoul, Hàn Quốc"},
        "categories": ["Huấn luyện viên bóng đá Hàn Quốc"],
        "text": "Park Hang-seo là huấn luyện viên người Hàn Quốc",
        "expected": "South Korea"
    },
    # French coach
    {
        "name": "Philippe Troussier",
        "properties": {"birth_place": "Paris, France"},
        "categories": ["French football managers"],
        "text": "Philippe Troussier is a French football manager",
        "expected": "France"
    },
    # Thai player
    {
        "name": "Chanathip Songkrasin",
        "properties": {"birth_place": "Bangkok, Thailand"},
        "categories": ["Thai footballers"],
        "text": "",
        "expected": "Thailand"
    },
    # Japanese player
    {
        "name": "Keisuke Honda",
        "properties": {"birth_place": "Osaka, Nhật Bản"},
        "categories": ["Cầu thủ bóng đá Nhật Bản"],
        "text": "",
        "expected": "Japan"
    },
]

passed = 0
failed = 0

for test in test_cases:
    nationality = extract_nationality(
        properties=test["properties"],
        categories=test["categories"],
        text=test["text"]
    )
    
    expected = test["expected"]
    status = "✅ PASS" if nationality == expected else "❌ FAIL"
    
    if nationality == expected:
        passed += 1
    else:
        failed += 1
    
    print(f"{status} | {test['name']}")
    print(f"       Expected: {expected}")
    print(f"       Got:      {nationality}")
    print(f"       Source:   birth_place={test['properties'].get('birth_place', 'N/A')}")
    print()

print("=" * 80)
print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
print(f"Success rate: {passed/len(test_cases)*100:.1f}%")
print("=" * 80)
