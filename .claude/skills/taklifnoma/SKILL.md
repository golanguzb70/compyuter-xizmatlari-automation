---
name: taklifnoma
description: Create a print-ready wedding / to'y invitation (taklifnoma) as a Word .docx file in Uzbek Cyrillic or Latin — nikoh, kelin to'yi, qizlar bazmi, sunnat, aqiqa, muchal, yubiley, beshik, fotiha, and combined occasions. Use whenever the user asks for a taklifnoma / таклифнома / invitation / to'y kartasi, gives to'y details (names, date, nahorgi osh, to'yxona, "Hurmat bilan"), or asks for variants (misollar) of an invitation.
---

# Taklifnoma (wedding & to'y invitations)

The shop prints Qashqadaryo (Chiroqchi) village-style invitations onto
ready-made cards. The text area on the card is **11 × 6 cm** unless the
operator says otherwise.

## Hard rules

1. **Ask the alphabet every time** — Kirill or Lotin — with AskUserQuestion,
   before writing any text. Never assume it from the language the operator
   typed in (operators often type Latin but want a Cyrillic card).
2. **Deliver only Word (.docx) files.** No PDF, PNG or other files go to the
   operator or into the order folder. Previews for your own checking go to a
   temp folder (`render.py --preview`).
3. **Every text passes `check.py` with 0 errors** before rendering.
4. Never print with `____` blanks left in — ask for the missing detail or
   drop that line.

## Workflow

### 1. Collect the details (one AskUserQuestion round, max 4 questions)

Always ask **alifbo**. Then ask only what is missing from the message:

| Detail | Notes |
|---|---|
| Occasion(s) | nikoh / kelin to'yi, qizlar bazmi, sunnat, aqiqa, muchal, yubiley, beshik, fotiha — may be combined on one card |
| Names | kuyov + kelin, or the child(ren), or bobo/momo. Optional for some cards |
| Date | weekday is computed by `check.py`, never guessed |
| Meal / time | «Наҳорги ош» (morning, usually no time) or «Базм» / дастурхон with a time |
| Signature | "Ҳурмат билан: ___ бобо ўғли ___лар хонадони" |
| Address | tuman, MFY / qishloq, optional «___» тўйхонаси |
| Type | **oddiy** (text onto a ready card — default) or **maxsus** (designed card with frame/background) |
| Variants | how many versions (operators write "misollar soni: N") |
| Card type | which preset in `taklifnoma-chop/cards.json` (e.g. `ft-oltin-15x10`). Ask if more than one card type exists; a new card must be calibrated first |

Spelling the operator's input: they type quickly in Latin without special
letters ("tuyxona", "Naxorgi", "Shoxsanam"). Convert to correct spelling —
тўйхона, Наҳорги, Шоҳсанам — and mention notable fixes in your reply.

### 2. Write the text

Start from [references/shablonlar.md](references/shablonlar.md) — 13
Cyrillic templates in render markup, plus grammar rules for names and
suffixes. For **Lotin**, write the Cyrillic text first and convert:

```bash
.venv/bin/python .claude/skills/taklifnoma-imlo/scripts/translit.py --to lat 1.txt > 1-lat.txt
```

then read the result — transliteration is a first draft.

For N variants, vary the wording meaningfully (classic, "Ҳурмат ва эҳтиром
ила", big date block, "келин тушиши шодиёнасида", warmer phrasing) — don't
just swap one word. Keep every variant to ~8–10 lines so the font stays
≥ 11 pt in the 11 × 6 area.

Order folder: `buyurtmalar/<YYYY-MM-DD>-<familiya>/` with `1.txt … N.txt`.

### 3. Proofread

```bash
.venv/bin/python .claude/skills/taklifnoma-imlo/scripts/check.py --alphabet cyrl \
    --font "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf" 1.txt
```

Fix every ❌. Review ⚠️ (a "double space" warning on a spaced title or big
date line is expected). See the `taklifnoma-imlo` skill for details.

### 4. Render the Word files

```bash
.venv/bin/python .claude/skills/taklifnoma-chop/scripts/render.py 1.txt \
    --preset ft-oltin-15x10 --out buyurtmalar/<folder>/taklifnoma-1 --preview
```

The Word page is **A4**, with the text placed at the card's measured clean
area. If the card has a pre-printed «АССАЛОМУ АЛАЙКУМ!», the `# ` title line
is dropped automatically, so keep it in the .txt.

Open the preview PNG it prints (temp folder) with Read and check:
- the text sits inside the dashed card outline, in the clean area;
- the names are red;
- the body font is ≥ 11 pt.

If the font is too small, shorten or re-break lines rather than accept
tiny text. If the preset says `"calibrated": false`, tell the operator the
position is an estimate and point them to calibration in `taklifnoma-chop`.
Options for maxsus designs, test prints and A4 sheets are in the
`taklifnoma-chop` skill.

### 5. Report

Short table: variant № → what is different → font size. Give the paths to
the .docx files only. Mention spelling corrections you made and anything you
assumed (district, word order of the signature, etc.).

## Setup (first run on a machine)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```
