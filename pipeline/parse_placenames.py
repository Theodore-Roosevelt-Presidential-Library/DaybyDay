"""Parse the OCR of the TRA Chronological Record place-names index (TRC-CR-1 PlaceNames).

The index lists each place TR visited with the dates he was there:

    ALBANY, New York            1882  Jan. 2 - 5
                                      Jan. 9 - 13
                                1883  Dec. 26 - Jan. 18, 1884
    FLORENCE, Italy             1870  Feb. 19 - Mar. 5

The place/date pairs are facts (where TR was on which days); no TRA prose is
carried forward. Output:
    data/places_index.json   one record per place with its visit ranges
    work/placenames_unparsed.txt  lines the parser could not use (for review)

Usage: python pipeline/parse_placenames.py <dir-of-tesseract-txt-pages>
"""
import csv
import datetime as dt
import json
import re
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6, "june": 6,
    "jul": 7, "july": 7, "aug": 8, "sep": 9, "sept": 9, "oct": 10, "nov": 11, "dec": 12,
}
MON_RE = r"(Jan|Feb|Mar|Apr|May|June|Jun|July|Jul|Aug|Sept|Sep|Oct|Nov|Dec)[a-z]*\.?"

# PLACE, Region  [optional (Continued)]  — place is upper case, region mixed case
PLACE_RE = re.compile(
    r"^(?P<place>[A-Z0-9][A-Z0-9'’.&/\- ]*[A-Z.)](?:\s*\([^)]*\))?)"
    r"(?:\s*,\s*(?P<region>[A-Z][A-Za-z.'’ \-]+?))?"
    r"(?:\s*\((?:Continued|continued|Cont\.?)\))?"
    r"(?=\s+(?:1[89]\d\d)\b|\s*$)"
)
YEAR_RE = re.compile(r"\b(1[89]\d\d)\b")


def slugify(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def clean_line(l):
    l = re.sub(r"(\d)l(?=\s*-)", r"\1", l)
    l = re.sub(r"\bl1(?=\s*-)", "1", l)
    l = l.replace("—", "-").replace("–", "-").replace("~", "-").replace("|", " ")
    l = re.sub(r"(?<=\d)l\b|\bl(?=\d)", "1", l)   # 1l -> 11
    l = re.sub(r"(?<=\d)[Oo]\b", "0", l)
    l = re.sub(r"\s+", " ", l).strip(" '‘’\".,")
    return l


def month_num(s):
    k = s.rstrip(".").lower()
    return MONTHS.get(k) or MONTHS[k[:3]]


def parse_ranges(text, year):
    """Return list of (start_date, end_date) from 'Jan. 2 - 5', 'Dec. 26 - Jan. 18, 1884', 'Dec. 27, 28'."""
    out = []
    text = text.strip()
    if not text:
        return out, ""
    # tokenise into month/day/year tokens
    # rebuild sequence of (kind, value)
    seq = []
    for t in re.finditer(MON_RE + r"|\d{4}|\d{1,2}|-|,", text):
        s = t.group(0)
        if re.match(MON_RE, s):
            seq.append(("m", month_num(s)))
        elif re.fullmatch(r"\d{4}", s):
            seq.append(("y", int(s)))
        elif s.isdigit():
            seq.append(("d", int(s)))
        else:
            seq.append((s, None))
    i, cur_m = 0, None
    leftovers = []
    while i < len(seq):
        k, v = seq[i]
        if k == "m":
            cur_m = v
            i += 1
            continue
        if k == "d" and cur_m:
            sd = (year, cur_m, v)
            # range?
            if i + 1 < len(seq) and seq[i + 1][0] == "-":
                j = i + 2
                em, ey = cur_m, year
                if j < len(seq) and seq[j][0] == "m":
                    em = seq[j][1]
                    j += 1
                if j < len(seq) and seq[j][0] == "d":
                    ed = seq[j][1]
                    j += 1
                    if j + 1 < len(seq) and seq[j][0] == "," and seq[j + 1][0] == "y":
                        ey = seq[j + 1][1]
                        j += 2
                    elif j < len(seq) and seq[j][0] == "y":
                        ey = seq[j][1]
                        j += 1
                    if em < cur_m and ey == year:
                        ey = year + 1
                    out.append((sd, (ey, em, ed)))
                    cur_m = em
                    i = j
                    continue
            out.append((sd, sd))
            i += 1
            continue
        if k in (",", "-"):
            i += 1
            continue
        leftovers.append(str(v))
        i += 1
    good = []
    for a, b in out:
        try:
            da, db = dt.date(*a), dt.date(*b)
        except ValueError:
            leftovers.append(f"bad-date {a}-{b}")
            continue
        if db < da or (db - da).days > 400:
            leftovers.append(f"bad-range {da}-{db}")
            continue
        good.append((da.isoformat(), db.isoformat(), "day"))
    return good, " ".join(leftovers)


def parse_month_ranges(text, year):
    """'June - Sept', 'Jan. - June', 'Mar. - Apr.', 'March', 'Late Mar.' -> whole-month spans."""
    t = re.sub(r"\b(Early|Mid|Late|End of|Sometime in|Between)\b-?", "", text, flags=re.I).strip(" .?")
    t = re.sub(r"\((?:Mon|Tue|Wed|Thu|Fri|Sat|Sun)[a-z]*\.?\)", "", t)
    m = re.fullmatch(MON_RE + r"\s*(\d{1,2})?\s*-\s*" + MON_RE + r"\s*(\d{1,2})?\s*,?\s*(1[89]\d\d)", t.strip())
    if m:
        toks = re.findall(MON_RE, t)
        m1, m2 = month_num(toks[0]), month_num(toks[1])
        d1 = int(m.group(2)) if m.group(2) else 1
        y2 = int(m.group(5))
        start = dt.date(year, m1, d1)
        end = dt.date(y2, m2, int(m.group(4))) if m.group(4) else (dt.date(y2 + (m2 == 12), (m2 % 12) + 1, 1) - dt.timedelta(days=1))
        if start <= end and (end - start).days < 400:
            return [(start.isoformat(), end.isoformat(), "day" if m.group(2) and m.group(4) else "month")], ""
        return [], ""
    m = re.fullmatch(MON_RE + r"\s*(?:-\s*" + MON_RE + r")?\s*\.?\s*\??", t)
    if not m or re.search(r"\d", t):
        return [], ""
    toks = re.findall(MON_RE, t)
    m1 = month_num(toks[0])
    m2 = month_num(toks[1]) if len(toks) > 1 else m1
    y2 = year + 1 if m2 < m1 else year
    start = dt.date(year, m1, 1)
    end = (dt.date(y2 + (m2 == 12), (m2 % 12) + 1, 1) - dt.timedelta(days=1))
    return [(start.isoformat(), end.isoformat(), "month")], ""


HEAD_START = re.compile(r"^(?:Mc)?[A-Z][A-Z.]")   # PLACE names are upper case


def split_head(head):
    """'CHRISTIANA [OSLO], Norway' -> name, region, notes"""
    notes = re.findall(r"\[([^\]]*)\]", head)
    head = re.sub(r"\[[^\]]*\]|\{[^}]*\]", " ", head)
    head = re.sub(r"\((?:Continued|continued|Cont\.?)\)", " ", head)
    head = re.sub(r"\s+", " ", head).strip(" ,")
    if "," in head:
        name, region = head.split(",", 1)
    else:
        name, region = head, ""
    region = re.sub(r"\s+", " ", region).strip(" ,")
    return name.strip(), region, [n.strip() for n in notes if n.strip()]


def page_lines(tsv_path):
    """Yield (left_text, right_text, left_x) per OCR line, split at the year column."""
    rows = list(csv.DictReader(open(tsv_path, errors="ignore"), delimiter="\t", quoting=csv.QUOTE_NONE))
    words = [r for r in rows if r.get("level") == "5" and (r.get("text") or "").strip()]
    if not words:
        return
    years = [int(w["left"]) for w in words if re.fullmatch(r"1[89]\d\d\.?", w["text"].strip())]
    months = sorted(int(w["left"]) for w in words if re.fullmatch(MON_RE, w["text"].strip()))
    cands = []
    if years:
        cands.append(sorted(years)[len(years) // 4] - 40)
    if months:
        cands.append(months[len(months) // 10] - 260)   # year column sits ~210px left of the months
    split = min(cands) if cands else 1300
    lines = {}
    for w in words:
        lines.setdefault((int(w["block_num"]), int(w["par_num"]), int(w["line_num"])), []).append(w)
    ordered = sorted(lines.values(), key=lambda ws: min(int(w["top"]) for w in ws))
    for ws in ordered:
        ws.sort(key=lambda w: int(w["left"]))
        left = [w for w in ws if int(w["left"]) < split and re.search(r"[A-Za-z0-9\[\](]{2,}|^[A-Z]$", w["text"])]
        right = [w for w in ws if int(w["left"]) >= split]
        yield (" ".join(w["text"] for w in left), " ".join(w["text"] for w in right),
               int(left[0]["left"]) if left else None)


def main(src_dir):
    pages = sorted(Path(src_dir).glob("p-*.tsv"))
    entries, unparsed = [], []     # entries: [heading_text, [visits], pages]
    cur, cur_year = None, None
    for p in pages:
        pno = int(re.search(r"(\d+)", p.stem).group(1))
        plines = list(page_lines(p))
        xs = sorted(x for l_, _, x in plines if x is not None and HEAD_START.match(re.sub(r"^[^A-Za-z]+", "", l_)))
        # heading column = smallest x shared by at least two heading-like lines (ignores stray marks)
        base = next((x for i, x in enumerate(xs) if any(abs(x - y) <= 25 for y in xs[i + 1:i + 4])), xs[0] if xs else 0)
        head_x = base
        for left, right, lx in plines:
            ym_left = re.search(r"\s(1[89]\d\d)\.?$", " " + left)
            if ym_left:   # skewed page: year slipped into the left column
                left, right = left[:ym_left.start()].rstrip(), ym_left.group(1) + " " + right
            left = clean_line(left)
            left = re.sub(r"^[^A-Za-z0-9\[{(]+", "", left)
            if left and re.fullmatch(r"-?\s*\d{1,3}\s*-?", left):
                left = ""
            if left:
                if lx is not None and lx <= head_x + 70 and HEAD_START.match(left) and not re.match(MON_RE + r"(\s|$)", left):
                    cur = {"heading": left, "visits": [], "pages": [pno]}
                    entries.append(cur)
                    head_x = lx
                elif cur is not None:
                    if re.match(r"^[\[{(]?see also", left, re.I):
                        cur.setdefault("see_also", []).append(re.sub(r"[\[\]{}()]|see also", "", left, flags=re.I).strip())
                    else:
                        cur["heading"] += " " + left
            r = clean_line(right)
            r = re.sub(r"(\d)l(?=\s*-)", r"\1", r)
            r = re.sub(r"\bl1(?=\s*-)", "1", r)
            r = re.sub(r"\bll\b", "11", r)
            r = re.sub(r"\bdune\b", "June", r)
            r = re.sub(r"\bdan\.", "Jan.", r)
            r = re.sub(r"\bOcz\.+", "Oct.", r)
            r = re.sub(r"\bDer\.+", "Dec.", r)
            r = re.sub(r"^[^A-Za-z0-9]+", "", r)
            if not r:
                continue
            if cur is None:
                unparsed.append(f"p{pno}: {right}")
                continue
            if pno not in cur["pages"]:
                cur["pages"].append(pno)
            ym = YEAR_RE.match(r)
            if ym:
                cur_year = int(ym.group(1))
                r = r[ym.end():].strip(" .")
            if not r or cur_year is None:
                continue
            rngs, left_over = parse_month_ranges(r, cur_year)
            if not rngs:
                rngs, left_over = parse_ranges(r, cur_year)
            cur["visits"].extend(rngs)
            if left_over.strip() or not rngs:
                unparsed.append(f"p{pno} [{cur['heading'][:30]}/{cur_year}]: {right}  ->  {left_over}")
    places = {}
    for e in entries:
        name, region, notes = split_head(e["heading"])
        key = slugify(f"{name} {region}")
        pl = places.setdefault(key, {"id": key, "index_name": name, "region": region, "notes": [],
                                     "visits": [], "see_also": [], "index_pages": []})
        for n in notes:
            if n not in pl["notes"]:
                pl["notes"].append(n)
        pl["see_also"] += [x for x in e.get("see_also", []) if x not in pl["see_also"]]
        pl["visits"] += e["visits"]
        pl["index_pages"] += [x for x in e["pages"] if x not in pl["index_pages"]]
    for v in places.values():
        seen = {}
        for a, b, prec in v["visits"]:
            seen[(a, b)] = prec
        v["visits"] = [{"start": a, "end": b, "precision": seen[(a, b)]} for a, b in sorted(seen)]
        v["visit_days"] = sum((dt.date.fromisoformat(x["end"]) - dt.date.fromisoformat(x["start"])).days + 1 for x in v["visits"])
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "work").mkdir(exist_ok=True)
    json.dump(sorted(places.values(), key=lambda x: x["id"]), open(ROOT / "data/places_index.json", "w"), indent=1)
    (ROOT / "work/placenames_unparsed.txt").write_text("\n".join(unparsed))
    print(f"places: {len(places)}  visits: {sum(len(v['visits']) for v in places.values())}  unparsed lines: {len(unparsed)}")


if __name__ == "__main__":
    main(sys.argv[1])
