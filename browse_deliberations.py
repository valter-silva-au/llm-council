#!/usr/bin/env python3
"""Browse and search past council deliberations."""

import sys
import os
import io

# Fix Windows console encoding
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from backend.deliberations import list_deliberations, get_deliberation, search_deliberations


def print_header(text: str):
    """Print a formatted header."""
    print("\n" + "=" * 80)
    print(text)
    print("=" * 80 + "\n")


def list_command(limit: int = 10):
    """List recent deliberations."""
    print_header("Recent Council Deliberations")

    deliberations = list_deliberations(limit=limit)

    if not deliberations:
        print("No deliberations found.")
        return

    for i, delib in enumerate(deliberations, 1):
        print(f"{i}. {delib['name']}")
        print(f"   Date: {delib['date']} {delib['time']}")
        print(f"   Question: {delib['question_preview']}")
        print(f"   Models: {delib['models_participated']}, Chairman: {delib['chairman']}")
        print(f"   Web Search: {'✓' if delib['web_search_enabled'] else '✗'}")
        print()


def view_command(name: str):
    """View a specific deliberation."""
    delib = get_deliberation(name)

    if not delib:
        print(f"Deliberation not found: {name}")
        return

    print_header(f"Deliberation: {delib['name']}")

    # Print metadata
    print(f"**Date:** {delib['date']} {delib['time']}")
    print(f"**Models:** {delib['models_participated']}")
    print(f"**Chairman:** {delib['chairman']}")
    print(f"**Web Search:** {'Yes' if delib['web_search_enabled'] else 'No'}")
    print()

    # Print question
    print_header("Question")
    print(delib['question'])

    # Print Stage 1 responses
    print_header(f"Stage 1: Individual Responses ({len(delib['stage1'])} models)")
    for resp in delib['stage1']:
        print(resp['content'])
        print("\n" + "-" * 80 + "\n")

    # Print Stage 3 final answer
    print_header("Stage 3: Final Answer")
    print(delib['stage3'])


def search_command(query: str, limit: int = 5):
    """Search deliberations."""
    print_header(f"Search Results for: '{query}'")

    results = search_deliberations(query, limit=limit)

    if not results:
        print("No deliberations found matching your query.")
        return

    for i, delib in enumerate(results, 1):
        print(f"{i}. {delib['name']}")
        print(f"   Date: {delib['date']} {delib['time']}")
        print(f"   Question: {delib['question_preview']}")
        print()


def main():
    """Main CLI interface."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python browse_deliberations.py list [limit]")
        print("  python browse_deliberations.py view <name>")
        print("  python browse_deliberations.py search <query>")
        print()
        print("Examples:")
        print("  python browse_deliberations.py list")
        print("  python browse_deliberations.py list 20")
        print("  python browse_deliberations.py view 2026-01-30-16-30-05-i-want-to-explain-the-llm-council-system-to-yo")
        print("  python browse_deliberations.py search roadmap")
        sys.exit(1)

    command = sys.argv[1]

    if command == "list":
        limit = int(sys.argv[2]) if len(sys.argv) > 2 else 10
        list_command(limit)
    elif command == "view":
        if len(sys.argv) < 3:
            print("Error: Missing deliberation name")
            sys.exit(1)
        view_command(sys.argv[2])
    elif command == "search":
        if len(sys.argv) < 3:
            print("Error: Missing search query")
            sys.exit(1)
        search_command(" ".join(sys.argv[2:]))
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
