"""
Simplified main file with step-by-step imports for debugging
"""

import sys
import asyncio
from pathlib import Path

# Add current directory to path if needed
sys.path.append(str(Path(__file__).parent))

def main():
    print("Starting simplified scraper...")
    
    # Test imports one by one
    print("1. Testing config import...")
    try:
        import config
        print(f"   ✓ Config loaded - BAIRRO: {config.BAIRRO}")
    except Exception as e:
        print(f"   ✗ Config failed: {e}")
        return
    
    print("2. Testing models import...")
    try:
        from models import PropertyInfo
        test_prop = PropertyInfo(url="test")
        print("   ✓ Models working")
    except Exception as e:
        print(f"   ✗ Models failed: {e}")
        return
    
    print("3. Testing data_parser import...")
    try:
        from data_parser import PropertyParser
        parser = PropertyParser()
        print("   ✓ Data parser working")
    except Exception as e:
        print(f"   ✗ Data parser failed: {e}")
        return
    
    print("4. Testing url_collector import...")
    try:
        from url_collector import URLCollector
        print("   ✓ URL collector working")
    except Exception as e:
        print(f"   ✗ URL collector failed: {e}")
        return
    
    print("5. Testing http_client import...")
    try:
        from http_client import PropertyFetcher
        fetcher = PropertyFetcher()
        print("   ✓ HTTP client working")
        
        # Now test the convenience function
        from http_client import fetch_properties
        print("   ✓ fetch_properties function available")
        
    except Exception as e:
        print(f"   ✗ HTTP client failed: {e}")
        return
    
    print("\nAll imports successful! The issue might be elsewhere.")
    
    # If we get here, try a simple run
    print("6. Testing URL collection...")
    try:
        from url_collector import collect_urls
        print("   Starting URL collection (this may take a while)...")
        # urls = collect_urls()  # Uncomment to actually collect
        # print(f"   Collected {len(urls)} URLs")
        print("   URL collection function is available (skipped actual collection)")
    except Exception as e:
        print(f"   ✗ URL collection failed: {e}")
        return
    
    print("\nScraper components are working!")


if __name__ == "__main__":
    main()