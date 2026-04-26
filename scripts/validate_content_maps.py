import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from services.content_registry import ContentRegistry


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate content maps for the Telegram bot."
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Audit every row in content_items.json, including inactive items",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="With --strict, print detailed item lists instead of summary counts only",
    )
    args = parser.parse_args()

    registry = ContentRegistry()

    if args.strict:
        strict_report = registry.validate_strict()
        registry.print_strict_report(strict_report, verbose=args.verbose)
        return

    # Default mode: unchanged behavior
    has_warnings = any(registry.validation_report.values())
    if has_warnings:
        print("[content-registry] validation completed with warnings")
    else:
        print("[content-registry] validation passed")


if __name__ == "__main__":
    main()
