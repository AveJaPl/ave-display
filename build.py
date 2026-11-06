#!/usr/bin/env python3
"""Buduje Ave Display (dist/*.ttf, dist/*.woff2), sprawdza font i renderuje podglądy.

Użycie:  .venv/bin/python build.py [--no-check] [--no-preview]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from ave_display.builder import build_font  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description="Buduje font Ave Display.")
    parser.add_argument("--no-check", action="store_true", help="pomiń testy fontu")
    parser.add_argument("--no-preview", action="store_true", help="pomiń render podglądów PNG")
    args = parser.parse_args()

    ttf, woff2 = build_font(ROOT / "dist")
    print(f"zbudowano: {ttf.relative_to(ROOT)}, {woff2.relative_to(ROOT)}")

    if not args.no_check:
        import verify

        if not verify.run(ttf, woff2):
            return 1

    if not args.no_preview:
        import preview

        preview.render_all(ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
