"""
Test utility for the enhanced filtering system.
Tests various page titles to validate INCLUDE/EXCLUDE keyword filtering.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.crawl import WikiCrawler
from src import config


def test_filtering():
    """Test the filtering system with various page titles."""
    
    crawler = WikiCrawler(max_depth=1)
    
    # Test cases: (page_title, expected_skip, reason)
    test_cases = [
        # Should KEEP (relevant football pages)
        ("Nguyễn_Quang_Hải_(sinh_1997)", False, "Player name"),
        ("Câu_lạc_bộ_bóng_đá_Hà_Nội", False, "Football club"),
        ("Đội_tuyển_bóng_đá_quốc_gia_Việt_Nam", False, "National team"),
        ("Park_Hang-seo", False, "Coach name"),
        ("V.League_1", False, "League"),
        ("Giải_vô_địch_bóng_đá_Đông_Nam_Á", False, "Tournament"),
        ("Tiền_đạo", False, "Position"),
        ("Huấn_luyện_viên_bóng_đá", False, "Coach role"),
        ("Filip_Nguyễn", False, "Vietnamese diaspora player"),
        
        # Should SKIP (irrelevant pages)
        ("Lịch_sử_Việt_Nam", True, "History page"),
        ("Kinh_tế_Việt_Nam", True, "Economy page"),
        ("Các_vùng_đô_thị_Việt_Nam", True, "Urban areas"),
        ("Tỉnh_Hà_Nội", True, "Province/geography"),
        ("Huyện_Ba_Vì", True, "District"),
        ("Xã_Tân_Lập", True, "Commune"),
        ("Bóng_rổ", True, "Basketball (other sport)"),
        ("Cầu_lông", True, "Badminton (other sport)"),
        ("Lý_Thái_Tổ", True, "Historical figure"),
        ("Chiến_tranh_Việt_Nam", True, "War/military"),
        ("Văn_hóa_Việt_Nam", True, "Culture"),
        ("Sông_Hồng", True, "River/geography"),
        ("Núi_Phú_Sĩ", True, "Mountain"),
        ("Danh_sách_tỉnh_thành_Việt_Nam", True, "List page"),
        
        # Should SKIP (media files)
        ("File:Example.jpg", True, "File prefix"),
        ("Tập_tin:Hình_ảnh.png", True, "Vietnamese file prefix"),
        ("Image:Photo.gif", True, "Image prefix"),
        
        # Should SKIP (Wikipedia meta pages)
        ("Wikipedia:Chính_sách", True, "Wikipedia meta"),
        ("Thể_loại:Bóng_đá", True, "Category page"),
        ("Bản_mẫu:Infobox", True, "Template page"),
        
        # Edge cases (mixed keywords)
        ("Lịch_sử_câu_lạc_bộ_bóng_đá_Hà_Nội", False, "Club history (INCLUDE > EXCLUDE)"),
        ("Kinh_tế_thể_thao_Việt_Nam", True, "Sports economy (EXCLUDE >= INCLUDE)"),
        ("Danh_sách_cầu_thủ_bóng_đá_Việt_Nam", False, "List of players (INCLUDE > EXCLUDE)"),
    ]
    
    print("=" * 80)
    print("FILTERING SYSTEM TEST")
    print("=" * 80)
    print()
    
    passed = 0
    failed = 0
    
    for page_title, expected_skip, reason in test_cases:
        actual_skip = crawler._should_skip_link(page_title)
        status = "✅ PASS" if actual_skip == expected_skip else "❌ FAIL"
        
        if actual_skip == expected_skip:
            passed += 1
        else:
            failed += 1
        
        action = "SKIP" if actual_skip else "KEEP"
        expected_action = "SKIP" if expected_skip else "KEEP"
        
        print(f"{status} | {page_title}")
        print(f"       Expected: {expected_action} | Actual: {action} | Reason: {reason}")
        print()
    
    print("=" * 80)
    print(f"RESULTS: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"Success rate: {passed/len(test_cases)*100:.1f}%")
    print("=" * 80)
    
    return failed == 0


def show_keyword_stats():
    """Show statistics about the keyword lists."""
    print("\n" + "=" * 80)
    print("KEYWORD STATISTICS")
    print("=" * 80)
    print(f"INCLUDE_KEYWORDS: {len(config.INCLUDE_KEYWORDS)} keywords")
    print(f"EXCLUDE_KEYWORDS: {len(config.EXCLUDE_KEYWORDS)} keywords")
    print(f"PRIORITY_KEYWORDS: {len(config.PRIORITY_KEYWORDS)} keywords")
    print(f"SKIP_PREFIXES: {len(config.SKIP_PREFIXES)} prefixes")
    print(f"SKIP_URL_KEYWORDS: {len(config.SKIP_URL_KEYWORDS)} keywords")
    print()
    
    print("Sample INCLUDE_KEYWORDS (first 10):")
    for kw in config.INCLUDE_KEYWORDS[:10]:
        print(f"  - {kw}")
    print()
    
    print("Sample EXCLUDE_KEYWORDS (first 10):")
    for kw in config.EXCLUDE_KEYWORDS[:10]:
        print(f"  - {kw}")
    print("=" * 80)


def interactive_test():
    """Interactive mode to test custom page titles."""
    crawler = WikiCrawler(max_depth=1)
    
    print("\n" + "=" * 80)
    print("INTERACTIVE FILTERING TEST")
    print("=" * 80)
    print("Enter page titles to test (or 'quit' to exit)")
    print()
    
    while True:
        page_title = input("Page title: ").strip()
        
        if page_title.lower() in ['quit', 'exit', 'q']:
            break
        
        if not page_title:
            continue
        
        should_skip = crawler._should_skip_link(page_title)
        action = "SKIP ⛔" if should_skip else "KEEP ✅"
        
        print(f"  → {action}")
        print()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test the enhanced filtering system")
    parser.add_argument("--interactive", "-i", action="store_true", 
                       help="Run in interactive mode")
    parser.add_argument("--stats", "-s", action="store_true",
                       help="Show keyword statistics")
    
    args = parser.parse_args()
    
    if args.stats:
        show_keyword_stats()
    
    if args.interactive:
        interactive_test()
    else:
        # Run automated tests
        success = test_filtering()
        
        if args.stats:
            show_keyword_stats()
        
        sys.exit(0 if success else 1)
