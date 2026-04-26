import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from services.content_registry import ContentRegistry


def main() -> None:
    registry = ContentRegistry()
    has_warnings = any(registry.validation_report.values())
    if has_warnings:
        print("[content-registry] validation completed with warnings")
    else:
        print("[content-registry] validation passed")


if __name__ == "__main__":
    main()
