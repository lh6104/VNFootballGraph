"""
Comprehensive test suite for the advanced filtering system.
Tests relevance scoring, layer assignment, and multi-signal evaluation.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.filters_advanced import AdvancedFilter, evaluate_page_simple, is_noise_page
from src import config


def test_relevance_scoring():
    """Test the relevance scoring system with various scenarios."""
    
    filter_instance = AdvancedFilter()
    
    print("=" * 80)
    print("ADVANCED FILTERING SYSTEM TEST - Relevance Scoring")
    print("=" * 80)
    print()
    
    # Test cases: (title, text, categories, expected_layer, description)
    test_cases = [
        # HIGH QUALITY - Should be CORE
        (
            "Nguyễn_Quang_Hải_(sinh_1997)",
            "Nguyễn Quang Hải là cầu thủ bóng đá người Việt Nam, thi đấu ở vị trí tiền vệ cho câu lạc bộ Pau và đội tuyển quốc gia Việt Nam.",
            ["Cầu thủ bóng đá Việt Nam", "Sinh năm 1997"],
            "core",
            "Famous Vietnamese player with rich context"
        ),
        (
            "Park_Hang-seo",
            "Park Hang-seo là huấn luyện viên bóng đá người Hàn Quốc, từng dẫn dắt đội tuyển bóng đá quốc gia Việt Nam.",
            ["Huấn luyện viên bóng đá", "Huấn luyện viên Hàn Quốc"],
            "core",
            "Famous coach with valid categories"
        ),
        (
            "Câu_lạc_bộ_bóng_đá_Hà_Nội",
            "Câu lạc bộ bóng đá Hà Nội là một câu lạc bộ bóng đá chuyên nghiệp tại Việt Nam, thi đấu tại V.League 1.",
            ["Câu lạc bộ bóng đá Việt Nam", "V.League"],
            "core",
            "Major Vietnamese football club"
        ),
        
        # MEDIUM QUALITY - Should be CONTEXT
        (
            "Giải_bóng_đá_vô_địch_quốc_gia_Việt_Nam",
            "Giải bóng đá vô địch quốc gia Việt Nam là giải đấu bóng đá hàng đầu tại Việt Nam.",
            ["Giải bóng đá Việt Nam"],
            "context",
            "Tournament page - relevant but not core entity"
        ),
        (
            "Sân_vận_động_Mỹ_Đình",
            "Sân vận động Mỹ Đình là sân vận động lớn nhất Việt Nam, thường xuyên tổ chức các trận đấu bóng đá.",
            ["Sân vận động Việt Nam"],
            "context",
            "Stadium - related but not core"
        ),
        
        # LOW QUALITY - Should be SKIP
        (
            "Lịch_sử_Việt_Nam",
            "Lịch sử Việt Nam là lịch sử của dân tộc Việt Nam và các chính thể Việt Nam.",
            ["Lịch sử Việt Nam", "Lịch sử châu Á"],
            "skip",
            "History page - irrelevant"
        ),
        (
            "Kinh_tế_Việt_Nam",
            "Kinh tế Việt Nam là nền kinh tế đang phát triển của Việt Nam.",
            ["Kinh tế Việt Nam", "Kinh tế châu Á"],
            "skip",
            "Economy page - irrelevant"
        ),
        (
            "Tỉnh_Hà_Nội",
            "Hà Nội là thủ đô của Việt Nam, là trung tâm chính trị, văn hóa.",
            ["Tỉnh thành Việt Nam", "Địa lý Việt Nam"],
            "skip",
            "Geography page - irrelevant"
        ),
        (
            "File:Example.jpg",
            "",
            [],
            "skip",
            "Media file - should be blocked immediately"
        ),
        (
            "Danh_sách_cầu_thủ_bóng_đá_Việt_Nam",
            "Danh sách các cầu thủ bóng đá Việt Nam.",
            ["Danh sách"],
            "skip",
            "List page - noise"
        ),
        
        # EDGE CASES - Mixed signals
        (
            "Lịch_sử_câu_lạc_bộ_bóng_đá_Hà_Nội",
            "Lịch sử câu lạc bộ bóng đá Hà Nội bắt đầu từ năm 2006, khi câu lạc bộ được thành lập.",
            ["Câu lạc bộ bóng đá Việt Nam", "Lịch sử thể thao"],
            "context",
            "Club history - INCLUDE keywords should win"
        ),
        (
            "Filip_Nguyễn",
            "Filip Nguyễn là cầu thủ bóng đá người Thụy Điển gốc Việt, thi đấu ở vị trí thủ môn.",
            ["Cầu thủ bóng đá Thụy Điển", "Người Việt kiều"],
            "core",
            "Vietnamese diaspora player - high value"
        ),
    ]
    
    passed = 0
    failed = 0
    
    for title, text, categories, expected_layer, description in test_cases:
        score, layer = filter_instance.evaluate_page(
            title=title,
            text=text,
            categories=categories
        )
        
        status = "✅ PASS" if layer == expected_layer else "❌ FAIL"
        
        if layer == expected_layer:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | {title}")
        print(f"       Expected: {expected_layer} | Actual: {layer} | Score: {score}")
        print(f"       Description: {description}")
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"Success rate: {passed/len(test_cases)*100:.1f}%")
    print("=" * 80)
    
    return failed == 0


def test_semantic_patterns():
    """Test semantic pattern matching."""
    
    filter_instance = AdvancedFilter()
    
    print("\n" + "=" * 80)
    print("SEMANTIC PATTERN MATCHING TEST")
    print("=" * 80)
    print()
    
    test_texts = [
        ("Nguyễn Văn A là cầu thủ bóng đá người Việt Nam.", True, "Vietnamese player pattern"),
        ("John Smith là huấn luyện viên bóng đá người Anh.", True, "Coach pattern"),
        ("Đội tuyển quốc gia Việt Nam thi đấu tại World Cup.", True, "National team pattern"),
        ("Câu lạc bộ Manchester United chơi cho Premier League.", True, "Club pattern"),
        ("Anh ấy thi đấu cho đội bóng Barcelona.", True, "Plays for pattern"),
        ("Hà Nội là thủ đô của Việt Nam.", False, "No football context"),
        ("Lịch sử Việt Nam rất lâu đời.", False, "History - no pattern"),
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
        print(f"       Text: {text[:60]}...")
        print(f"       Expected match: {should_match} | Actual: {matched}")
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_texts)} tests")
    print("=" * 80)
    
    return failed == 0


def test_noise_detection():
    """Test noise page detection."""
    
    print("\n" + "=" * 80)
    print("NOISE PAGE DETECTION TEST")
    print("=" * 80)
    print()
    
    test_cases = [
        ("File:Example.jpg", True, "File prefix"),
        ("Tập_tin:Hình_ảnh.png", True, "Vietnamese file prefix"),
        ("Wikipedia:Chính_sách", True, "Wikipedia meta"),
        ("Thể_loại:Bóng_đá", True, "Category page"),
        ("Danh_sách_cầu_thủ", True, "List page"),
        ("Nguyễn_Quang_Hải", False, "Player name - not noise"),
        ("Câu_lạc_bộ_bóng_đá_Hà_Nội", False, "Club name - not noise"),
    ]
    
    passed = 0
    failed = 0
    
    for title, expected_noise, description in test_cases:
        is_noise = is_noise_page(title)
        status = "✅ PASS" if is_noise == expected_noise else "❌ FAIL"
        
        if is_noise == expected_noise:
            passed += 1
        else:
            failed += 1
        
        print(f"{status} | {title}")
        print(f"       Expected noise: {expected_noise} | Actual: {is_noise}")
        print(f"       Description: {description}")
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print("=" * 80)
    
    return failed == 0


def show_config_summary():
    """Show summary of filtering configuration."""
    
    print("\n" + "=" * 80)
    print("FILTERING CONFIGURATION SUMMARY")
    print("=" * 80)
    print()
    
    print("📊 Keyword Lists:")
    print(f"   - INCLUDE_KEYWORDS: {len(config.INCLUDE_KEYWORDS)} keywords")
    print(f"   - EXCLUDE_KEYWORDS: {len(config.EXCLUDE_KEYWORDS)} keywords")
    print(f"   - PRIORITY_KEYWORDS: {len(config.PRIORITY_KEYWORDS)} keywords")
    print(f"   - SKIP_PREFIXES: {len(config.SKIP_PREFIXES)} prefixes")
    print()
    
    print("⚖️  Relevance Weights:")
    for signal, weight in config.RELEVANCE_WEIGHTS.items():
        sign = "+" if weight > 0 else ""
        print(f"   - {signal}: {sign}{weight}")
    print()
    
    print("🎯 Score Thresholds:")
    print(f"   - CORE layer: >= {config.RELEVANCE_SCORE_THRESHOLD_CORE}")
    print(f"   - CONTEXT layer: >= {config.RELEVANCE_SCORE_THRESHOLD_CONTEXT}")
    print()
    
    print("🔧 Active Filters:")
    for filter_name, enabled in config.ACTIVE_FILTERS.items():
        status = "✅ ON" if enabled else "❌ OFF"
        print(f"   - {filter_name}: {status}")
    print()
    
    print("📐 Graph Parameters:")
    print(f"   - MAX_ALLOWED_DISTANCE: {config.MAX_ALLOWED_DISTANCE}")
    print(f"   - MIN_NODE_DEGREE: {config.MIN_NODE_DEGREE}")
    print()
    
    print("🧠 Semantic Patterns: {len(config.SEMANTIC_PATTERNS)} patterns")
    print("   Sample patterns:")
    for pattern in config.SEMANTIC_PATTERNS[:5]:
        print(f"   - {pattern}")
    print()
    
    print("=" * 80)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test advanced filtering system")
    parser.add_argument("--config", "-c", action="store_true",
                       help="Show configuration summary")
    parser.add_argument("--scoring", "-s", action="store_true",
                       help="Test relevance scoring")
    parser.add_argument("--semantic", "-m", action="store_true",
                       help="Test semantic pattern matching")
    parser.add_argument("--noise", "-n", action="store_true",
                       help="Test noise detection")
    parser.add_argument("--all", "-a", action="store_true",
                       help="Run all tests")
    
    args = parser.parse_args()
    
    # If no specific test selected, run all
    if not any([args.config, args.scoring, args.semantic, args.noise, args.all]):
        args.all = True
    
    all_passed = True
    
    if args.config or args.all:
        show_config_summary()
    
    if args.scoring or args.all:
        if not test_relevance_scoring():
            all_passed = False
    
    if args.semantic or args.all:
        if not test_semantic_patterns():
            all_passed = False
    
    if args.noise or args.all:
        if not test_noise_detection():
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ ALL TESTS PASSED")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 80)
    
    sys.exit(0 if all_passed else 1)
