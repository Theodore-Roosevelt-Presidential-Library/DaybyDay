"""Assemble the canonical Day by Day dataset.

Inputs (all committed, none contain TRA text):
  data/enrich/*.jsonl      rewritten day records
  data/places_index.json   TRA place-names index (place -> date ranges)
  data/places.json         curated places (+ coordinates)
  data/people.json         curated people
  data/periods.json        editorial life periods
Outputs:
  data/days.jsonl          one record per calendar day of TR's life (1858-10-27 .. 1919-01-06)
  data/people.json         + stats (mentions, first/last, top places/companions)
  data/places.json         + stats (days present, first/last)
  data/letters.jsonl, data/quotes.jsonl, data/events.jsonl   flattened tables
  data/days.csv            flat table for spreadsheets
"""
import csv
import datetime as dt
import glob
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

from link_diaries import quote_key

ROOT = Path(__file__).resolve().parent.parent
BIRTH = dt.date(1858, 10, 27)
DEATH = dt.date(1919, 1, 6)
LOCAL_KINDS = {"city", "town", "residence", "ranch", "camp", "ship", "train", "building", "institution",
               "battlefield", "park", "mountain", "body_of_water", "region", "state", "country", "other"}
SPECIFIC = {"residence": 0, "ranch": 0, "camp": 1, "ship": 1, "train": 1, "building": 2, "institution": 2,
            "battlefield": 2, "park": 3, "mountain": 3, "body_of_water": 4, "town": 5, "city": 5,
            "region": 7, "state": 8, "country": 9, "other": 6}


def norm(s):
    return re.sub(r"\s+", " ", (s or "").strip().lower())


def age_on(d):
    a = d.year - BIRTH.year - ((d.month, d.day) < (BIRTH.month, BIRTH.day))
    return a


def daterange(a, b):
    d = a
    while d <= b:
        yield d
        d += dt.timedelta(days=1)


def main():
    places = json.load(open(ROOT / "data/places.json"))
    people = json.load(open(ROOT / "data/people.json"))
    periods = json.load(open(ROOT / "data/periods.json"))["periods"]
    pidx = json.load(open(ROOT / "data/places_index.json"))
    place_by_id = {p["id"]: p for p in places}
    person_by_id = {p["id"]: p for p in people}

    # alias maps
    place_alias = {}
    index_to_place = {}
    for p in places:
        for a in p.get("aliases") or []:
            place_alias[(norm(a["name"]), norm(a.get("region")))] = p["id"]
        place_alias.setdefault((norm(p["name"]), norm(p.get("region"))), p["id"])
        for i in p.get("index_ids") or []:
            index_to_place[i] = p["id"]
    person_alias = {}
    for p in people:
        person_alias[norm(p["name"])] = p["id"]
        for a in p.get("aliases") or []:
            person_alias.setdefault(norm(a), p["id"])

    def place_id(name, region):
        return place_alias.get((norm(name), norm(region))) or place_alias.get((norm(name), ""))

    def flat(v):
        out = []
        for x in v or []:
            if isinstance(x, list):
                out += flat(x)
            elif isinstance(x, dict):
                out.append(x.get("name") or "")
            elif x:
                out.append(str(x))
        return out

    def event_place(n, day_places):
        for pp in day_places:
            if norm(place_by_id[pp]["name"]) == norm(n):
                return pp
        return place_id(n, None)

    def person_id(name):
        if isinstance(name, dict):
            name = name.get("name") or ""
        return person_alias.get(norm(name))

    # where TR was, from the TRA place index
    # index entries the OCR ran together (lists of ships under one heading) are not used for location
    BUNDLED = {e["id"] for e in pidx if len(e["id"]) > 45}
    ovr_path = ROOT / "data/places_index_overrides.json"
    for fx in (json.load(open(ovr_path)).get("year_fixes", []) if ovr_path.exists() else []):
        for e in pidx:
            if e["id"] == fx["id"]:
                for v in e["visits"]:
                    for k in ("start", "end"):
                        if v[k].startswith(str(fx["from_year"])):
                            v[k] = str(fx["to_year"]) + v[k][4:]
    headers = json.load(open(ROOT / "data/day_headers.json")) if (ROOT / "data/day_headers.json").exists() else {}

    def chain(pid):
        out, n = [], 0
        while pid and n < 6:
            out.append(pid)
            pid = place_by_id.get(pid, {}).get("parent")
            n += 1
        return out

    def related(a, b):
        return a in chain(b) or b in chain(a)
    where = defaultdict(list)          # date -> [(place, precision, span_days)]
    skipped_visits = 0
    for e in pidx:
        pid = index_to_place.get(e["id"])
        if not pid or e["id"] in BUNDLED:
            continue
        for v in e["visits"]:
            a, b = dt.date.fromisoformat(v["start"]), dt.date.fromisoformat(v["end"])
            # skip a visit that every heading in its span contradicts (a misread date in the index)
            heads = [headers[x.isoformat()]["ids"] for x in daterange(a, b) if x.isoformat() in headers]
            if len(heads) >= 3 and not any(related(pid, h) for ids in heads for h in ids):
                skipped_visits += 1
                continue
            for d in daterange(a, b):
                if pid not in [x[0] for x in where[d]]:
                    where[d].append((pid, v.get("precision", "day"), (b - a).days + 1))
    for d in where:
        where[d].sort(key=lambda x: (x[1] != "day", x[2]))   # day precision, shortest stay first
    print(f"index visits contradicted by every heading in their span, skipped: {skipped_visits}")


    enrich = {}
    for f in sorted(glob.glob(str(ROOT / "data/enrich/*.jsonl"))):
        for line in open(f):
            if line.strip():
                r = json.loads(line)
                enrich[r["date"]] = r

    tra_pages = {}
    try:   # page citations only (no text) — available when the private parse is present
        for r in json.load(open(ROOT / "private/tra_chronology.json"))["records"]:
            tra_pages[r["date"]] = r["source"]
        json.dump(tra_pages, open(ROOT / "data/tra_pages.json", "w"))
    except FileNotFoundError:
        tra_pages = json.load(open(ROOT / "data/tra_pages.json"))

    trc_day, trc_letters = {}, {}
    if (ROOT / "data/trc_by_day.jsonl").exists():
        for line in open(ROOT / "data/trc_by_day.jsonl"):
            x = json.loads(line)
            trc_day[x["date"]] = x
        trc_letters = json.load(open(ROOT / "data/trc_letters.json"))
    TRC_URL = "https://www.theodorerooseveltcenter.org/digital-library/{}/"
    diary_links = json.load(open(ROOT / "data/diary_links.json")) if (ROOT / "data/diary_links.json").exists() else {}
    loc_fixes = {}
    for x in json.load(open(ROOT / "data/corrections.json")).get("locations", []):
        for d in daterange(dt.date.fromisoformat(x["date"]), dt.date.fromisoformat(x.get("to") or x["date"])):
            loc_fixes[d.isoformat()] = x["place"]
    speeches = json.load(open(ROOT / "data/speeches_by_day.json")) if (ROOT / "data/speeches_by_day.json").exists() else {}

    unresolved_people, unresolved_places = Counter(), Counter()
    days, last_loc, last_head = [], None, None
    stats_person = defaultdict(lambda: {"mentions": 0, "days": [], "places": Counter(), "with": Counter()})
    stats_place = defaultdict(list)
    letters_out, quotes_out, events_out = [], [], []

    for d in daterange(BIRTH, DEATH):
        ds = d.isoformat()
        r = enrich.get(ds)
        rec = {
            "date": ds, "weekday": d.strftime("%a"), "year": d.year, "month": d.month, "day": d.day,
            "age": age_on(d), "has_entry": r is not None,
            "headline": None, "summary": None, "significance": 0,
            "location": None, "places": [], "people": [], "events": [], "letters": [], "tr_quotes": [],
            "works": [], "references": [], "guests": [], "tags": [], "film": False,
            "periods": [p["id"] for p in periods if p["start"] <= ds <= p["end"]],
            "sources": [{"work": "TRA Chronological Record (TRC-CR-1)", "pages": tra_pages.get((r or {}).get("moved_from") or ds, [])}],
            "redated_from": (r or {}).get("moved_from"),
            "uncertain": None,
            "speeches": speeches.get(ds, []),
        }
        day_places = []
        if r:
            rec.update({k: r.get(k) for k in ("headline", "summary", "significance", "film", "uncertain")})
            rec["tags"] = r.get("tags") or []
            rec["works"] = r.get("works") or []
            rec["references"] = r.get("references") or []
            for p in r.get("places") or []:
                pid = place_id(p["name"], p.get("region"))
                if pid:
                    if pid not in day_places:
                        day_places.append(pid)
                else:
                    unresolved_places[(p["name"], p.get("region"))] += 1
            names = {}
            for p in r.get("people") or []:
                pid = person_id(p["name"])
                if not pid:
                    unresolved_people[p["name"]] += 1
                    continue
                if pid not in names:
                    names[pid] = p.get("role")
            rec["people"] = [{"id": k, "role": v} for k, v in names.items()]
            rec["guests"] = [person_id(g) or g for g in r.get("guests") or []]
            for i, e in enumerate(r.get("events") or []):
                ev = {"seq": i + 1, "action": e["action"], "detail": e.get("detail"), "time": e.get("time"),
                      "people": [x for x in (person_id(n) for n in flat(e.get("people"))) if x],
                      "places": [x for x in (event_place(n, day_places) for n in flat(e.get("places"))) if x]}
                rec["events"].append(ev)
                events_out.append({"date": ds, **ev})
            for l in r.get("letters") or []:
                lid = person_id(l.get("correspondent") or "")
                letter = {"direction": l["direction"], "correspondent": lid or l.get("correspondent"),
                          "correspondent_resolved": bool(lid), "topic": l.get("topic")}
                hit = trc_letters.get(f"{ds}|{l['direction']}|{letter['correspondent']}")
                if hit:
                    letter["trc"] = [TRC_URL.format(i) for i in hit["trc"]]
                rec["letters"].append(letter)
                letters_out.append({"date": ds, **letter})
            tr_letters = [l for l in rec["letters"] if l["direction"] == "from_tr"]
            for q in r.get("tr_quotes") or []:
                qq = {"text": q["text"], "kind": q["kind"], "verified": False,
                      "source": {"cited_in": {"work": "TRA Chronological Record", "pages": rec["sources"][0]["pages"]}}}
                dl = diary_links.get(quote_key(ds, q["text"])) if q["kind"] == "diary" else None
                if dl:
                    qq["source"]["original"] = {"type": "diary_page", "title": dl["loc_title"], "url": dl["loc"],
                                                "holder": "Library of Congress, Manuscript Division",
                                                "explorer": dl["explorer"], "match": dl["match"]}
                elif q["kind"] == "letter" and len(tr_letters) == 1 and tr_letters[0].get("trc"):
                    # Only one letter by T.R. is recorded that day, so the quote can be tied to it.
                    l = tr_letters[0]
                    qq["source"]["original"] = {"type": "letter", "url": l["trc"][0],
                                                "holder": "Theodore Roosevelt Center, Dickinson State University",
                                                "title": "Letter to " + (person_by_id[l["correspondent"]]["name"] if l["correspondent_resolved"] and l["correspondent"] in person_by_id else str(l["correspondent"]))}
                rec["tr_quotes"].append(qq)
                quotes_out.append({"date": ds, **qq})

        # location. 1) the day's own place heading in the record; 2) between headings, the last stated
        # place carries forward unless the place index records a short, specific visit elsewhere;
        # 3) with no heading at all, the place index (shortest day-precision stay first); 4) a place
        # named in the entry; 5) the last known place. A more specific place inside the chosen one
        # (Sagamore Hill inside Oyster Bay) refines it.
        idx = where.get(d, [])
        idx_places = [pid for pid, _, _ in idx]
        src_date = (r or {}).get("moved_from") or ds
        head = [] if (r or {}).get("split") else (headers.get(src_date) or {}).get("ids") or []
        loc, loc_source = None, None
        if head:
            loc, loc_source = head[0], "heading"
            last_head = (loc, d)
        elif last_head and (d - last_head[1]).days <= 45:
            short = [pid for pid, prec, span in idx if prec == "day" and span <= 14 and not related(pid, last_head[0])]
            if short:
                loc, loc_source = short[0], "index"
            else:
                loc, loc_source = last_head[0], "heading-carried"
                # an arrival somewhere new that day moves him, and later days carry it
                arr = [x for ev in rec["events"] if ev["action"] == "arrival" for x in ev["places"]
                       if place_by_id[x]["kind"] in LOCAL_KINDS and place_by_id[x].get("lat") is not None
                       and not related(x, last_head[0])]
                if arr:
                    loc, loc_source = arr[-1], "arrival"
                    last_head = (loc, d)
        elif idx:
            loc, loc_source = idx[0][0], "index"
        if loc is None and day_places:
            cands = [p for p in day_places if place_by_id[p]["kind"] in LOCAL_KINDS]
            if cands:
                loc, loc_source = sorted(cands, key=lambda x: SPECIFIC.get(place_by_id[x]["kind"], 6))[0], "entry"
        if loc is None and last_loc:
            loc, loc_source = last_loc, "carried"
        if ds in loc_fixes:   # a checked correction (data/corrections.json "locations") wins
            loc, loc_source = loc_fixes[ds], "correction"
            if loc not in day_places:
                day_places.append(loc)
        if loc and loc_source != "correction":   # refine to a more specific place inside it, named that day or in the index
            inner = [p for p in day_places + idx_places
                     if p != loc and loc in chain(p)[1:] and place_by_id[p]["kind"] in LOCAL_KINDS]
            if inner:
                loc = sorted(inner, key=lambda x: SPECIFIC.get(place_by_id[x]["kind"], 6))[0]
                loc_source = loc_source + "+refined"
        for pid in idx_places:
            if pid not in day_places:
                day_places.append(pid)
        rec["places"] = day_places
        if loc:
            p = place_by_id[loc]
            rec["location"] = {"id": loc, "name": p["name"], "lat": p.get("lat"), "lon": p.get("lon"),
                               "source": loc_source, "also": [x for x in idx_places if x != loc]}
            if loc_source != "carried":
                last_loc = loc
        t = trc_day.get(ds)
        rec["archive"] = ({"source": "Theodore Roosevelt Center, Dickinson State University", "count": t["count"],
                           "types": t["types"],
                           "items": [{"title": i["title"], "type": i["type"], "url": TRC_URL.format(i["id"])} for i in t["items"]]}
                          if t else None)
        days.append(rec)
        for pid in day_places:
            stats_place[pid].append(ds)
        for pp in rec["people"]:
            s = stats_person[pp["id"]]
            s["mentions"] += 1
            s["days"].append(ds)
            if loc:
                s["places"][loc] += 1
            for other in rec["people"]:
                if other["id"] != pp["id"]:
                    s["with"][other["id"]] += 1

    with open(ROOT / "data/days.jsonl", "w") as f:
        for rec in days:
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    for name, rows in (("letters", letters_out), ("quotes", quotes_out), ("events", events_out)):
        with open(ROOT / f"data/{name}.jsonl", "w") as f:
            for x in rows:
                f.write(json.dumps(x, ensure_ascii=False) + "\n")
    with open(ROOT / "data/days.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "weekday", "age", "has_entry", "significance", "headline", "summary", "location_id",
                    "location_name", "lat", "lon", "location_source", "people", "places", "tags", "periods",
                    "letters", "tr_quotes", "tra_pages"])
        for r in days:
            loc = r["location"] or {}
            w.writerow([r["date"], r["weekday"], r["age"], int(r["has_entry"]), r["significance"], r["headline"] or "",
                        r["summary"] or "", loc.get("id", ""), loc.get("name", ""), loc.get("lat", ""), loc.get("lon", ""),
                        loc.get("source", ""), ";".join(p["id"] for p in r["people"]), ";".join(r["places"]),
                        ";".join(r["tags"]), ";".join(r["periods"]), len(r["letters"]), len(r["tr_quotes"]),
                        ";".join(r["sources"][0]["pages"])])

    for p in people:
        s = stats_person.get(p["id"])
        p["mentions"] = s["mentions"] if s else 0
        p["first"] = s["days"][0] if s else None
        p["last"] = s["days"][-1] if s else None
        p["top_places"] = [k for k, _ in s["places"].most_common(5)] if s else []
        p["top_companions"] = [k for k, _ in s["with"].most_common(8)] if s else []
    for p in places:
        ds = stats_place.get(p["id"], [])
        p["days_present"] = len(ds)
        p["first"] = ds[0] if ds else None
        p["last"] = ds[-1] if ds else None
    json.dump(people, open(ROOT / "data/people.json", "w"), indent=1, ensure_ascii=False)
    json.dump(places, open(ROOT / "data/places.json", "w"), indent=1, ensure_ascii=False)

    n_loc = sum(1 for r in days if r["location"])
    print(f"days {len(days)}  with entry {sum(r['has_entry'] for r in days)}  with location {n_loc} "
          f"(carried {sum(1 for r in days if r['location'] and r['location']['source']=='carried')})")
    print("unresolved people mentions:", sum(unresolved_people.values()), unresolved_people.most_common(10))
    print("unresolved place mentions:", sum(unresolved_places.values()), unresolved_places.most_common(10))


if __name__ == "__main__":
    main()
