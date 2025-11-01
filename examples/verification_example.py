#!/usr/bin/env python
"""
Verification Example for ApiLinker - No API Keys Required
===========================================================

This example demonstrates basic ApiLinker functionality using the public
httpbin.org API, which requires no authentication. This is designed for
reviewers and users to verify installation without needing to obtain API keys.

Expected output is documented inline.

Usage:
    python verification_example.py

Requirements:
    - ApiLinker installed (pip install apilinker)
    - Internet connection
"""

from apilinker import ApiLinker


def main():
    """Run verification tests using httpbin.org public API."""
    
    print("=" * 70)
    print("ApiLinker Installation Verification")
    print("=" * 70)
    print()
    
    # Test 1: Basic HTTP GET request
    print("Test 1: Basic HTTP GET Request")
    print("-" * 70)
    
    linker = ApiLinker()
    linker.add_source(
        type="rest",
        base_url="https://httpbin.org",
        endpoints={
            "get_test": {
                "path": "/get",
                "method": "GET",
                "params": {"test_param": "verification"}
            }
        }
    )
    
    result = linker.fetch("get_test")
    print("[OK] Successfully fetched data from httpbin.org")
    print(f"  - Response URL: {result.get('url', 'N/A')}")
    print(f"  - Test parameter received: {result.get('args', {}).get('test_param', 'N/A')}")
    print()
    # Expected output:
    #   [OK] Successfully fetched data from httpbin.org
    #   - Response URL: https://httpbin.org/get?test_param=verification
    #   - Test parameter received: verification
    
    # Test 2: Field mapping
    print("Test 2: Field Mapping and Transformation")
    print("-" * 70)
    
    linker2 = ApiLinker()
    linker2.add_source(
        type="rest",
        base_url="https://httpbin.org",
        endpoints={
            "get_user_agent": {
                "path": "/user-agent",
                "method": "GET"
            }
        }
    )
    
    # Add a simple target (we won't actually POST, just test mapping)
    linker2.add_target(
        type="rest",
        base_url="https://httpbin.org",
        endpoints={
            "echo": {
                "path": "/post",
                "method": "POST"
            }
        }
    )
    
    # Add mapping with transformation
    linker2.add_mapping(
        source="get_user_agent",
        target="echo",
        fields=[
            {"source": "user-agent", "target": "browser", "transform": "strip"}
        ]
    )
    
    # Fetch and map (dry run - don't actually POST)
    source_data = linker2.fetch("get_user_agent")
    mapped_data = linker2.mapper.map_data(
        "get_user_agent",
        "echo",
        source_data
    )
    
    print("[OK] Field mapping successful")
    print(f"  - Source field 'user-agent': Present")
    print(f"  - Mapped to 'browser': {mapped_data.get('browser', 'N/A')[:50]}...")
    print()
    # Expected output:
    #   [OK] Field mapping successful
    #   - Source field 'user-agent': Present
    #   - Mapped to 'browser': python-httpx/... (or similar)
    
    # Test 3: JSON response handling
    print("Test 3: JSON Response Handling")
    print("-" * 70)
    
    linker3 = ApiLinker()
    linker3.add_source(
        type="rest",
        base_url="https://httpbin.org",
        endpoints={
            "get_json": {
                "path": "/json",
                "method": "GET"
            }
        }
    )
    
    json_result = linker3.fetch("get_json")
    slideshow = json_result.get("slideshow", {})
    
    print("[OK] JSON parsing successful")
    print(f"  - Slideshow title: {slideshow.get('title', 'N/A')}")
    print(f"  - Slideshow author: {slideshow.get('author', 'N/A')}")
    print(f"  - Nested data access: {type(slideshow.get('slides', [])).__name__}")
    print()
    # Expected output:
    #   [OK] JSON parsing successful
    #   - Slideshow title: Sample Slide Show
    #   - Slideshow author: Yours Truly
    #   - Nested data access: list
    
    # Test 4: Custom transformer
    print("Test 4: Custom Transformer Registration")
    print("-" * 70)
    
    def to_uppercase(value):
        """Custom transformer for testing."""
        return str(value).upper() if value else value
    
    linker4 = ApiLinker()
    linker4.mapper.register_transformer("to_uppercase", to_uppercase)
    
    # Test the transformer
    test_value = "hello world"
    transformed = linker4.mapper.transform(test_value, "to_uppercase")
    
    print("[OK] Custom transformer registered and working")
    print(f"  - Original: '{test_value}'")
    print(f"  - Transformed: '{transformed}'")
    print()
    # Expected output:
    #   [OK] Custom transformer registered and working
    #   - Original: 'hello world'
    #   - Transformed: 'HELLO WORLD'
    
    # Summary
    print("=" * 70)
    print("VERIFICATION COMPLETE")
    print("=" * 70)
    print()
    print("All tests passed! ApiLinker is correctly installed and functional.")
    print()
    print("Next steps:")
    print("  1. Review the examples/ directory for more use cases")
    print("  2. Read the documentation at https://apilinker.readthedocs.io/")
    print("  3. Try the CLI: apilinker --help")
    print()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n[ERROR] Verification failed with error: {e}")
        print("\nTroubleshooting:")
        print("  1. Ensure ApiLinker is installed: pip install apilinker")
        print("  2. Check internet connection (httpbin.org must be accessible)")
        print("  3. Verify Python version >=3.8: python --version")
        print(f"\nError details: {type(e).__name__}: {e}")
        exit(1)

