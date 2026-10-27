"""Link Day by Day to the Library's speech bank (speeches.labs.trlibrary.com).

Input : the speech bank's speech list, /api/v1/speeches.json (one row per speech: id, date, prec,
        title, place, kind, themes, words, text, trc, loc, occasion).
        Usage: python pipeline/link_speeches.py [path-or-url]   (default: the live API)
Output: data/speeches_by_day.json   date -> [{id, title, kind, full_text, url}]

Only speeches dated to the day (prec == "day") are linked; month- or year-dated ones are left out
rather than pinned to a guessed day.
"""
import json
import sys
import urllib.request
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = "https://speeches.labs.trlibrary.com/"
API = SITE + "api/v1/speeches.json"


def load(src):
    if src.startswith("http"):
        with urllib.request.urlopen(src, timeout=60) as r:
            return json.load(r)
    return json.load(open(src))


def main(src=API):
    rows = load(src)["speeches"]
    by_day, skipped = defaultdict(list), 0
    for s in rows:
        if s.get("prec") != "day" or not s.get("date"):
            skipped += 1
            continue
        by_day[s["date"]].append({"id": s["id"], "title": s["title"], "kind": s["kind"],
                                  "full_text": bool(s.get("text")),
                                  "url": f"{SITE}speech.html?id={s['id']}"})
    json.dump(dict(sorted(by_day.items())), open(ROOT / "data/speeches_by_day.json", "w"), indent=0, ensure_ascii=False)
    print(f"{sum(len(v) for v in by_day.values())} speeches on {len(by_day)} days; {skipped} not dated to the day")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else API)
