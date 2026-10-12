"""Extract where TR was from each day's own place heading in the TRA record.

Entries in the Chronological Record usually open with an ALL-CAPS place: "SAGAMORE HILL - ...",
"MILWAUKEE, Wisconsin - ...", "S.S. HAMBURG - ...". That heading is the record's own statement of
where TR was that day, so it outranks the separate place-names index. Only the resolved place ids are
written out (facts, no TRA prose).

Input : private/tra_chronology.json, data/places.json
Output: data/day_headers.json  {date: {"ids": [place ids in order], "raw": [heading text]}}
"""
import json
import re
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HEAD = re.compile(r"(?:^|[\s.;)\]]\s*)((?:S\.S\.\s|U\.S\.S\.\s)?[A-Z][A-Z'’.&/,\- ]{2,48}?[A-Z.])(?:,\s*[A-Z][a-z]+(?:\s[A-Z][a-z]+)?)?\s*[-–—:]\s")
NOISE = {"T.R", "TR", "LETTERS", "NOTE", "NOTES", "SEE", "THE", "D", "G", "F", "H", "U.S", "AM", "PM", "A.M", "P.M"}


def norm(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\bst\.?\s", "saint ", s)
    s = s.replace("s.s.", "ss ").replace("u.s.s.", "uss ")
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def main():
    places = json.load(open(ROOT / "data/places.json"))
    names = defaultdict(list)
    for p in places:
        for n in [p["name"]] + [a["name"] for a in p.get("aliases") or []]:
            k = norm(n)
            if len(k) >= 3 and p["id"] not in names[k]:
                names[k].append(p["id"])
    by_id = {p["id"]: p for p in places}
    for k in names:   # most-visited first when a name is shared (Cambridge MA before Cambridge, England)
        names[k].sort(key=lambda i: -by_id[i].get("days_present", 0))

    def resolve(text):
        t = norm(text)
        t = re.sub(r"\b(north dakota|new york|massachusetts|d c|dc|washington d c)$", lambda m: m.group(0), t)
        words = t.split()
        for n in range(len(words), 0, -1):   # longest leading phrase that names a place
            k = " ".join(words[:n])
            if k in names:
                return names[k][0]
        # a heading that is the start of a place's name ("MALTESE CROSS" -> Maltese Cross Ranch)
        if len(t) >= 5:
            longer = [i for k, ids in names.items() if k.startswith(t + " ") for i in ids]
            if longer:
                return sorted(set(longer), key=lambda i: -by_id[i].get("days_present", 0))[0]
        return None

    out = {}
    for r in json.load(open(ROOT / "private/tra_chronology.json"))["records"]:
        if not r["entry"]:
            continue
        text = " ".join(r["entry"])[:600]
        ids, raw = [], []
        # an entry that is only a heading ("SAGAMORE HILL", "SAGAMORE HILL -")
        bare = re.fullmatch(r"\s*((?:S\.S\.\s|U\.S\.S\.\s)?[A-Z][A-Z'’.&/,\- ]{2,48}?)\s*[-–—:]?\s*(?:Letters:.*)?", text)
        if bare and resolve(bare.group(1)):
            out[r["date"]] = {"ids": [resolve(bare.group(1))], "raw": [bare.group(1).strip()]}
            continue
        # "KENTUCKY - SAGAMORE HILL The Roosevelts..." : a second caps heading with no dash after it
        st = re.match(r"\s*([A-Z][A-Z'’.&/, ]{2,48}?[A-Z.])\s*[-–—:]\s*((?:S\.S\.\s|U\.S\.S\.\s)?[A-Z][A-Z'’.&/ ]{2,48}?[A-Z.])\s+[A-Z][a-z]", text)
        if st and resolve(st.group(2)) and resolve(st.group(1)):
            a, b = resolve(st.group(2)), resolve(st.group(1))
            out[r["date"]] = {"ids": [a] + ([b] if b != a else []), "raw": [st.group(2), st.group(1)]}
            continue
        prev_end = None
        for m in HEAD.finditer(text + " - "):
            h = m.group(1).strip(" ,.")
            if h.replace(".", "") in NOISE or len(h) < 3 or h.isdigit():
                continue
            pid = resolve(h)
            if pid and pid not in ids:
                # stacked headings with nothing between them ("KENTUCKY - SAGAMORE HILL"): the last one
                # is where the day's text happens, so it goes first
                if prev_end is not None and not text[prev_end:m.start(1)].strip(" -–—:"):
                    ids.insert(0, pid)
                    raw.insert(0, h)
                else:
                    ids.append(pid)
                    raw.append(h)
                prev_end = m.end()
            if len(ids) >= 3:
                break
        if ids:
            out[r["date"]] = {"ids": ids, "raw": raw}
    json.dump(out, open(ROOT / "data/day_headers.json", "w"), indent=0)
    print(f"days with a resolved heading: {len(out)}")


if __name__ == "__main__":
    main()
