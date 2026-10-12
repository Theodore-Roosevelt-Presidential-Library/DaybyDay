"""Apply editorial corrections to data/enrich and log them.

data/corrections.json:
  "moves":  [{"from": "1901-10-10", "to": "1901-10-23", "shift_days": 7, "reason": "..."}]
            Every record dated in [from, to] moves by shift_days. If the target date already holds a
            record that is not itself moving, the two are merged (moved record keeps its headline and
            summary; events, people, places, letters, quotes and tags are combined).
  "splits": [{"from": "...", "to": "...", "match": ["substring of event detail", ...], "reason": "..."}]
            Applied after moves. Events whose detail matches move to the target day (created if empty),
            with the people, places and letters that appear only in those events.
  "fixes":  [{"date": "...", "uncertain": "...", "headline": "...", "summary": "..."}]
            Applied after moves and splits, to the record's final date. Only the fields given are changed.
Applied corrections are recorded in data/corrections_applied.json; running again is a no-op.
"""
import datetime as dt
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LIST_FIELDS = ["events", "people", "places", "letters", "tr_quotes", "works", "references", "guests", "tags"]


def main():
    spec = json.load(open(ROOT / "data/corrections.json"))
    done_path = ROOT / "data/corrections_applied.json"
    done = json.load(open(done_path)) if done_path.exists() else {"moves": [], "fixes": []}
    files = sorted(glob.glob(str(ROOT / "data/enrich/*.jsonl")))
    recs, where = {}, {}
    for f in files:
        for line in open(f):
            if line.strip():
                r = json.loads(line)
                recs[r["date"]] = r
                where[r["date"]] = f
    for m in spec.get("moves", []):
        key = f"{m['from']}..{m['to']}{m['shift_days']:+d}"
        if key in done["moves"]:
            continue
        a, b = dt.date.fromisoformat(m["from"]), dt.date.fromisoformat(m["to"])
        moving = sorted(d for d in recs if a <= dt.date.fromisoformat(d) <= b)
        moved = {}
        for d in moving:
            r = recs.pop(d)
            f = where.pop(d)
            nd = (dt.date.fromisoformat(d) + dt.timedelta(days=m["shift_days"])).isoformat()
            r["date"] = nd
            r["moved_from"] = d
            note = f"The record places this on {dt.date.fromisoformat(d):%B %-d, %Y}; {m['reason']}"
            r["uncertain"] = f"{r['uncertain']} {note}" if r.get("uncertain") else note
            moved[nd] = (r, f)
        for nd, (r, f) in moved.items():
            if nd in recs:   # merge with a record that stayed put
                old = recs[nd]
                for k in LIST_FIELDS:
                    r[k] = (r.get(k) or []) + [x for x in (old.get(k) or []) if x not in (r.get(k) or [])]
                r["merged_with"] = [nd]
                r["significance"] = max(r.get("significance") or 1, old.get("significance") or 1)
            recs[nd] = r
            where[nd] = where.get(nd, f)
        done["moves"].append(key)
        print(f"moved {len(moving)} records {m['from']}..{m['to']} by {m['shift_days']:+d} days")
    for sp in spec.get("splits", []):
        key = f"split:{sp['from']}>{sp['to']}:{'|'.join(sp['match'])}"
        if key in done.setdefault("splits", []):
            continue
        src = recs.get(sp["from"])
        if not src:
            print("split source missing:", sp["from"])
            continue
        hit = lambda e: any(m.lower() in (e.get("detail") or "").lower() for m in sp["match"])
        go = [e for e in src.get("events") or [] if hit(e)]
        stay = [e for e in src.get("events") or [] if not hit(e)]
        names = lambda evs, k: {x for e in evs for x in (e.get(k) or [])}
        go_people = names(go, "people") - names(stay, "people")
        go_places = names(go, "places") - names(stay, "places")
        tgt = recs.get(sp["to"])
        if not tgt:
            tgt = {"date": sp["to"], "headline": "", "summary": "", "events": [], "people": [], "places": [],
                   "letters": [], "tr_quotes": [], "works": [], "references": [], "guests": [], "film": False,
                   "tags": list(src.get("tags") or []), "significance": src.get("significance") or 1,
                   "uncertain": None, "moved_from": sp["from"], "split": True}
            recs[sp["to"]] = tgt
            where[sp["to"]] = where[sp["from"]]
        moved_people = [p for p in src.get("people") or [] if p["name"] in go_people]
        moved_places = [p for p in src.get("places") or [] if p["name"] in go_places or
                        (p["name"] in names(go, "places") and p not in tgt["places"])]
        moved_letters = [l for l in src.get("letters") or [] if l.get("correspondent") in go_people]
        src["events"] = stay
        src["people"] = [p for p in src.get("people") or [] if p["name"] not in go_people]
        src["places"] = [p for p in src.get("places") or [] if p["name"] not in go_places]
        src["letters"] = [l for l in src.get("letters") or [] if l not in moved_letters]
        tgt["events"] = (tgt.get("events") or []) + go
        for k, items in (("people", moved_people), ("places", moved_places), ("letters", moved_letters)):
            tgt[k] = (tgt.get(k) or []) + [x for x in items if x not in (tgt.get(k) or [])]
        note = f"Includes items the record places on {dt.date.fromisoformat(sp['from']):%B %-d}: {sp['reason']}"
        tgt["uncertain"] = f"{tgt['uncertain']} {note}" if tgt.get("uncertain") else note
        done["splits"].append(key)
        print(f"split {len(go)} events {sp['from']} -> {sp['to']}")
    for fx in spec.get("fixes", []):
        key = json.dumps(fx, sort_keys=True)
        if key in done["fixes"]:
            continue
        r = recs.get(fx["date"])
        if not r and fx.get("create"):   # fill an empty day; "create" names the source date it rests on
            r = {"date": fx["date"], "headline": "", "summary": "", "events": [], "people": [], "places": [],
                 "letters": [], "tr_quotes": [], "works": [], "references": [], "guests": [], "film": False,
                 "tags": [], "significance": 1, "uncertain": None, "moved_from": fx["create"], "split": True}
            recs[fx["date"]] = r
            where[fx["date"]] = next((where[d] for d in sorted(where) if d > fx["date"]), files[-1])
        if not r:
            print("fix target missing:", fx["date"])
            continue
        for k in ("headline", "summary", "uncertain", "significance", "tr_quotes", "events", "people", "places", "tags"):
            if fx.get(k) is not None:
                r[k] = fx[k]
        done["fixes"].append(key)
    by_file = {}
    for d, r in recs.items():
        by_file.setdefault(where[d], []).append(r)
    for f in files:
        rows = sorted(by_file.get(f, []), key=lambda x: x["date"])
        with open(f, "w") as fh:
            for r in rows:
                fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    json.dump(done, open(done_path, "w"), indent=1)
    print(f"fixes applied: {len(done['fixes'])}")


if __name__ == "__main__":
    main()
