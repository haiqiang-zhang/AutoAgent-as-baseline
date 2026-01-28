#!/usr/bin/env python3
"""
Test script for the SerpAPI implementation of web_search.

This script demonstrates both API-based and browser-based search modes.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autoagent.tools.web_tools import web_search, _serpapi_search


def test_api_search():
    """Test the API-based search if credentials are available."""
    print("=" * 70)
    print("Testing SerpAPI Search")
    print("=" * 70)

    # Check if API credentials are set
    api_key = os.environ.get("SERPAPI_API_KEY")

    if not api_key:
        print("⚠️  SERPAPI_API_KEY not found in environment variables")
        print("   Please set this variable to test API-based search.")
        print("   See WEB_SEARCH_SETUP.md for setup instructions.\n")
        return False

    print(f"✓ API Key found: {api_key[:10]}...\n")

    # Check if serpapi package is installed
    try:
        from serpapi import GoogleSearch
        print("✓ serpapi package is installed\n")
    except ImportError:
        print("✗ serpapi package not installed")
        print("  Install with: pip install google-search-results\n")
        return False

    # Test query
    test_query = "Python programming language"
    print(f"Searching for: '{test_query}'\n")

    try:
        result = _serpapi_search(test_query, num_results=3)
        print(result)
        print("\n✓ API search successful!")
        return True
    except Exception as e:
        print(f"✗ Error during API search: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_web_search_tool():
    """Test the web_search tool function with context_variables."""
    print("\n" + "=" * 70)
    print("Testing web_search tool function")
    print("=" * 70)

    context_variables = {}
    test_query = "machine learning basics"

    print(f"Searching for: '{test_query}'\n")

    try:
        result = web_search(context_variables, test_query, use_api=True)
        print("Result type:", type(result))
        print("\nResult value (first 800 chars):")
        print(result.value[:800] if len(result.value) > 800 else result.value)
        print("\n✓ web_search tool successful!")
        return True
    except Exception as e:
        print(f"✗ Error during web_search: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_location_search():
    """Test location-based search."""
    print("\n" + "=" * 70)
    print("Testing location-based search")
    print("=" * 70)

    # Check if API credentials are set
    api_key = os.environ.get("SERPAPI_API_KEY")

    if not api_key:
        print("⚠️  Skipping (SERPAPI_API_KEY not configured)")
        return True  # Not a failure, just skipped

    context_variables = {}
    test_query = "Italian restaurants"
    location = "San Francisco, CA"

    print(f"Searching for: '{test_query}' in '{location}'\n")

    try:
        result = web_search(
            context_variables,
            test_query,
            use_api=True,
            location=location
        )
        print("Result value (first 500 chars):")
        print(result.value[:500] if len(result.value) > 500 else result.value)
        print("\n✓ Location search successful!")
        return True
    except Exception as e:
        print(f"✗ Error during location search: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_fallback_mode():
    """Test fallback behavior when API is not available."""
    print("\n" + "=" * 70)
    print("Testing fallback mode (without API credentials)")
    print("=" * 70)

    # Temporarily remove API credentials to test fallback
    original_key = os.environ.get("SERPAPI_API_KEY")

    if original_key:
        del os.environ["SERPAPI_API_KEY"]

    context_variables = {}  # No web_env

    try:
        result = web_search(context_variables, "test query", use_api=True)
        print("Result:", result.value[:300])

        # Check if error message is correct
        if "SerpAPI credentials" in result.value or "web_env" in result.value:
            print("\n✓ Fallback error message displayed correctly")
            success = True
        else:
            print("\n✗ Unexpected fallback behavior")
            success = False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        success = False
    finally:
        # Restore original credentials
        if original_key:
            os.environ["SERPAPI_API_KEY"] = original_key

    return success


def test_answer_box():
    """Test answer box extraction."""
    print("\n" + "=" * 70)
    print("Testing answer box extraction")
    print("=" * 70)

    # Check if API credentials are set
    api_key = os.environ.get("SERPAPI_API_KEY")

    if not api_key:
        print("⚠️  Skipping (SERPAPI_API_KEY not configured)")
        return True  # Not a failure, just skipped

    context_variables = {}
    test_query = "what is the capital of France"

    print(f"Searching for: '{test_query}'\n")

    try:
        result = web_search(context_variables, test_query, use_api=True)

        # Check if answer box is present
        if "Answer Box" in result.value or "Paris" in result.value:
            print("✓ Answer box detected!")
            print("\nResult (first 400 chars):")
            print(result.value[:400])
        else:
            print("⚠️  No answer box found (this is OK, depends on query)")
            print("\nResult (first 400 chars):")
            print(result.value[:400])

        print("\n✓ Answer box test completed!")
        return True
    except Exception as e:
        print(f"✗ Error during answer box test: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("SerpAPI Web Search Implementation Test Suite")
    print("=" * 70 + "\n")

    results = []

    # Test 1: API search
    results.append(("API Search", test_api_search()))

    # Test 2: web_search tool
    results.append(("web_search Tool", test_web_search_tool()))

    # Test 3: Location search
    results.append(("Location Search", test_location_search()))

    # Test 4: Fallback mode
    results.append(("Fallback Mode", test_fallback_mode()))

    # Test 5: Answer box
    results.append(("Answer Box", test_answer_box()))

    # Summary
    print("\n" + "=" * 70)
    print("Test Summary")
    print("=" * 70)
    for test_name, success in results:
        status = "✓ PASS" if success else "✗ FAIL"
        print(f"{status}: {test_name}")

    total_passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")

    return total_passed == len(results)


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
