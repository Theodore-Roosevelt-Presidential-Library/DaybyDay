"""Link TR's diary quotes to the original pages of his 1878-1884 pocket diaries.

Input : a checkout of the Library's DiaryExplorer repo (diary.labs.trlibrary.com), which holds a
        page-by-page transcription of the Library of Congress scans (Theodore Roosevelt Papers,
        Series 8, Personal Diaries, Vols. 1-7).
        Usage: python pipeline/link_diaries.py ../DiaryExplorer
Output: data/diary_links.json   quote_key(date, text) -> 
        {volume, page, explorer, loc, loc_title, match}

Each diary quote is compared with the transcription of every page holding writing dated within a day
of it. The best page is kept when most of the quote's words appear on it in order (match >= 0.6).
Failing that, the whole volume is searched (and the 1883 volume for 1884, where T.R. kept his Bighorn
log) with a stricter bar (match >= 0.8).
Otherwise the page dated that day is linked with match null, so readers still land on the right page.
Only links and a match score are stored here; no transcription text is copied.
"""
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import date, timedelta
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXPLORER = "https://diary.labs.trlibrary.com/"
LOC_1884 = "https://www.loc.gov/resource/mss38299a.80701/?sp={}"


def quote_key(ds, text):
    """Stable key for a quote: its date and a short hash of its exact text."""
    return f"{ds}|{hashlib.sha1(text.encode()).hexdigest()[:10]}"


def words(s):
    return re.findall(r"[a-z0-9]+", (s or "").lower().replace("&", " and "))


def block_text(b):
    out = list(b.get("lines") or [])
    for row in b.get("rows") or []:
        out.extend(str(c) for c in (row if isinstance(row, list) else row.values()))
    return " ".join(out)


def pages_by_date(de):
    vols = {v["id"]: v for v in json.load(open(de / "data/volumes.json"))["volumes"]}
    found = defaultdict(list)          # date -> [(page record, words on that page)]
    by_vol = defaultdict(list)         # volume -> every (page record, words) in it

    def add(ds, link, text):
        found[ds].append((link, words(text)))
        by_vol[link["volume"]].append(found[ds][-1])

    for p in json.load(open(de / "data/diary.json"))["pages"]:
        if not p.get("handwriting") or not p.get("date") or not p.get("in_book", True):
            continue
        n = int(p["seq"])
        link = {"volume": "1884", "page": p["seq"], "explorer": f"{EXPLORER}#{p['seq']}",
                "loc": LOC_1884.format(n), "loc_title": vols["1884"]["loc_title"]}
        add(p["date"], link, " ".join(block_text(b) for b in p["handwriting"] if b.get("hand", "TR") == "TR"))
    for vid, v in vols.items():
        if vid == "1884":
            continue
        for p in json.load(open(de / v["file"]))["pages"]:
            if not p.get("handwriting") or not p.get("in_book", True):
                continue
            link = {"volume": vid, "page": p["seq"], "explorer": f"{EXPLORER}#{vid}/{p['seq']}",
                    "loc": f"{v['loc_resource']}?sp={p.get('loc_sp') or 1}", "loc_title": v["loc_title"]}
            per = defaultdict(list)
            for b in p["handwriting"]:
                if b.get("hand", "TR") != "TR":
                    continue
                per[b.get("date") or p.get("date") or (p.get("dates") or [None])[0]].append(block_text(b))
            for ds, texts in per.items():
                if ds:
                    add(ds, link, " ".join(texts))
    return found, by_vol


def score(q, page):
    if not q or not page:
        return 0.0
    m = SequenceMatcher(None, q, page, autojunk=False)
    return sum(b.size for b in m.get_matching_blocks()) / len(q)


def main(de):
    found, by_vol = pages_by_date(Path(de))
    out, stats = {}, defaultdict(int)
    for line in open(ROOT / "data/quotes.jsonl"):
        q = json.loads(line)
        key = quote_key(q["date"], q["text"])
        if q["kind"] != "diary" or not ("1878" <= q["date"][:4] <= "1884"):
            continue
        d = date.fromisoformat(q["date"])
        qw = words(q["text"])
        cands = []
        for off in (0, -1, 1):
            for link, pw in found.get((d + timedelta(days=off)).isoformat(), []):
                cands.append((score(qw, pw), off == 0, link))
        best = max(cands, key=lambda c: (c[0], c[1])) if cands else (0, False, None)
        if best[0] < 0.6 and len(qw) >= 5:
            # Entry written on another page of the volume (a catch-up entry, or the 1884 Bighorn log
            # that T.R. kept in his 1883 volume under printed 1883 dates). Stricter bar: 0.8.
            vols = [q["date"][:4]] + (["1883"] if q["date"][:4] == "1884" else [])
            wide = [(score(qw, pw), False, link) for v in vols for link, pw in by_vol[v]]
            if wide:
                w = max(wide, key=lambda c: c[0])
                if w[0] >= 0.8:
                    best = w
                    stats["found elsewhere in volume"] += 1
        if not cands and best[0] < 0.8:
            stats["no page"] += 1
            continue
        if best[0] >= 0.6:
            out[key] = {**best[2], "match": round(best[0], 2)}
            stats["matched"] += 1
        else:
            same = [c for c in cands if c[1]] or cands
            out[key] = {**max(same, key=lambda c: c[0])[2], "match": None}
            stats["page by date only"] += 1
    json.dump(out, open(ROOT / "data/diary_links.json", "w"), indent=0, sort_keys=True)
    print(dict(stats), "->", len(out), "links")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT.parent / "DiaryExplorer"))
