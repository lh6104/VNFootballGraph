#!/usr/bin/env python3
"""
Test career status detection (active vs retired players)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.crawl import WikiCrawler
from src import config

# Test cases: [page_title, expected_status, description]
TEST_CASES = [
    # Active players
    ("Nguyễn_Hoàng_Đức_(cầu_thủ_bóng_đá)", "active", "Current midfielder"),
    ("Nguyễn_Văn_Toàn_(cầu_thủ_bóng_đá)", "active", "Current forward"),
    ("Nguyễn_Văn_Hoàng_(cầu_thủ_bóng_đá)", "active", "Current goalkeeper"),
    
    # Retired/Former players
    ("Lê_Công_Vinh", "retired", "Famous retired striker"),
    
    # Former players who became coaches (should be 'retired' as players)
    ("Trần_Công_Minh", "retired", "Former player, now coach"),
]

def extract_career_status(page_data):
    """
    Extract career status from page data.
    
    Returns:
        str: 'active', 'retired', or 'unknown'
    """
    first_para = page_data.get('first_paragraph', '').lower()
    infobox_text = page_data.get('infobox_text', '').lower()
    
    # Retired indicators
    retired_keywords = [
        'cựu cầu thủ', 'cựu tuyển thủ', 'cựu danh thủ',
        'đã giải nghệ', 'treo giày', 'giải nghệ năm',
        'kết thúc sự nghiệp', 'nghỉ thi đấu',
        'từng thi đấu', 'từng khoác áo',
        'former player', 'retired', 'former footballer'
    ]
    
    # Active indicators
    active_keywords = [
        'đang thi đấu', 'đang khoác áo', 'hiện đang',
        'hiện tại thi đấu', 'currently plays', 'plays for'
    ]
    
    # Check for retired
    if any(keyword in first_para for keyword in retired_keywords):
        return 'retired'
    
    # Check for active
    if any(keyword in first_para for keyword in active_keywords):
        return 'active'
    
    # Check infobox for current team
    if 'đội hiện nay' in infobox_text or 'current team' in infobox_text:
        return 'active'
    
    return 'unknown'

def extract_retirement_year(page_data):
    """
    Extract retirement year if available.
    
    Returns:
        str or None: Year of retirement
    """
    import re
    
    first_para = page_data.get('first_paragraph', '')
    infobox_text = page_data.get('infobox_text', '')
    
    text = first_para + ' ' + infobox_text
    
    # Pattern: "giải nghệ năm 2020", "retired in 2020"
    patterns = [
        r'giải nghệ năm (\d{4})',
        r'treo giày năm (\d{4})',
        r'retired in (\d{4})',
        r'kết thúc sự nghiệp năm (\d{4})'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1)
    
    return None

def main():
    print("="*80)
    print("CAREER STATUS DETECTION TEST")
    print("="*80)
    
    crawler = WikiCrawler(max_depth=1)
    
    passed = 0
    failed = 0
    
    for page_title, expected_status, description in TEST_CASES:
        print(f"\n{'='*80}")
        print(f"Testing: {page_title}")
        print(f"Description: {description}")
        print(f"Expected: {expected_status}")
        
        # Fetch page
        try:
            page_data = crawler.fetch_page(page_title)
            if not page_data:
                print(f"⚠️  SKIP | Could not fetch page")
                continue
            
            # Extract career status
            detected_status = extract_career_status(page_data)
            retirement_year = extract_retirement_year(page_data)
            
            # Show first paragraph snippet
            first_para = page_data.get('first_paragraph', '')[:200]
            print(f"\nFirst paragraph snippet:")
            print(f"  {first_para}...")
            
            print(f"\nDetected status: {detected_status}")
            if retirement_year:
                print(f"Retirement year: {retirement_year}")
            
            # Check result
            if detected_status == expected_status:
                print(f"✅ PASS")
                passed += 1
            else:
                print(f"❌ FAIL | Expected: {expected_status}, Got: {detected_status}")
                failed += 1
                
        except Exception as e:
            print(f"❌ ERROR | {e}")
            failed += 1
    
    # Summary
    print(f"\n{'='*80}")
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(TEST_CASES)} tests")
    print(f"Success rate: {passed/len(TEST_CASES)*100:.1f}%")
    print(f"{'='*80}")
    
    if failed == 0:
        print("\n✅ ALL TESTS PASSED")
        return 0
    else:
        print(f"\n❌ {failed} TESTS FAILED")
        return 1

if __name__ == "__main__":
    sys.exit(main())
