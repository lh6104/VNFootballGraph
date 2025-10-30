"""
Test coach detection, especially for foreign coaches working in Vietnam.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.filters_advanced import AdvancedFilter
from src.crawl import WikiCrawler
from src import config


def test_coach_detection():
    """Test detection of coaches (Vietnamese and foreign)."""
    
    crawler = WikiCrawler(max_depth=1, use_advanced_filter=True)
    filter_instance = AdvancedFilter()
    
    print("=" * 80)
    print("COACH DETECTION TEST")
    print("=" * 80)
    print()
    
    # Test cases: (title, text, categories, expected_type, description)
    test_cases = [
        # Vietnamese coaches
        (
            "Trần_Công_Minh",
            "Trần Công Minh là huấn luyện viên bóng đá người Việt Nam, từng dẫn dắt nhiều câu lạc bộ tại V.League.",
            ["Huấn luyện viên bóng đá Việt Nam"],
            "coach",
            "Vietnamese coach"
        ),
        
        # Foreign coach - Park Hang-seo
        (
            "Park_Hang-seo",
            "Park Hang-seo là huấn luyện viên bóng đá người Hàn Quốc, từng dẫn dắt đội tuyển bóng đá quốc gia Việt Nam từ năm 2017 đến 2023.",
            ["Huấn luyện viên bóng đá Hàn Quốc", "Huấn luyện viên đội tuyển Việt Nam"],
            "coach",
            "Foreign coach (Korean) working in Vietnam"
        ),
        
        # Foreign coach - Philippe Troussier
        (
            "Philippe_Troussier",
            "Philippe Troussier is a French football manager who was appointed as head coach of the Vietnam national football team in 2023.",
            ["French football managers", "Vietnam national football team managers"],
            "coach",
            "Foreign coach (French) working in Vietnam"
        ),
        
        # Assistant coach
        (
            "Lee_Young-jin",
            "Lee Young-jin là trợ lý huấn luyện viên người Hàn Quốc, làm việc tại Việt Nam cùng Park Hang-seo.",
            ["Trợ lý huấn luyện viên"],
            "coach",
            "Assistant coach (Korean) in Vietnam"
        ),
        
        # Player (should NOT be coach)
        (
            "Nguyễn_Quang_Hải",
            "Nguyễn Quang Hải là cầu thủ bóng đá người Việt Nam, thi đấu ở vị trí tiền vệ.",
            ["Cầu thủ bóng đá Việt Nam"],
            "player",
            "Player (not coach)"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for title, text, categories, expected_type, description in test_cases:
        # Create mock page data
        page_data = {
            'title': title,
            'first_paragraph': text,
            'infobox_text': text,
            'categories': categories,
        }
        
        # Detect entity type
        entity_type = crawler.get_page_type(page_data)
        
        # Check relevance score
        score, layer = filter_instance.evaluate_page(
            title=title,
            text=text,
            categories=categories
        )
        
        status = "✅ PASS" if entity_type == expected_type else "❌ FAIL"
        
        if entity_type == expected_type:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | {title}")
        print(f"       Expected: {expected_type} | Actual: {entity_type}")
        print(f"       Relevance: layer={layer}, score={score}")
        print(f"       Description: {description}")
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"Success rate: {passed/len(test_cases)*100:.1f}%")
    print("=" * 80)
    
    return failed == 0


def test_semantic_patterns_coaches():
    """Test semantic pattern matching for coaches."""
    
    filter_instance = AdvancedFilter()
    
    print("\n" + "=" * 80)
    print("SEMANTIC PATTERN TEST - COACHES")
    print("=" * 80)
    print()
    
    test_texts = [
        ("Park Hang-seo là huấn luyện viên bóng đá người Hàn Quốc.", True, "Vietnamese coach pattern"),
        ("Philippe Troussier is a football coach working in Vietnam.", True, "English coach pattern"),
        ("Ông được bổ nhiệm làm huấn luyện viên trưởng đội tuyển Việt Nam.", True, "Appointment pattern"),
        ("He was appointed as head coach of Vietnam national team.", True, "English appointment"),
        ("Nhà cầm quân người Hàn Quốc dẫn dắt đội tuyển Việt Nam.", True, "Tactician pattern"),
        ("The manager signed a contract to coach in Vietnam.", True, "Contract pattern"),
        ("Nguyễn Văn A là cầu thủ bóng đá.", False, "Player (not coach)"),
    ]
    
    passed = 0
    failed = 0
    
    for text, should_match, description in test_texts:
        # Check if any pattern matches
        matched = False
        for pattern in filter_instance.compiled_patterns:
            if pattern.search(text.lower()):
                matched = True
                break
        
        status = "✅ PASS" if matched == should_match else "❌ FAIL"
        
        if matched == should_match:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | {description}")
        print(f"       Text: {text[:70]}...")
        print(f"       Expected match: {should_match} | Actual: {matched}")
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_texts)} tests")
    print("=" * 80)
    
    return failed == 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test coach detection")
    parser.add_argument("--detection", "-d", action="store_true",
                       help="Test entity type detection")
    parser.add_argument("--semantic", "-s", action="store_true",
                       help="Test semantic patterns")
    parser.add_argument("--all", "-a", action="store_true",
                       help="Run all tests")
    
    args = parser.parse_args()
    
    # If no specific test selected, run all
    if not any([args.detection, args.semantic, args.all]):
        args.all = True
    
    all_passed = True
    
    if args.detection or args.all:
        if not test_coach_detection():
            all_passed = False
    
    if args.semantic or args.all:
        if not test_semantic_patterns_coaches():
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    sys.exit(0 if all_passed else 1)
