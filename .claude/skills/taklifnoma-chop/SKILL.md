---
name: taklifnoma-chop
description: Turn a checked invitation text into a print-ready Word (.docx) file at exact card size — single card, test print with text-area outline, several cards tiled on A4/A3 with cut lines, or a special (maxsus) design with frame and background. Use when rendering/printing a taklifnoma, adding a new card size, or when the printed text lands in the wrong place on the card.
---

# Taklifnoma chop (Word files for printing)

**Output is always .docx and nothing else.** The renderer writes only
`<out>.docx`. `--preview` draws a PNG into a temp folder so you can check
the layout by eye. Never copy the preview into the order folder or hand it
to the operator.

```bash
.venv/bin/python .claude/skills/taklifnoma-chop/scripts/render.py matn.txt \
    --preset matn-11x6 --out buyurtmalar/<folder>/taklifnoma-1 --preview
```

## What the file looks like

- Word page = the card. Margins put the text exactly in the text area, centred both ways.
- Times New Roman italic. `{NAMES}` red (#C00000) and bold. `# title` 1.25× bold. `## big line` 1.6× bold.
- **Auto font size**: the largest size at which the widest line and the whole block fit inside the area, minus a 0.2 cm inner margin (`--padding`). Line spacing is fixed ("exactly"), so Word does not reflow.
- If the size would fall below 8 pt, the script stops. Shorten or re-break the lines; don't force `--size`.
- The output reports the size and the widest line. Break that line to make the text larger.

## Card sizes — `cards.json`

| preset | card | text area | use |
|---|---|---|---|
| `matn-11x6` | 11×6 | 11×6 | Page = text area. Default when the real card size is unknown. |
| `a6-yotiq` | 14.8×10.5 | 11×6 centred | A6 landscape card |
| `maxsus-15x21` | 15×21 | 11×15 | Designed portrait card |

For a new card stock, measure it with a ruler and add a preset (cm):

```json
"chiroqchi-oq-21x10": {"card": [21, 10], "area": [11, 6], "offset": [8.5, 2], "note": "..."}
```

`offset` = distance from the card's **top-left corner** to the text area's
top-left corner. `null` = centred. You can also pass sizes directly:
`--card 21x10 --area 11x6 --offset 8.5,2`.

## Modes

| Need | Flags |
|---|---|
| Normal card (oddiy) | `--preset …` |
| Test print on plain paper, to hold against the card in light | `--guides`, which adds a dashed outline of the text area. Never give this file for the real print run. |
| Several copies on one sheet, to print on cardstock and cut | `--sheet A4` (or `A3`). Picks the orientation that fits the most cards and adds dotted cut lines between cards. |
| Maxsus design | `--frame gold\|red\|green\|#hex` (double page border) and/or `--background fon.jpg` (full-card picture behind the text, card ratio, 300 dpi). Background works on single cards only. Consider `--font georgia-italic`. |
| Other colours | `--name-color #hex`, `--text-color #hex` |
| Fonts | `--font times-italic` (default) `times` `georgia-italic` `georgia`; add more in `fonts.json`. Run `check.py --font` to confirm the font has ў қ ғ ҳ. |

For maxsus portrait cards, re-break the text into more, shorter lines.
Otherwise the widest line keeps the font small on a tall card.

## Printing tips to tell the operator

- In Word's print dialog, set scale to **100% / "Actual size"**, not "Fit to page".
- Choose the printer's card / thick paper tray and set the paper size to match the card.
- Do one test page with `--guides` on plain paper and check it against the card. If it is shifted, fix `offset` in the preset, not in Word.
- Word may show a "margins outside printable area" warning for edge-to-edge cards. Ignore it when the text area itself is inside the printable zone.
