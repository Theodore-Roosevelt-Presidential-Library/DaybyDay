"""Link Day by Day to the Theodore Roosevelt Center (TRC) Digital Library at Dickinson State University.

Input : a compact export of the TRC catalog (one JSON per line: id, date, title, creator[], recipient[],
        type, collection, subject[]), made from the trc-rag harvest of all 141,609 TRC records.
        Usage: python pipeline/link_trc.py <trc_compact.jsonl>
Output: data/trc_by_day.jsonl   per day: count, counts by type, and up to 12 items (TR's own first)
        data/trc_letters.json   our letter (date|direction|correspondent) -> TRC item ids, with match basis

Matching a letter: same date, TR as creator (from_tr) or recipient (to_tr), and the correspondent's
surname equal to a surname on the other side of the TRC record. Only exact-date, exact-surname matches
are kept; nothing is guessed. TRC catalog metadata is linked and credited, not altered.
"""
import json
import re
import sys
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRC_URL = "https://www.theodorerooseveltcenter.org/digital-library/{}/"
SUFFIX = {"jr", "sr", "ii", "iii", "2nd", "3rd", "esq"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z]", "", s)


def trc_surname(name):
    """'Revell, Alexander H. (Alexander Hamilton), 1858-1931' -> 'revell'"""
    return norm(name.split(",")[0]) if name else ""


def our_surname(name):
    toks = [t for t in re.sub(r"\(.*?\)", "", name or "").replace(",", " ").split() if norm(t) not in SUFFIX]
    return norm(toks[-1]) if toks else ""


def trc_given(name):
    """'Revell, Alexander H. (...)' -> 'alexander'"""
    parts = name.split(",")
    return norm(parts[1].split()[0]) if len(parts) > 1 and parts[1].split() else ""


def our_given(name):
    toks = [t for t in re.sub(r"\(.*?\)", "", name or "").split() if norm(t) not in SUFFIX
            and norm(t) not in {"mr", "mrs", "miss", "dr", "senator", "governor", "general", "colonel", "captain", "judge", "president", "secretary", "admiral", "major", "sir", "lord", "lady"}]
    return norm(toks[0]) if len(toks) > 1 else ""


def same_person(our_name, trc_name):
    if trc_surname(trc_name) != our_surname(our_name):
        return False
    a, b = our_given(our_name), trc_given(trc_name)
    if not a or not b:
        return True
    return a == b or (len(a) == 1 and b.startswith(a)) or (len(b) == 1 and a.startswith(b))


def is_tr(name):
    return name.startswith("Roosevelt, Theodore, 1858-1919")


def main(src):
    by_day = defaultdict(list)
    for line in open(src):
        r = json.loads(line)
        by_day[r["date"]].append(r)
    people = {p["id"]: p for p in json.load(open(ROOT / "data/people.json"))}

    # per-day archive digest
    with open(ROOT / "data/trc_by_day.jsonl", "w") as f:
        for d in sorted(by_day):
            items = by_day[d]
            def rank(r):
                tr_side = any(is_tr(c) for c in r["creator"]) * 2 + any(is_tr(c) for c in r["recipient"])
                return (-tr_side, r["type"] != "Letter", r["title"])
            top = sorted(items, key=rank)[:12]
            f.write(json.dumps({"date": d, "count": len(items),
                                "types": dict(Counter(r["type"] or "Other" for r in items).most_common()),
                                "items": [{"id": r["id"], "title": r["title"], "type": r["type"]} for r in top]},
                               ensure_ascii=False) + "\n")

    # letter matching
    matches, tried = {}, 0
    for line in open(ROOT / "data/days.jsonl"):
        day = json.loads(line)
        cands = by_day.get(day["date"], [])
        for l in day["letters"]:
            tried += 1
            corr = l["correspondent"]
            name = people[corr]["name"] if l.get("correspondent_resolved") and corr in people else corr
            sn = our_surname(name)
            if len(sn) < 3 or sn in {"unknown", "unidentified", "anonymous"}:
                continue
            hits = []
            for r in cands:
                if l["direction"] == "from_tr" and any(is_tr(c) for c in r["creator"]):
                    if any(same_person(name, x) for x in r["recipient"]):
                        hits.append(r["id"])
                elif l["direction"] == "to_tr" and any(is_tr(c) for c in r["recipient"]):
                    if any(same_person(name, x) for x in r["creator"]):
                        hits.append(r["id"])
            if hits:
                matches[f"{day['date']}|{l['direction']}|{corr}"] = {"trc": hits[:3], "basis": "date+name"}
    json.dump(matches, open(ROOT / "data/trc_letters.json", "w"), ensure_ascii=False, indent=0)
    print(f"days with TRC items: {len(by_day)}  items: {sum(len(v) for v in by_day.values())}")
    print(f"letters matched: {len(matches)} of {tried} ({100 * len(matches) / max(1, tried):.1f}%)")


if __name__ == "__main__":
    main(sys.argv[1])
