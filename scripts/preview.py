#!/usr/bin/env python3
"""Renderuje podglądy PNG przez Chrome bez okna (headless).

preview/specimen.png      - cały specimen.html
preview/banner.png        - napis AVEJA i podpis Filip Piątek w dużym rozmiarze
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
BACKGROUND = (7, 7, 8)

BANNER = """<!doctype html>
<html lang="pl"><head><meta charset="utf-8"><title>AveJa</title>
<style>
@font-face { font-family: "Ave Display"; src: url("../dist/AveDisplay-Regular.woff2") format("woff2"); font-display: block; }
html, body { margin: 0; height: 100%; background: #070708; }
body { display: grid; place-content: center; text-align: center; font-family: "Ave Display"; line-height: 1; }
h1 { margin: 0; font-size: 230px; font-weight: 400; color: #fff; }
p { margin: 36px 0 0; font-size: 60px; color: #9ba3ab; letter-spacing: 0.06em; }
</style></head><body><h1>AveJa</h1><p>Filip Piątek</p></body></html>
"""


def chrome() -> str:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("nie znaleziono Chrome/Chromium do renderowania podglądów")


def screenshot(html: Path, png: Path, width: int, height: int) -> None:
    png.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars",
            f"--window-size={width},{height}", "--virtual-time-budget=5000",
            f"--screenshot={png}", html.resolve().as_uri(),
        ],
        check=True, capture_output=True, timeout=120,
    )


def trim_bottom(png: Path, margin: int = 24) -> None:
    image = Image.open(png).convert("RGB")
    pixels = np.asarray(image).astype(int)
    rows = np.where(np.abs(pixels - BACKGROUND).sum(axis=2).max(axis=1) > 24)[0]
    if rows.size:
        image.crop((0, 0, image.width, min(image.height, rows.max() + margin))).save(png)


def render_all(root: Path = ROOT) -> None:
    preview = root / "preview"
    specimen_png = preview / "specimen.png"
    screenshot(root / "specimen.html", specimen_png, 1600, 9000)
    trim_bottom(specimen_png, margin=56)

    banner_html = preview / "banner.html"
    banner_html.write_text(BANNER, encoding="utf-8")
    screenshot(banner_html, preview / "banner.png", 2400, 760)
    print(f"podglądy: {specimen_png.relative_to(root)}, {(preview / 'banner.png').relative_to(root)}")


if __name__ == "__main__":
    render_all(Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT)
