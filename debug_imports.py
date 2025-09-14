"""
Debug script to identify import issues
"""

def test_imports():
    """Test each import individually to identify the issue"""
    
    print("Testing imports...")
    
    try:
        import config
        print("✓ config imported successfully")
    except Exception as e:
        print(f"✗ config import failed: {e}")
        return
    
    try:
        from models import PropertyInfo
        print("✓ models.PropertyInfo imported successfully")
    except Exception as e:
        print(f"✗ models.PropertyInfo import failed: {e}")
        return
    
    try:
        from data_parser import parse_property_html
        print("✓ data_parser.parse_property_html imported successfully")
    except Exception as e:
        print(f"✗ data_parser.parse_property_html import failed: {e}")
        return
    
    try:
        import http_client
        print("✓ http_client module imported successfully")
        
        # Check what's available in the module
        print(f"Available in http_client: {dir(http_client)}")
        
        if hasattr(http_client, 'fetch_properties'):
            print("✓ fetch_properties function found in http_client")
        else:
            print("✗ fetch_properties function NOT found in http_client")
            
    except Exception as e:
        print(f"✗ http_client import failed: {e}")
        return
    
    try:
        from http_client import fetch_properties
        print("✓ fetch_properties imported successfully")
    except Exception as e:
        print(f"✗ fetch_properties import failed: {e}")
        return
    
    print("\nAll imports successful!")


if __name__ == "__main__":
    test_imports()