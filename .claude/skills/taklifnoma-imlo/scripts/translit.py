#!/usr/bin/env python3
"""Uzbek Cyrillic <-> Latin transliteration (official 1995 Latin alphabet).

Usage:
    translit.py --to lat  < input.txt  > output.txt
    translit.py --to cyrl input.txt
    translit.py --to lat --text "Азиз меҳмонимиз бўлинг!"

Inline markup used by the invitation tools ({NAME}, **bold**, "# " line
prefixes) passes through untouched.

The result is a strong first draft, not a final text: Latin->Cyrillic in
particular is ambiguous for some loanwords (ts/ц, ye/е, e/э). Always run
check.py and read the output before printing.
"""
import argparse
import re
import sys

O_TICK = "ʻ"  # ʻ  used in oʻ, gʻ
APOS = "ʼ"    # ʼ  tutuq belgisi (ъ)

CYR_VOWELS = set("аеёиоуэюяўАЕЁИОУЭЮЯЎ")
LAT_VOWELS = set("aeiouAEIOU")

CYR2LAT = {
    "а": "a", "б": "b", "в": "v", "г": "g", "д": "d", "ё": "yo", "ж": "j",
    "з": "z", "и": "i", "й": "y", "к": "k", "л": "l", "м": "m", "н": "n",
    "о": "o", "п": "p", "р": "r", "с": "s", "т": "t", "у": "u", "ф": "f",
    "х": "x", "ч": "ch", "ш": "sh", "щ": "sh", "ъ": APOS, "ы": "i", "ь": "",
    "э": "e", "ю": "yu", "я": "ya", "ў": "o" + O_TICK, "қ": "q",
    "ғ": "g" + O_TICK, "ҳ": "h",
}


def _apply_case(lat: str, src: str, prev: str, nxt: str) -> str:
    if not src.isupper() or not lat:
        return lat
    # All-caps word (ШАРОФ -> SHAROF) vs. capitalised word (Шароф -> Sharof)
    if len(lat) > 1 and (prev.isupper() or nxt.isupper()):
        return lat.upper()
    return lat[0].upper() + lat[1:]


def cyr_to_lat(text: str) -> str:
    out = []
    n = len(text)
    for i, ch in enumerate(text):
        low = ch.lower()
        prev = text[i - 1] if i > 0 else ""
        nxt = text[i + 1] if i + 1 < n else ""
        word_start = not prev.isalpha()
        if low == "е":
            lat = "ye" if (word_start or prev in CYR_VOWELS or prev.lower() in "ъь") else "e"
        elif low == "ц":
            lat = "ts" if (prev in CYR_VOWELS and not word_start) else "s"
        elif low in CYR2LAT:
            lat = CYR2LAT[low]
        else:
            out.append(ch)
            continue
        out.append(_apply_case(lat, ch, prev, nxt))
    return "".join(out)


def normalize_latin_apostrophes(text: str) -> str:
    """o' g' o` g` o’ -> oʻ gʻ ; other apostrophes after letters -> ʼ."""
    text = re.sub(r"([oOgG])['`’‘ʼ]", lambda m: m.group(1) + O_TICK, text)
    text = re.sub(r"(?<=[A-Za-z])['’`](?=[A-Za-z])", APOS, text)
    return text


LAT_DIGRAPHS = [
    ("o" + O_TICK, "ў"), ("g" + O_TICK, "ғ"), ("sh", "ш"), ("ch", "ч"),
    ("yo", "ё"), ("yu", "ю"), ("ya", "я"), ("ye", "е"),
]
LAT_SINGLE = {
    "a": "а", "b": "б", "d": "д", "e": "е", "f": "ф", "g": "г", "h": "ҳ",
    "i": "и", "j": "ж", "k": "к", "l": "л", "m": "м", "n": "н", "o": "о",
    "p": "п", "q": "қ", "r": "р", "s": "с", "t": "т", "u": "у", "v": "в",
    "x": "х", "y": "й", "z": "з", APOS: "ъ",
}


def lat_to_cyr(text: str) -> str:
    text = normalize_latin_apostrophes(text)
    out = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        prev = text[i - 1] if i > 0 else ""
        two = text[i:i + 2]
        hit = None
        for lat, cyr in LAT_DIGRAPHS:
            if two.lower() == lat:
                hit = (cyr, 2)
                break
        if hit is None:
            low = ch.lower()
            if low == "e":
                # word-initial e is э (ertalab -> эрталаб)
                hit = ("э" if not prev.isalpha() else "е", 1)
            elif low in LAT_SINGLE or ch == APOS:
                hit = (LAT_SINGLE.get(low, LAT_SINGLE.get(ch)), 1)
        if hit is None:
            out.append(ch)
            i += 1
            continue
        cyr, size = hit
        if ch.isupper():
            cyr = cyr.upper()
        out.append(cyr)
        i += size
    return "".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--to", choices=["lat", "cyrl"], required=True)
    ap.add_argument("--text")
    ap.add_argument("file", nargs="?")
    args = ap.parse_args()
    if args.text is not None:
        src = args.text
    elif args.file:
        with open(args.file, encoding="utf-8") as f:
            src = f.read()
    else:
        src = sys.stdin.read()
    sys.stdout.write(cyr_to_lat(src) if args.to == "lat" else lat_to_cyr(src))
    if args.text is not None:
        sys.stdout.write("\n")


if __name__ == "__main__":
    main()
