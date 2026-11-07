#!/usr/bin/env python3
"""Podglądy Ave Text renderowane przez Chrome bez okna.

Arkusz składa się z sekcji (glify w dużym rozmiarze, ciągi kontrolne odstępów, akapity
w rozmiarach tekstowych obok nagłówka w Ave Display). Każdy font z listy dostaje własny blok,
więc ten sam arkusz służy do porównywania wariantów.

Użycie z kodu:  proof([("Regular", path_to_ttf)], out_png, sections=["glyphs", "spacing", "text"])
"""

from __future__ import annotations

import html
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DISPLAY_WOFF2 = ROOT / "dist" / "AveDisplay-Regular.woff2"

LOWER = "abcdefghijklmnopqrstuvwxyz"
UPPER = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
SPACING_LOWER = [
    "nnnnonnnn", "nnannbnncnndnnennfnngnnhnninnjnnknnlnnmnn",
    "nnonnpnnqnnrnnsnntnnunnvnnwnnxnnynnznn",
    "oooaoobooocoodooeoofoogoohooiooj", "ookoolooomoonoooopooqoorooso", "ootoouoovoowooxooyoozoo",
]
WORDS = "minimum hamburgefontsiv kolejka wyjazd zażółć gęślą jaźń quiz typografia"
PARAGRAPH = (
    "Każde auto z naszej floty przechodzi przegląd przed wydaniem: sprawdzamy hamulce, opony "
    "i elektronikę, zanim oddamy Ci kluczyki. Rezerwację potwierdzisz w dwie minuty, a w cenie masz "
    "pełne ubezpieczenie i 300 km dziennie. Bez ukrytych opłat i bez kaucji przy wynajmie na weekend, "
    "nawet jeśli wybierzesz najmocniejszy model."
)
LOWER_PARAGRAPH = (
    "każde auto z naszej floty przechodzi przegląd przed wydaniem: sprawdzamy hamulce, opony "
    "i elektronikę, zanim oddamy kluczyki. rezerwację potwierdzisz w dwie minuty, a w cenie masz "
    "pełne ubezpieczenie i limit kilometrów na każdy dzień. bez ukrytych opłat i bez kaucji przy "
    "wynajmie na weekend, nawet jeśli wybierzesz najmocniejszy model z naszej oferty."
)


def chrome() -> str:
    for name in ("google-chrome", "google-chrome-stable", "chromium", "chromium-browser"):
        path = shutil.which(name)
        if path:
            return path
    raise RuntimeError("nie znaleziono Chrome/Chromium do renderowania podglądów")


def screenshot(page: Path, png: Path, width: int, height: int, scale: float = 1.0) -> None:
    png.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(
        [
            chrome(), "--headless=new", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
            f"--window-size={width},{height}", f"--force-device-scale-factor={scale}",
            "--virtual-time-budget=5000", f"--screenshot={png}", page.resolve().as_uri(),
        ],
        check=True, capture_output=True, timeout=180,
    )


def _font_face(family: str, path: Path) -> str:
    return (f'@font-face {{ font-family: "{family}"; src: url("{path.resolve().as_uri()}"); '
            f"font-display: block; }}")


def _section(kind: str, family: str, dark: bool) -> str:
    esc = html.escape
    if kind == "glyphs":
        return (f'<div class="row big" style="font-family:\'{family}\'">{esc(LOWER)}</div>'
                f'<div class="row big" style="font-family:\'{family}\'">{esc(UPPER)}</div>')
    if kind == "lower":
        return f'<div class="row big" style="font-family:\'{family}\'">{esc(LOWER)}</div>'
    if kind == "spacing":
        rows = "".join(f"<div>{esc(t)}</div>" for t in SPACING_LOWER)
        return f'<div class="row mid" style="font-family:\'{family}\'">{rows}</div>'
    if kind == "words":
        return f'<div class="row words" style="font-family:\'{family}\'">{esc(WORDS)}</div>'
    if kind in ("text", "lowertext"):
        body = PARAGRAPH if kind == "text" else LOWER_PARAGRAPH
        cols = "".join(
            f'<div class="col"><small>{size} px</small><p style="font-family:\'{family}\';font-size:{size}px">'
            f"{esc(body)}</p></div>"
            for size in (14, 16, 18, 24)
        )
        head = '<div class="head">WYBIERZ MASZYNĘ</div>' if kind == "text" else ""
        return f'{head}<div class="cols">{cols}</div>'
    raise ValueError(kind)


def proof_html(fonts: list[tuple[str, Path]], sections: list[str], dark: bool = True) -> str:
    faces = [_font_face("AveDisplayProof", DISPLAY_WOFF2)]
    blocks = []
    for i, (label, path) in enumerate(fonts):
        family = f"proof{i}"
        faces.append(_font_face(family, path))
        inner = "".join(_section(kind, family, dark) for kind in sections)
        blocks.append(f'<section><h2>{html.escape(label)}</h2>{inner}</section>')
    bg, fg, muted, line = ("#070708", "#e8e8ec", "#8a8a93", "#222228") if dark else ("#ffffff", "#141416", "#777", "#ddd")
    return f"""<!doctype html><html lang="pl"><head><meta charset="utf-8"><style>
{chr(10).join(faces)}
body {{ margin: 0; background: {bg}; color: {fg}; -webkit-font-smoothing: antialiased; }}
main {{ padding: 28px 36px; }}
section {{ padding: 8px 0 22px; border-bottom: 1px solid {line}; }}
h2 {{ font: 600 13px/1 monospace; letter-spacing: .1em; text-transform: uppercase; color: #e10600; margin: 14px 0 12px; }}
.row {{ white-space: nowrap; }}
.big {{ font-size: 104px; line-height: 1.22; }}
.mid {{ font-size: 40px; line-height: 1.3; }}
.words {{ font-size: 64px; line-height: 1.3; }}
.head {{ font: 400 48px/1.1 "AveDisplayProof"; margin: 14px 0 6px; }}
.cols {{ display: grid; grid-template-columns: 1fr 1fr 1fr 1.25fr; gap: 28px; align-items: start; }}
.col small {{ font: 12px monospace; color: {muted}; }}
.col p {{ margin: 6px 0 0; line-height: 1.6; }}
</style></head><body><main>{''.join(blocks)}</main></body></html>"""


def proof(fonts: list[tuple[str, Path]], png: Path, sections: list[str], width: int = 1800,
          height: int = 2400, scale: float = 1.0, dark: bool = True) -> Path:
    page = png.with_suffix(".html")
    page.write_text(proof_html(fonts, sections, dark), encoding="utf-8")
    screenshot(page, png, width, height, scale)
    return png
