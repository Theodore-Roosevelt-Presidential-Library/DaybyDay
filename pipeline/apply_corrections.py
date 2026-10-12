"""Apply editorial corrections to data/enrich and log them.

data/corrections.json:
  "moves":  [{"from": "1901-10-10", "to": "1901-10-23", "shift_days": 7, "reason": "..."}]
            Every record dated in [from, to] moves by shift_days. If the target date already holds a
            record that is not itself moving, the two are merged (moved record keeps its headline and
            summary; events, people, places, letters, quotes and tags are combined).
  "fixes":  [{"date": "...", "uncertain": "...", "headline": "...", "summary": "..."}]
            Applied after moves, to the record's final date. Only the fields given are changed.
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
            note = f"Re-dated from {d}: {m['reason']}"
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
    for fx in spec.get("fixes", []):
        key = json.dumps(fx, sort_keys=True)
        if key in done["fixes"]:
            continue
        r = recs.get(fx["date"])
        if not r:
            print("fix target missing:", fx["date"])
            continue
        for k in ("headline", "summary", "uncertain", "significance", "tr_quotes"):
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
