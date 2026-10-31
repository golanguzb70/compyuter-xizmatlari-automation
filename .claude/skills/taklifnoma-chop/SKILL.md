---
name: taklifnoma-chop
description: Turn a checked invitation text into a print-ready Word (.docx) file — an A4 page with the text placed exactly on the card's clean area (inside the ornament, below the pre-printed title, clear of emblems), plus calibration of where cards land in the printer, test prints, A4 sheets of cut-out cards, and special (maxsus) designs. Use when rendering/printing a taklifnoma, adding or measuring a new card type, or when printed text lands on the border/title/emblem.
---

# Taklifnoma chop (Word files for printing)

**Output is always .docx and nothing else.** The page is **A4** by default.
The card is fed into the printer with A4 selected, and the text is placed
at the exact spot on the A4 page where the card's clean area lands.
`--preview` draws a PNG of the whole A4 page (dashed card outline + text)
into a temp folder for your own check. Never put it in the order folder.

```bash
.venv/bin/python .claude/skills/taklifnoma-chop/scripts/render.py matn.txt \
    --preset ft-oltin-15x10 --out buyurtmalar/<folder>/taklifnoma-1 --preview
```

## Why it is measured, not centred

Ready-made cards (see `ft-oltin-15x10`) have three things the text must avoid:
1. **An ornament border.** Text must stay inside it.
2. **A pre-printed «АССАЛОМУ АЛАЙКУМ!» at the top.** Our title line must not
   be printed (`preprinted_title: true` drops `# ` lines automatically).
3. **An emblem or picture** (e.g. a horse at the right). The area must stop
   before it.

If text was centred on the card, or set too large, it ran into all three.
That is the bug seen on a real print. So every card type has a measured
preset, and the text is auto-sized to that area only.

## Card presets — `cards.json`

| key | meaning |
|---|---|
| `page` | Paper size selected in the printer: `A4` (default) or `card` (page = card, for full-bleed maxsus designs) |
| `card_pos` | Card's top-left corner on the A4 page, X,Y in cm, as the printer actually feeds it. `null` = assumed top-centre (prints a warning) |
| `card` | Card W×H, cm |
| `area` | Clean text area W×H, cm |
| `offset` | Text area's top-left corner measured from the card's top-left corner, X,Y in cm |
| `preprinted_title` | `true` → `# ` title lines are not printed |
| `calibrated` | `false` → values are estimates. Tell the operator to calibrate before a big run |

Current presets: `ft-oltin-15x10` (FT CARDS gold card: pre-printed title,
horse emblem at right; **estimated from a photo, not yet calibrated**),
`matn-11x6`, `a6-yotiq`, `maxsus-15x21`.

Flags override presets: `--page A4|A3|card`, `--card-pos X,Y`,
`--card WxH`, `--area WxH`, `--offset X,Y`, `--no-title`.

## Calibrating a card type (do this once per card type and printer)

```bash
.venv/bin/python .claude/skills/taklifnoma-chop/scripts/kalibrovka.py --out buyurtmalar/kalibrovka-a4
```

The output is an A4 .docx with a mm grid. Every 1 cm square is labelled
`X·Y` (A4 cm). Tell the operator:

1. Cut plain paper to exactly the card's size. Feed it the way cards are fed (same tray and guides). Print at A4, scale **100% / Actual size**.
2. Read the grid under the paper's top-left corner → `card_pos`.
3. Lay the printed piece on a real card with the edges matched. Read the clean area's left, top, right and bottom edges, inside the ornament, below the printed title, clear of the emblem, with ~2 mm safety. Then `offset` = (left − card_pos X, top − card_pos Y) and `area` = (right − left, bottom − top).
4. Put the numbers into `cards.json` and set `"calibrated": true`.
5. Do a test print: run `render.py … --guides` (dashed outline of the text area) on plain paper cut to card size. It must sit inside the ornament.

## Text size

- The font size is chosen automatically: the largest that fits the area with a 0.2 cm inner margin (`--padding`). Line spacing is fixed ("exactly"), so Word does not reflow.
- The output prints the body size and the widest line. Below ~11 pt, shorten or re-break that line, or drop the greeting line ("Азиз меҳмонимиз бўлинг!") on small cards. The script refuses anything under 8 pt.
- Times New Roman italic. `{NAMES}` red (#C00000) and bold. Fonts are listed in `fonts.json`.

## Other modes

| Need | Flags |
|---|---|
| Test print outline | `--guides`. Never use that file for the real run. |
| Many cards cut from one sheet | `--sheet A4` (page = sheet, dotted cut lines) |
| Maxsus design (we print the whole card) | `--preset maxsus-15x21 --frame gold --background fon.jpg` (page = card) |
| Colours | `--name-color #hex`, `--text-color #hex` |

## Printing tips for the operator

- In Word, print at scale **100% / "Actual size"** with paper **A4**. Never use "Fit to page". Feed the card the same way as during calibration.
- **Red names smudging** on glossy or metallic cards happens because ink doesn't dry fast on coated stock. Let each card dry 1–2 minutes before stacking, choose a "glossy / photo paper" media type in the printer settings, and if it still smears use `--name-color #A00000` (less ink).
- If every card shifts by the same amount, fix `card_pos` in the preset, not in Word.
