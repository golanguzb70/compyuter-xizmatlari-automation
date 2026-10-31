#!/usr/bin/env python3
"""A4 calibration grid (.docx) for measuring where a card lands in the printer.

The page carries a 300 dpi millimetre grid: thin lines every 1 mm, thick
lines every 1 cm, and every 1 cm square is labelled "X·Y" = the A4
coordinates (cm) of its top-left corner. Print it the way cards are printed
(same printer and tray, paper size A4, scale 100% / "Actual size"):

  1. Cut plain paper to the card's exact size, feed it like a card, print.
  2. On that piece read the coordinates under its top-left corner
     (label + mm lines)  ->  card_pos X,Y.
  3. Lay the piece on a real card (edges aligned) and read where the clean
     area starts and ends: inside the ornament, below a pre-printed title,
     clear of emblems  ->  area (W×H) and offset (from the card's corner).

Usage:
    kalibrovka.py --out buyurtmalar/kalibrovka-a4
"""
import argparse
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render import SHEETS, add_background, new_document  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402

DPI = 300
PX_PER_MM = DPI / 25.4
LABEL_FONT = "/System/Library/Fonts/Supplemental/Arial.ttf"


def grid_png(page_w_cm, page_h_cm, path):
    w, h = round(page_w_cm * 10 * PX_PER_MM), round(page_h_cm * 10 * PX_PER_MM)
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(LABEL_FONT, 22) if os.path.exists(LABEL_FONT) else ImageFont.load_default()
    for mm in range(int(page_w_cm * 10) + 1):
        x = round(mm * PX_PER_MM)
        major = mm % 10 == 0
        d.line([(x, 0), (x, h)], fill=(40, 40, 40) if major else (200, 200, 200), width=3 if major else 1)
    for mm in range(int(page_h_cm * 10) + 1):
        y = round(mm * PX_PER_MM)
        major = mm % 10 == 0
        d.line([(0, y), (w, y)], fill=(40, 40, 40) if major else (200, 200, 200), width=3 if major else 1)
    for cx in range(int(page_w_cm)):
        for cy in range(int(page_h_cm)):
            red = cx % 5 == 0 or cy % 5 == 0
            d.text((round(cx * 10 * PX_PER_MM) + 6, round(cy * 10 * PX_PER_MM) + 5), f"{cx}·{cy}",
                   fill=(200, 0, 0) if red else (90, 90, 90), font=font)
    img.save(path, dpi=(DPI, DPI))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", required=True, help="output path without extension")
    ap.add_argument("--page", choices=list(SHEETS), default="A4")
    args = ap.parse_args()

    pw, ph = SHEETS[args.page]
    png = os.path.join(tempfile.mkdtemp(prefix="kalibrovka-"), "grid.png")
    grid_png(pw / cm, ph / cm, png)
    doc, _ = new_document(pw, ph, 0.5 * cm, 0.5 * cm, 0.5 * cm, 0.5 * cm)
    add_background(doc.add_paragraph(), png, pw, ph)  # image anchored at the page corner, exact size
    os.makedirs(os.path.dirname(os.path.abspath(args.out)) or ".", exist_ok=True)
    doc.save(args.out + ".docx")
    print(f"DOCX: {args.out}.docx  ({args.page}, mm to'r, har 1 sm katak X·Y bilan belgilangan)")


if __name__ == "__main__":
    main()
