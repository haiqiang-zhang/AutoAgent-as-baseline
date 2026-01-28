#!/usr/bin/env python3
"""
Fix cost statistics in GAIA benchmark output.jsonl files.

The original code only recorded the usage_stats from the last run_async call,
missing the cost from retries. This script:
1. Analyzes messages to detect actual LLM call count (assistant messages)
2. Compares with recorded api_calls
3. Adjusts cost proportionally if there's a mismatch

Usage:
    python evaluation/gaia/fix_cost.py <output.jsonl> [--output fixed_output.jsonl]
"""

import json
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Tuple


def count_assistant_messages(messages: List[Dict]) -> int:
    """Count the number of assistant messages (each represents an LLM call)."""
    count = 0
    for msg in messages:
        role = msg.get('role', '')
        # Assistant messages represent LLM responses
        if role == 'assistant':
            count += 1
        # Tool messages with certain patterns also indicate LLM decisions
        elif role == 'tool':
            content = msg.get('content', '')
            if isinstance(content, str):
                # Tool call results that show agent decision-making
                if content.startswith(('Open the', 'Re-open', 'Attempt to', 'Check', 'Search')):
                    # These are tool call descriptions from agent, count as LLM call
                    pass
    return count


def detect_retry_pattern(messages: List[Dict]) -> Tuple[int, int, bool]:
    """
    Detect retry patterns in messages.

    Returns:
        (retry_count, case_not_resolved_count, has_meta_agent)
    """
    retry_count = 0
    case_not_resolved_count = 0
    has_meta_agent = False

    for msg in messages:
        content = msg.get('content', '')
        if isinstance(content, str):
            if 'Case not resolved' in content:
                case_not_resolved_count += 1
            if 'try to resolve the case again' in content.lower():
                retry_count += 1
            if 'existing agent system' in content.lower() and 'MetaChain' in content:
                has_meta_agent = True

    return retry_count, case_not_resolved_count, has_meta_agent


def estimate_actual_api_calls(messages: List[Dict]) -> int:
    """
    Estimate actual API calls by counting assistant role messages.
    Each assistant message represents one LLM API call.
    """
    return sum(1 for msg in messages if msg.get('role') == 'assistant')


def fix_instance_cost(instance: Dict) -> Tuple[Dict, bool, str]:
    """
    Fix cost for a single instance.

    Simple approach: If there are retries, multiply cost by (retry_count + 1).
    retry_count = number of "Please try to resolve the case again" messages.
    Total attempts = retry_count + 1 (original attempt + retries).

    Returns:
        (fixed_instance, was_modified, modification_reason)
    """
    messages = instance.get('messages', [])
    test_result = instance.get('test_result', {})
    usage_stats = test_result.get('usage_stats', {})

    if not usage_stats:
        return instance, False, "No usage_stats found"

    retry_count, case_not_resolved_count, has_meta_agent = detect_retry_pattern(messages)

    # If no retries detected, no fix needed
    if retry_count == 0:
        return instance, False, "No retries detected"

    # Calculate multiplier: total attempts = retry_count + 1
    multiplier = retry_count + 1
    original_cost = usage_stats.get("total_cost", 0)

    # Create fixed usage stats
    fixed_usage_stats = {
        "total_prompt_tokens": int(usage_stats.get("total_prompt_tokens", 0) * multiplier),
        "total_completion_tokens": int(usage_stats.get("total_completion_tokens", 0) * multiplier),
        "total_tokens": int(usage_stats.get("total_tokens", 0) * multiplier),
        "total_cost": original_cost * multiplier,
        "api_calls": usage_stats.get("api_calls", 0) * multiplier,
        # Keep original values for reference
        "_original_cost": original_cost,
        "_original_api_calls": usage_stats.get("api_calls", 0),
        "_retry_count": retry_count,
        "_multiplier": multiplier,
    }

    # Update instance
    fixed_instance = instance.copy()
    fixed_instance['test_result'] = test_result.copy()
    fixed_instance['test_result']['usage_stats'] = fixed_usage_stats

    reason = (f"Multiplied by {multiplier} (retry_count={retry_count}), "
              f"cost: ${original_cost:.4f} -> ${original_cost * multiplier:.4f}")

    return fixed_instance, True, reason


def fix_output_file(input_path: str, output_path: str = None) -> Dict:
    """
    Fix cost statistics in output.jsonl file.

    Returns summary statistics.
    """
    if output_path is None:
        output_path = input_path.replace('.jsonl', '_fixed.jsonl')

    summary = {
        "total_instances": 0,
        "modified_instances": 0,
        "original_total_cost": 0.0,
        "fixed_total_cost": 0.0,
        "modifications": []
    }

    fixed_lines = []

    with open(input_path, 'r') as f:
        for line in f:
            if not line.strip():
                continue

            instance = json.loads(line)
            summary["total_instances"] += 1

            # Get original cost
            original_cost = instance.get('test_result', {}).get('usage_stats', {}).get('total_cost', 0)
            summary["original_total_cost"] += original_cost

            # Fix instance
            fixed_instance, was_modified, reason = fix_instance_cost(instance)

            # Get fixed cost
            fixed_cost = fixed_instance.get('test_result', {}).get('usage_stats', {}).get('total_cost', 0)
            summary["fixed_total_cost"] += fixed_cost

            if was_modified:
                summary["modified_instances"] += 1
                summary["modifications"].append({
                    "instance_id": instance.get('instance_id'),
                    "reason": reason,
                    "original_cost": original_cost,
                    "fixed_cost": fixed_cost,
                })

            fixed_lines.append(json.dumps(fixed_instance, ensure_ascii=False))

    # Write fixed file
    with open(output_path, 'w') as f:
        for line in fixed_lines:
            f.write(line + '\n')

    return summary


def main():
    parser = argparse.ArgumentParser(description='Fix cost statistics in GAIA output files')
    parser.add_argument('input_file', help='Input output.jsonl file')
    parser.add_argument('--output', '-o', help='Output file path (default: input_fixed.jsonl)')
    parser.add_argument('--dry-run', action='store_true', help='Only analyze without writing')
    args = parser.parse_args()

    if not Path(args.input_file).exists():
        print(f"Error: File {args.input_file} does not exist")
        sys.exit(1)

    output_path = args.output
    if args.dry_run:
        output_path = '/dev/null'

    summary = fix_output_file(args.input_file, output_path)

    print("\n" + "=" * 70)
    print("GAIA Cost Fix Summary")
    print("=" * 70)
    print(f"Input file: {args.input_file}")
    if not args.dry_run:
        print(f"Output file: {output_path or args.input_file.replace('.jsonl', '_fixed.jsonl')}")
    print()
    print(f"Total instances: {summary['total_instances']}")
    print(f"Modified instances: {summary['modified_instances']}")
    print()
    print(f"Original total cost: ${summary['original_total_cost']:.4f}")
    print(f"Fixed total cost:    ${summary['fixed_total_cost']:.4f}")
    print(f"Difference:          ${summary['fixed_total_cost'] - summary['original_total_cost']:.4f}")
    print()

    if summary['modifications']:
        print("Modified instances:")
        for mod in summary['modifications']:
            print(f"  {mod['instance_id']}:")
            print(f"    {mod['reason']}")
            print(f"    Cost: ${mod['original_cost']:.4f} -> ${mod['fixed_cost']:.4f}")
        print()

    print("=" * 70)


if __name__ == "__main__":
    main()
