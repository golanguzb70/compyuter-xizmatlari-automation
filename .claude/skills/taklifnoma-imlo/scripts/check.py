#!/usr/bin/env python3
"""Proofread an Uzbek invitation text before printing.

Usage:
    check.py --alphabet cyrl matn.txt
    check.py --alphabet lat matn.txt --font "/path/to/Font.ttf"

Catches what Word does not: Latin letters hiding inside Cyrillic words (and
vice versa), known typos, broken -нинг/-ларнинг endings, wrong month names,
a weekday that does not match the date, dates in the past, bad times,
non-standard oʻ/gʻ apostrophes, unbalanced «» or {} markup, and characters
missing from the chosen font.

Exit code: 0 = clean (warnings allowed), 1 = errors found.
"""
import argparse
import datetime as dt
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from translit import O_TICK, APOS  # noqa: E402

CYR_LETTERS = "абвгдеёжзийклмнопрстуфхцчшщъыьэюяўқғҳ"
CYR_RE = re.compile(f"[{CYR_LETTERS}{CYR_LETTERS.upper()}]")
LAT_RE = re.compile(r"[A-Za-z]")

MONTHS = {
    "cyrl": ["январ", "феврал", "март", "апрел", "май", "июн", "июл", "август",
             "сентябр", "октябр", "ноябр", "декабр"],
    "lat": ["yanvar", "fevral", "mart", "aprel", "may", "iyun", "iyul", "avgust",
            "sentabr", "oktabr", "noyabr", "dekabr"],
}
WEEKDAYS = {  # Monday first, matches date.weekday()
    "cyrl": ["душанба", "сешанба", "чоршанба", "пайшанба", "жума", "шанба", "якшанба"],
    "lat": ["dushanba", "seshanba", "chorshanba", "payshanba", "juma", "shanba", "yakshanba"],
}

# wrong -> right. Keys are lowercase; matched as whole words.
TYPOS = {
    "cyrl": {
        "октябь": "октябр", "октабр": "октябр", "нойабр": "ноябр", "нояб": "ноябр",
        "декаб": "декабр", "сентабр": "сентябр", "январь": "январ", "февраль": "феврал",
        "апрель": "апрел", "июнь": "июн", "июль": "июл", "сентябрь": "сентябр",
        "октябрь": "октябр", "ноябрь": "ноябр", "декабрь": "декабр",
        "рестарани": "ресторани", "рестаран": "ресторан", "рестаранида": "ресторанида",
        "йасмена": "Ясмина", "йасмина": "Ясмина", "етамиз": "этамиз", "етилади": "этилади",
        "етиладиган": "этиладиган", "таклив": "таклиф", "тавлиф": "таклиф",
        "муносабати": None, "муносабатй": "муносабати", "мунасабати": "муносабати",
        "мунособати": "муносабати", "дастурхонимзга": "дастурхонимизга",
        "асалому": "ассалому", "ассаламу": "ассалому", "алайкум": None, "алейкум": "алайкум",
        "хонадон": None, "хонадни": "хонадони", "тўйхона": None, "туйхонаси": "тўйхонаси",
        "аъзолариингизни": "аъзоларингизни", "аzзоларингизни": "аъзоларингизни",
        "азоларингизни": "аъзоларингизни", "оилаъзоларингизни": "оила аъзоларингизни",
        "нахорги": "наҳорги", "наxорги": "наҳорги", "лутван": "лутфан",
    },
    "lat": {
        "oktyabr": "oktabr", "sentyabr": "sentabr", "noyabir": "noyabr",
        "restaran": "restoran", "restarani": "restorani", "yasmena": "Yasmina",
        "etamiz": None, "taklif": None, "asalomu": "Assalomu", "assalamu": "Assalomu",
        "aleykum": "alaykum", "azolaringizni": "aʼzolaringizni",
        "munosabti": "munosabati", "munasabati": "munosabati", "lutvan": "lutfan",
        "dasturxonimzga": "dasturxonimizga", "nahorgi": None,
    },
}

# Words typed without the special letters -> proper spelling (warning only:
# the shop may use a font that lacks ў қ ғ ҳ; check.py --font will tell).
SIMPLIFIED_CYRL = {
    "булинг": "бўлинг", "туй": "тўй", "туйи": "тўйи", "туйлари": "тўйлари",
    "туйига": "тўйига", "туйхонаси": "тўйхонаси", "никох": "никоҳ", "хурмат": "ҳурмат",
    "мехмонимиз": "меҳмонимиз", "мехмон": "меҳмон", "булиб": "бўлиб", "угли": "ўғли",
    "ўгли": "ўғли", "углининг": "ўғлининг", "кизимиз": "қизимиз", "кизлар": "қизлар",
    "кишлоги": "қишлоғи", "кишлоғи": "қишлоғи", "хамда": "ҳамда", "эхтиром": "эҳтиром",
    "акика": "ақиқа", "чирокчи": "Чироқчи", "кашкадарё": "Қашқадарё", "нахорги": "наҳорги",
    "набирамиз": None, "мучал": None, "фотиха": "фотиҳа", "кизи": "қизи",
    "ташкил": None, "ўтадиган": None, "утадиган": "ўтадиган",
}

MONTH_ROOT = {"cyrl": re.compile(r"^(янв|фев|мар|апр|июн|июл|авг|сен|окт|ноя|нояб|дек)", re.I),
              "lat": re.compile(r"^(yan|fev|apr|iyun|iyul|avg|sen|okt|noy|dek)", re.I)}

WORD_RE = re.compile(r"[^\W\d_][\w" + O_TICK + APOS + r"'’`‘]*", re.UNICODE)


class Report:
    def __init__(self):
        self.items = []

    def add(self, level, line_no, msg):
        self.items.append((level, line_no, msg))

    def print(self):
        if not self.items:
            print("✅ Хато топилмади / Xato topilmadi")
            return
        for level, line_no, msg in sorted(self.items, key=lambda x: (x[1], x[0])):
            icon = "❌" if level == "ERROR" else "⚠️ "
            where = f"{line_no}-qator" if line_no else "umumiy"
            print(f"{icon} [{where}] {msg}")
        e = sum(1 for i in self.items if i[0] == "ERROR")
        w = len(self.items) - e
        print(f"\nJami: {e} xato, {w} ogohlantirish")


def strip_markup(line):
    line = re.sub(r"^#{1,2}\s+", "", line)
    return line.replace("**", "").replace("{", "").replace("}", "")


def check_line_words(line, n, alphabet, rep):
    for m in WORD_RE.finditer(line):
        w = m.group(0)
        has_c, has_l = bool(CYR_RE.search(w)), bool(LAT_RE.search(w))
        if has_c and has_l:
            bad = "".join(ch for ch in w if (LAT_RE.match(ch) if alphabet == "cyrl" else CYR_RE.match(ch)))
            rep.add("ERROR", n, f"«{w}» so'zida aralash alifbo harflari bor ({bad!r}) — klaviatura xatosi")
            continue
        if alphabet == "cyrl" and has_l:
            rep.add("ERROR", n, f"«{w}» lotincha yozilgan, matn kirillda bo'lishi kerak")
            continue
        if alphabet == "lat" and has_c:
            rep.add("ERROR", n, f"«{w}» kirillcha yozilgan, matn lotinda bo'lishi kerak")
            continue
        low = w.lower()
        fix = TYPOS[alphabet].get(low, "")
        if fix:
            rep.add("ERROR", n, f"«{w}» → «{fix}»")
        if alphabet == "cyrl":
            if low.endswith(("рнг", "йнг", "ннг", "знг", "днг")):
                rep.add("ERROR", n, f"«{w}» → «{w[:-2]}{'НИНГ' if w[-2:].isupper() else 'нинг'}» (-нинг / -ларнинг)")
            simp = SIMPLIFIED_CYRL.get(low)
            if simp:
                rep.add("WARN", n, f"«{w}» → «{simp}» (shrift ў қ ғ ҳ harflarini qo'llasa)")
        else:
            if re.search(r"[oOgG]['`’‘]", w):
                rep.add("WARN", n, f"«{w}» — tutuq belgisi standart emas, «oʻ / gʻ» (U+02BB) ishlating")
            if low.endswith(("rng", "yng", "nng")):
                rep.add("ERROR", n, f"«{w}» → «{w[:-2]}ning» (-ning / -larning)")


def find_dates(text, alphabet):
    """Yield (date, weekday_name_or_None, line_no)."""
    months = MONTHS[alphabet]
    yil = "йил" if alphabet == "cyrl" else "yil"
    lines = text.splitlines()
    years = [int(y) for y in re.findall(r"\b(20\d\d)\b", text)]
    default_year = years[0] if years else None
    wd_names = WEEKDAYS[alphabet]
    found = []
    for n, raw in enumerate(lines, 1):
        line = strip_markup(raw).lower()
        # 2026 йил 15-ноябр
        for m in re.finditer(rf"(20\d\d)\s*{yil}\s*(\d{{1,2}})\s*-\s*([^\W\d_]+)", line):
            found.append((int(m.group(1)), int(m.group(2)), m.group(3), n))
        # ЖУМА 20 НОЯБР  (big date line; year may be on next line)
        for m in re.finditer(r"(?<![\d-])(\d{1,2})\s+([^\W\d_]+)", line):
            if m.group(2) in months and default_year:
                found.append((default_year, int(m.group(1)), m.group(2), n))
    results = []
    for year, day, month_word, n in found:
        wd = None
        near = "\n".join(strip_markup(l) for l in lines[max(0, n - 2):n + 1]).lower()
        for name in wd_names:
            if re.search(rf"(?<!\w){name}(?!\w)", near):
                wd = name
                break
        results.append((year, day, month_word, wd, n))
    return results


def check_dates(text, alphabet, today, rep):
    months = MONTHS[alphabet]
    seen = set()
    for year, day, month_word, wd, n in find_dates(text, alphabet):
        key = (year, day, month_word)
        if key in seen:
            continue
        seen.add(key)
        if month_word not in months:
            if MONTH_ROOT[alphabet].match(month_word) or month_word in TYPOS[alphabet]:
                guess = TYPOS[alphabet].get(month_word) or "?"
                rep.add("ERROR", n, f"oy nomi «{month_word}» noto'g'ri (to'g'risi: {guess}). Oylar: {', '.join(months)}")
            continue
        try:
            d = dt.date(year, months.index(month_word) + 1, day)
        except ValueError:
            rep.add("ERROR", n, f"{day}-{month_word} {year} — bunday sana yo'q")
            continue
        real_wd = WEEKDAYS[alphabet][d.weekday()]
        if wd and wd != real_wd:
            rep.add("ERROR", n, f"{d:%d.%m.%Y} — {real_wd.upper()}, matnda esa «{wd.upper()}» yozilgan")
        else:
            rep.add("INFO", n, f"sana: {d:%d.%m.%Y} ({real_wd})")
        if d < today:
            rep.add("ERROR", n, f"sana {d:%d.%m.%Y} o'tib ketgan (bugun {today:%d.%m.%Y})")
        elif (d - today).days > 365:
            rep.add("WARN", n, f"sana {d:%d.%m.%Y} — bir yildan ko'p keyin, yilni tekshiring")


def check_times(lines, rep):
    for n, line in enumerate(lines, 1):
        for m in re.finditer(r"\b(\d{1,2})[:.](\d{2})\b", line):
            h, mi = int(m.group(1)), int(m.group(2))
            if h > 23 or mi > 59:
                rep.add("ERROR", n, f"vaqt «{m.group(0)}» noto'g'ri")
            elif "." in m.group(0):
                rep.add("WARN", n, f"vaqt «{m.group(0)}» → «{h:02d}:{mi:02d}» ko'rinishida yozing")


def check_structure(lines, rep):
    for n, line in enumerate(lines, 1):
        if line.count("{") != line.count("}"):
            rep.add("ERROR", n, "{ } qavslar juft emas (ism belgisi)")
        if line.count("**") % 2:
            rep.add("ERROR", n, "** qalin belgisi juft emas")
        if line.count("«") != line.count("»"):
            rep.add("ERROR", n, "« » qo'shtirnoq juft emas")
        if '"' in line:
            rep.add("WARN", n, 'oddiy " qo\'shtirnoq o\'rniga « » ishlating')
        body = strip_markup(line)
        if line.rstrip() != line:
            rep.add("WARN", n, "qator oxirida ortiqcha probel")
        is_spaced = re.fullmatch(r"(\S )+\S?\s*!?", body.strip() + " ") or re.search(r"(\S ){4,}", body)
        if "  " in body.strip() and not is_spaced:
            rep.add("WARN", n, "ikki marta probel")
        if re.search(r"_{3,}", line):
            rep.add("ERROR", n, "to'ldirilmagan joy (____) qolgan")
        if re.search(r"__:__|__-", line):
            rep.add("ERROR", n, "to'ldirilmagan sana/vaqt qolgan")
        if re.search(r"\s[,.!:]", body) and not is_spaced:
            rep.add("WARN", n, "tinish belgisidan oldin probel")


def check_font(text, font_path, rep):
    try:
        from reportlab.pdfbase.ttfonts import TTFont
    except ImportError:
        rep.add("WARN", 0, "reportlab o'rnatilmagan — shrift tekshirilmadi")
        return
    face = TTFont("chk", font_path).face
    missing = sorted({ch for ch in strip_markup(text) if not ch.isspace() and ord(ch) not in face.charWidths})
    if missing:
        rep.add("ERROR", 0, f"shriftda yo'q harflar: {' '.join(missing)} — boshqa shrift tanlang yoki harfni almashtiring")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--alphabet", choices=["cyrl", "lat"], required=True)
    ap.add_argument("--font", action="append", default=[], help="TTF to check glyph coverage (repeatable)")
    ap.add_argument("--today", help="YYYY-MM-DD, default: system date")
    ap.add_argument("--quiet-info", action="store_true")
    ap.add_argument("file")
    args = ap.parse_args()
    with open(args.file, encoding="utf-8") as f:
        text = f.read()
    today = dt.date.fromisoformat(args.today) if args.today else dt.date.today()
    lines = text.splitlines()
    rep = Report()
    for n, line in enumerate(lines, 1):
        check_line_words(strip_markup(line), n, args.alphabet, rep)
    check_structure(lines, rep)
    check_times(lines, rep)
    check_dates(text, args.alphabet, today, rep)
    for font in args.font:
        check_font(text, font, rep)
    if args.quiet_info:
        rep.items = [i for i in rep.items if i[0] != "INFO"]
    else:
        for level, n, msg in [i for i in rep.items if i[0] == "INFO"]:
            print(f"ℹ️  [{n}-qator] {msg}")
        rep.items = [i for i in rep.items if i[0] != "INFO"]
    rep.print()
    sys.exit(1 if any(i[0] == "ERROR" for i in rep.items) else 0)


if __name__ == "__main__":
    main()
