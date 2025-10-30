#!/usr/bin/env python3
"""
Test women's football detection
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.crawl import WikiCrawler

# Test cases: [page_title, expected_gender, description]
TEST_CASES = [
    # Women's football
    ("Huỳnh_Như", "female", "Famous Vietnamese women's player"),
    ("Đội_tuyển_bóng_đá_nữ_quốc_gia_Việt_Nam", "female", "Vietnam women's national team"),
    
    # Men's football (for comparison)
    ("Nguyễn_Quang_Hải_(sinh_1997)", "male", "Vietnamese men's player"),
    ("Nguyễn_Hoàng_Đức_(cầu_thủ_bóng_đá)", "male", "Vietnamese men's player"),
]

def extract_gender(page_data):
    """Extract gender from page data."""
    title = page_data.get('title', '').lower()
    first_para = page_data.get('first_paragraph', '').lower()
    infobox_text = page_data.get('infobox_text', '').lower()
    categories = [c.lower() for c in page_data.get('categories', [])]
    
    text = title + ' ' + first_para + ' ' + infobox_text + ' ' + ' '.join(categories)
    
    # Female indicators
    female_keywords = [
        'cầu thủ nữ', 'tuyển thủ nữ', 'danh thủ nữ',
        'huấn luyện viên nữ', 'hlv nữ',
        'bóng đá nữ', 'đội tuyển nữ',
        'women\'s football', 'women\'s soccer', 'women footballer',
        'female player', 'female footballer', 'female coach',
        'women\'s national team', 'women\'s team',
        'ladies football', 'ladies team',
        'she is', 'she was', 'she plays', 'her career'
    ]
    
    # Male indicators
    male_keywords = [
        'he is', 'he was', 'he plays', 'his career',
        'anh là', 'ông là'
    ]
    
    if any(keyword in text for keyword in female_keywords):
        return 'female'
    
    if any(keyword in text for keyword in male_keywords):
        return 'male'
    
    return 'unknown'

def main():
    print("="*80)
    print("WOMEN'S FOOTBALL DETECTION TEST")
    print("="*80)
    
    crawler = WikiCrawler(max_depth=1)
    
    passed = 0
    failed = 0
    
    for page_title, expected_gender, description in TEST_CASES:
        print(f"\n{'='*80}")
        print(f"Testing: {page_title}")
        print(f"Description: {description}")
        print(f"Expected gender: {expected_gender}")
        
        try:
            page_data = crawler.fetch_page(page_title)
            if not page_data:
                print(f"⚠️  SKIP | Could not fetch page")
                continue
            
            # Extract gender
            detected_gender = extract_gender(page_data)
            
            # Show first paragraph snippet
            first_para = page_data.get('first_paragraph', '')[:200]
            print(f"\nFirst paragraph snippet:")
            print(f"  {first_para}...")
            
            print(f"\nDetected gender: {detected_gender}")
            
            # Check result
            if detected_gender == expected_gender:
                print(f"✅ PASS")
                passed += 1
            else:
                print(f"❌ FAIL | Expected: {expected_gender}, Got: {detected_gender}")
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
