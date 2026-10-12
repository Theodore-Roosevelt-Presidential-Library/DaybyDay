"""Split the private TRA parse into work chunks for the rewrite pass.

Input : private/tra_chronology.json   (OCR parse of the TRA Chronological Record; never committed)
Output: work/chunks/<id>.json         days with source text, for workers to read
        work/chunks/index.json        chunk list with day counts and character counts

A chunk is a run of consecutive months holding roughly MAX_CHARS of source text.
"""
import json
import re
from collections import OrderedDict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MAX_CHARS = 40_000
MAX_DAYS = 140


def clean(lines):
    t = " ".join(l.strip() for l in lines)
    t = re.sub(r"\s+", " ", t)
    return t.strip()


def main():
    d = json.load(open(ROOT / "private/tra_chronology.json"))
    months = OrderedDict()
    for r in d["records"]:
        if not r["entry"]:
            continue
        key = r["date"][:7]
        months.setdefault(key, []).append({
            "date": r["date"],
            "weekday": r["weekday"],
            "age": r["age"],
            "tra_pages": r["source"],
            "text": clean(r["entry"]),
        })
    chunks, cur, size = [], [], 0
    for key, days in months.items():
        n = sum(len(x["text"]) for x in days)
        if cur and (size + n > MAX_CHARS or len(cur) + len(days) > MAX_DAYS):
            chunks.append(cur)
            cur, size = [], 0
        cur.extend(days)
        size += n
    if cur:
        chunks.append(cur)
    out = ROOT / "work/chunks"
    out.mkdir(parents=True, exist_ok=True)
    index = []
    for c in chunks:
        cid = f"{c[0]['date'][:7]}_{c[-1]['date'][:7]}"
        json.dump({"chunk": cid, "days": c}, open(out / f"{cid}.json", "w"), indent=1, ensure_ascii=False)
        index.append({"chunk": cid, "days": len(c), "chars": sum(len(x["text"]) for x in c)})
    json.dump(index, open(out / "index.json", "w"), indent=1)
    print(len(index), "chunks;", sum(i["days"] for i in index), "days")


if __name__ == "__main__":
    main()
