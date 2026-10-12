"""Merge curated registry slices into data/people.json and data/places.json.

Inputs : work/curate/people_part*.out.json, work/curate/places_part*.out.json
Outputs: data/people.json, data/places.json (coordinates filled later by geocode.py)
Entities with the same id across slices are merged (aliases unioned).
"""
import glob
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def merge(pattern, key_fields):
    out = {}
    for f in sorted(glob.glob(str(ROOT / pattern))):
        for e in json.load(open(f)):
            cur = out.get(e["id"])
            if cur is None:
                out[e["id"]] = e
                continue
            for k in key_fields:
                vals = cur.get(k) or []
                for v in e.get(k) or []:
                    if v not in vals:
                        vals.append(v)
                cur[k] = vals
            for k, v in e.items():
                if cur.get(k) in (None, "") and v not in (None, ""):
                    cur[k] = v
            cur["uncertain"] = bool(cur.get("uncertain")) or bool(e.get("uncertain"))
    return out


def main():
    people = merge("work/curate/people_part*.out.json", ["aliases"])
    seed = {p["id"]: p for p in json.load(open(ROOT / "data/people_seed.json"))["people"]}
    for pid, s in seed.items():
        p = people.setdefault(pid, {"id": pid, "name": s["name"], "aliases": [], "description": None,
                                    "group": s["group"], "uncertain": False})
        p["name"] = s["name"]
        p["relation"] = s.get("relation")
        if s["group"] in ("family", "friend", "badlands", "expedition"):
            p["group"] = s["group"]
    places = merge("work/curate/places_part*.out.json", ["aliases", "index_ids"])
    ids = set(places)
    def resolve(pid):
        if pid in ids:
            return pid
        for cand in (pid.replace("new-york-city-ny", "new-york-ny"), pid.rsplit("-", 1)[0]):
            if cand in ids:
                return cand
        pre = [i for i in ids if i.startswith(pid + "-") or pid.startswith(i + "-")]
        return pre[0] if len(pre) == 1 else pid
    for p in places.values():
        if p.get("parent"):
            p["parent"] = resolve(p["parent"])
    missing_parents = sorted({p["parent"] for p in places.values() if p.get("parent") and p["parent"] not in places})
    for pid in missing_parents:
        print("parent id not found, cleared:", pid)
    for p in places.values():
        if p.get("parent") in missing_parents:
            p["parent"] = None
    json.dump(sorted(people.values(), key=lambda x: x["id"]), open(ROOT / "data/people.json", "w"), indent=1, ensure_ascii=False)
    json.dump(sorted(places.values(), key=lambda x: x["id"]), open(ROOT / "data/places.json", "w"), indent=1, ensure_ascii=False)
    print(f"people {len(people)}  places {len(places)}")


if __name__ == "__main__":
    main()
