---
name: taklifnoma-imlo
description: Proofread and transliterate Uzbek invitation text (Cyrillic ↔ Latin). Use for any taklifnoma text before printing, when a customer brings their own text or an old Word file to fix, when converting a card between Kirill and Lotin, or when the operator asks to check spelling (imlo), dates or names.
---

# Taklifnoma imlo (proofreading & transliteration)

Word does not check Uzbek, so typos reach the printed card. Two scripts
cover this. Run them with the repo venv: `.venv/bin/python`.

## Ask the alphabet

If the target alphabet is not already settled in this order, ask the
operator: Kirill or Lotin (AskUserQuestion). Never guess.

## check.py — proofreader

```bash
.venv/bin/python .claude/skills/taklifnoma-imlo/scripts/check.py --alphabet cyrl|lat \
    [--font path/to/Font.ttf] matn.txt
```

Exit code 1 means there are errors (❌). It catches:

- **Mixed alphabets inside a word**, e.g. a Latin `A` or `o` typed inside a Cyrillic word. These look identical on screen but break search and some fonts.
- Whole words written in the wrong alphabet.
- **Known typos**: октябь→октябр, нойабр→ноябр, рестарани→ресторани, Йасмена→Ясмина, етамиз→этамиз, Russian-style months with ь, and more (the `TYPOS` dict).
- **Broken suffixes**: -ларнг / -ойнг → -ларнинг / -нинг.
- Simplified letters (булинг, туй, никох, Хурмат), reported as warnings with the correct form (бўлинг, тўй, никоҳ, Ҳурмат).
- **Dates**: month spelling, whether the date exists, whether the weekday written nearby matches (e.g. ЖУМА 20 НОЯБР), and whether the date is in the past.
- Times: 25:00 is an error, and 14.00 should be written 14:00.
- Unfilled `____` / `__:__` blanks, unpaired «» { } **, `"` instead of « », and stray spaces.
- `--font`: letters missing from the print font (ў қ ғ ҳ ʻ ʼ).

The double-space warning on a spaced title or a `## ЖУМА   20   НОЯБР` line is
expected; ignore it there.

When you meet a new recurring typo, add it to `TYPOS` or `SIMPLIFIED_CYRL`
in check.py so it is caught next time.

## translit.py — Kirill ↔ Lotin

```bash
.venv/bin/python .claude/skills/taklifnoma-imlo/scripts/translit.py --to lat matn.txt > matn-lat.txt
.venv/bin/python .claude/skills/taklifnoma-imlo/scripts/translit.py --to cyrl --text "Assalomu alaykum"
```

- Follows the official 1995 Latin alphabet: ў→oʻ, ғ→gʻ (U+02BB ʻ), ъ→ʼ (U+02BC), ҳ→h, х→x, қ→q, е→ye at the start of a word or after a vowel, ц→s/ts.
- Keeps the case of all-caps names: ШОҲСАНАМОЙ → SHOHSANAMOY.
- Render markup (`{…}`, `**…**`, `#`) passes through unchanged.
- In Latin input, `o' g' o‘` are normalised to `oʻ gʻ`.
- **Lotin → Kirill is ambiguous** for some loanwords (e/э, ts/ц, s+h as in "Is'hoq"). Always read the result, then run check.py on it.

## Spelling notes

- Months: январ феврал март апрел май июн июл август сентябр октябр ноябр декабр. Latin: yanvar fevral mart aprel may iyun iyul avgust sentabr oktabr noyabr dekabr. No ь.
- Weekdays: душанба сешанба чоршанба пайшанба жума шанба якшанба. Latin: dushanba seshanba chorshanba payshanba juma shanba yakshanba.
- Operators type х for ҳ ("Naxorgi", "Shoxsanam"). The correct forms are **Наҳорги**, **Шоҳсанам**, **Ҳурмат**, **меҳмон**, **никоҳ**. Keep **х** in хонадон, дастурхон, тўйхона, Холяров.
- Write the date as `2026 йил 15-ноябр` and the time as `соат 14:00 да`.
