#!/usr/bin/env python3
"""Buduje kroje Ave (dist/*.ttf, dist/*.woff2), sprawdza je i renderuje podglądy.

- Ave Display: wersalikowy krój nagłówkowy (jeden styl),
- Ave Text: krój do akapitów (Regular, Italic, Bold, Bold Italic).

Użycie:  .venv/bin/python build.py [--family all|display|text] [--no-check] [--no-preview] [--no-hint]
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

DIST = ROOT / "dist"


def build_display(check: bool) -> bool:
    from ave_display.builder import build_font

    ttf, woff2 = build_font(DIST)
    print(f"zbudowano: {ttf.relative_to(ROOT)}, {woff2.relative_to(ROOT)}")
    if check:
        import verify

        return verify.run(ttf, woff2)
    return True


def build_text(check: bool, hint: bool) -> bool:
    from ave_text.builder import build_family

    for ttf, woff2 in build_family(DIST, hint=hint):
        print(f"zbudowano: {ttf.relative_to(ROOT)}, {woff2.relative_to(ROOT)}")
    if check:
        import verify_text

        return verify_text.run(DIST)
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Buduje kroje Ave Display i Ave Text.")
    parser.add_argument("--family", choices=["all", "display", "text"], default="all", help="który krój zbudować")
    parser.add_argument("--no-check", action="store_true", help="pomiń testy fontów")
    parser.add_argument("--no-preview", action="store_true", help="pomiń render podglądów PNG")
    parser.add_argument("--no-hint", action="store_true", help="Ave Text bez hintingu (szybciej, do iteracji)")
    args = parser.parse_args()

    ok = True
    if args.family in ("all", "display"):
        ok &= build_display(not args.no_check)
    if args.family in ("all", "text"):
        ok &= build_text(not args.no_check, not args.no_hint)
    if not ok:
        return 1

    if not args.no_preview:
        import preview

        if args.family in ("all", "display"):
            preview.render_all(ROOT)
        if args.family in ("all", "text"):
            preview.render_text(ROOT)
    return 0


if __name__ == "__main__":
    sys.exit(main())
