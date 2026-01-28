#!/usr/bin/env python3
"""
Example usage of the SerpAPI-based web_search tool.

Before running this example:
1. Set SERPAPI_API_KEY in your .env file
2. Install serpapi: pip install google-search-results
3. Run: python autoagent/tools/serpapi_example.py
"""

import os
import sys
from pathlib import Path



# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from autoagent.tools.web_tools import web_search


def example_basic_search():
    """Example 1: Basic search query."""
    print("=" * 70)
    print("Example 1: Basic Search")
    print("=" * 70)

    context_variables = {}
    result = web_search(context_variables, query="Python programming language")

    print(result.value)
    print("\n")


def example_location_search():
    """Example 2: Location-based search."""
    print("=" * 70)
    print("Example 2: Location-based Search")
    print("=" * 70)

    context_variables = {}
    result = web_search(
        context_variables,
        query="best coffee shops",
        location="Austin, Texas, United States"
    )

    print(result.value)
    print("\n")


def example_factual_query():
    """Example 3: Factual query with answer box."""
    print("=" * 70)
    print("Example 3: Factual Query (Answer Box)")
    print("=" * 70)

    context_variables = {}
    result = web_search(context_variables, query="what is the capital of France")

    print(result.value)
    print("\n")


def example_research_query():
    """Example 4: Research query for USGS data."""
    print("=" * 70)
    print("Example 4: Research Query (USGS Data)")
    print("=" * 70)

    context_variables = {}
    result = web_search(
        context_variables,
        query="invasive clownfish locations USGS data"
    )

    print(result.value)
    print("\n")


def example_knowledge_graph():
    """Example 5: Query with knowledge graph."""
    print("=" * 70)
    print("Example 5: Knowledge Graph")
    print("=" * 70)

    context_variables = {}
    result = web_search(context_variables, query="Albert Einstein")

    print(result.value)
    print("\n")


def main():
    """Run all examples."""
    # Check if API key is set
    api_key = os.environ.get("SERPAPI_API_KEY")

    if not api_key:
        print("=" * 70)
        print("ERROR: SERPAPI_API_KEY not found")
        print("=" * 70)
        print("\nPlease set SERPAPI_API_KEY in your .env file.")
        print("\nSteps:")
        print("1. Get your API key from: https://serpapi.com/")
        print("2. Add to .env: SERPAPI_API_KEY=your_key_here")
        print("3. See WEB_SEARCH_SETUP.md for detailed instructions")
        print("\n")
        sys.exit(1)

    print("\n" + "=" * 70)
    print("SerpAPI Web Search Examples")
    print("=" * 70 + "\n")

    try:
        # Run examples
        example_basic_search()
        example_location_search()
        example_factual_query()
        example_research_query()
        example_knowledge_graph()

        print("=" * 70)
        print("All examples completed successfully!")
        print("=" * 70)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
