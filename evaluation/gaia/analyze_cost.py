#!/usr/bin/env python3
"""
Analyze cost from GAIA benchmark evaluation results.

Usage:
    python evaluation/gaia/analyze_cost.py <output.jsonl>
"""

import json
import sys
from pathlib import Path


def analyze_cost(output_file: str):
    """Analyze cost from evaluation output file."""
    if not Path(output_file).exists():
        print(f"Error: File {output_file} does not exist")
        sys.exit(1)

    total_stats = {
        "total_prompt_tokens": 0,
        "total_completion_tokens": 0,
        "total_tokens": 0,
        "total_cost": 0.0,
        "total_api_calls": 0,
        "num_instances": 0,
    }

    instance_costs = []

    with open(output_file, 'r') as f:
        for line in f:
            if not line.strip():
                continue

            data = json.loads(line)
            total_stats["num_instances"] += 1

            # Extract usage stats
            test_result = data.get('test_result', {})
            usage_stats = test_result.get('usage_stats', {})

            if usage_stats:
                total_stats["total_prompt_tokens"] += usage_stats.get("total_prompt_tokens", 0)
                total_stats["total_completion_tokens"] += usage_stats.get("total_completion_tokens", 0)
                total_stats["total_tokens"] += usage_stats.get("total_tokens", 0)
                total_stats["total_cost"] += usage_stats.get("total_cost", 0.0)
                total_stats["total_api_calls"] += usage_stats.get("api_calls", 0)

                # Store per-instance cost
                instance_costs.append({
                    "instance_id": data.get("instance_id"),
                    "cost": usage_stats.get("total_cost", 0.0),
                    "tokens": usage_stats.get("total_tokens", 0),
                    "api_calls": usage_stats.get("api_calls", 0),
                    "score": test_result.get("score", "N/A"),
                })

    # Print summary
    print("\n" + "=" * 70)
    print("GAIA Benchmark Cost Analysis")
    print("=" * 70)
    print(f"Output file: {output_file}")
    print(f"Total instances: {total_stats['num_instances']}")
    print()
    print("Overall Statistics:")
    print(f"  Total API calls:        {total_stats['total_api_calls']:,}")
    print(f"  Total prompt tokens:    {total_stats['total_prompt_tokens']:,}")
    print(f"  Total completion tokens: {total_stats['total_completion_tokens']:,}")
    print(f"  Total tokens:           {total_stats['total_tokens']:,}")
    print(f"  Total cost:             ${total_stats['total_cost']:.4f}")
    print()

    if total_stats["num_instances"] > 0:
        avg_cost = total_stats["total_cost"] / total_stats["num_instances"]
        avg_tokens = total_stats["total_tokens"] / total_stats["num_instances"]
        avg_calls = total_stats["total_api_calls"] / total_stats["num_instances"]

        print("Average per instance:")
        print(f"  Avg API calls:          {avg_calls:.2f}")
        print(f"  Avg tokens:             {avg_tokens:.0f}")
        print(f"  Avg cost:               ${avg_cost:.4f}")
        print()

    # Show top 5 most expensive instances
    if instance_costs:
        instance_costs.sort(key=lambda x: x["cost"], reverse=True)
        print("Top 5 most expensive instances:")
        for i, inst in enumerate(instance_costs[:5], 1):
            print(f"  {i}. {inst['instance_id']}: ${inst['cost']:.4f} "
                  f"({inst['tokens']:,} tokens, {inst['api_calls']} calls, "
                  f"score: {inst['score']})")
        print()

    print("=" * 70)
    print()


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python evaluation/gaia/analyze_cost.py <output.jsonl>")
        sys.exit(1)

    analyze_cost(sys.argv[1])
