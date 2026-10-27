"""Build the static JSON API into site/api/v1 (served by GitHub Pages).

Endpoints (all GET, all JSON, CORS-open on GitHub Pages):
  /api/v1/index.json                      dataset metadata, counts, endpoint list
  /api/v1/days/{YYYY-MM-DD}.json          one full day record
  /api/v1/months/{YYYY-MM}.json           compact records for a month
  /api/v1/years/{YYYY}.json               compact records for a year
  /api/v1/on-this-day/{MM-DD}.json        that calendar date across TR's life, best first
  /api/v1/people/index.json               all people (compact)
  /api/v1/people/{id}.json                one person + every day they appear
  /api/v1/places/index.json               all places (compact, with coordinates)
  /api/v1/places/{id}.json                one place + every day TR was there
  /api/v1/periods.json                    life periods with day counts
  /api/v1/tags/{tag}.json                 dates carrying a tag
  /api/v1/stays.json                      consecutive days at one place, for maps and timelines
  /api/v1/grid.json                       one compact row per day for the life-in-days grid
  /api/v1/search.json                     headline + summary per day, for client-side search
  /api/v1/highlights.json                 days with significance >= 4
Bulk downloads are copied to /data/.
"""
import json
import shutil
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "site/api/v1"
BASE_URL = "https://daybyday.labs.trlibrary.com"


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(obj, f, ensure_ascii=False, separators=(",", ":"))


def compact(r):
    loc = r["location"] or {}
    return {"date": r["date"], "age": r["age"], "headline": r["headline"], "summary": r["summary"],
            "significance": r["significance"], "location": loc.get("name"), "location_id": loc.get("id"),
            "lat": loc.get("lat"), "lon": loc.get("lon"), "tags": r["tags"],
            "people": [p["id"] for p in r["people"]][:12]}


GROUPS = [
    ("new-york-city", "New York City"), ("oyster-bay", "Oyster Bay and Sagamore Hill"), ("washington", "Washington, D.C."),
    ("albany", "Albany"), ("cambridge", "Cambridge and Harvard"), ("badlands", "Dakota Badlands"),
    ("us-other", "Elsewhere in North America"), ("europe", "Europe and the Middle East"), ("africa", "Africa"),
    ("latin-america", "Latin America and the Caribbean"), ("at-sea", "At sea"),
]
GROUP_OF_PLACE = {"new-york-ny": "new-york-city", "oyster-bay-ny": "oyster-bay", "washington-dc": "washington",
                  "albany-ny": "albany", "cambridge-ma": "cambridge", "medora-nd": "badlands"}
AFRICA = {"Kenya", "Uganda", "Sudan", "Egypt", "South Sudan", "Democratic Republic of the Congo", "Tanzania", "Ethiopia"}
LATAM = {"Cuba", "Panama", "Puerto Rico", "Brazil", "Argentina", "Chile", "Paraguay", "Uruguay", "Mexico", "Jamaica",
         "Haiti", "Colombia", "Venezuela", "Peru", "Bolivia", "Trinidad and Tobago", "Barbados", "Martinique"}
NORTH_AMERICA = {"United States", "Canada"}


def build_time_and_place(days, place_by_id, periods):
    def up(pid):
        n = 0
        while place_by_id.get(pid, {}).get("parent") and n < 5:
            pid = place_by_id[pid]["parent"]
            n += 1
        return pid

    def group(pid):
        top = up(pid)
        if top in GROUP_OF_PLACE:
            return GROUP_OF_PLACE[top]
        p = place_by_id.get(top, {})
        if p.get("kind") == "ship" or "crossing" in top or not p.get("country"):
            return "at-sea" if p.get("kind") in ("ship", "body_of_water", "other") else "us-other"
        c = p["country"]
        if c in NORTH_AMERICA:
            return "us-other"
        if c in AFRICA:
            return "africa"
        if c in LATAM:
            return "latin-america"
        return "europe"

    years = defaultdict(lambda: defaultdict(int))
    top_by_year = defaultdict(lambda: defaultdict(int))
    per_day = []
    for r in days:
        loc = (r["location"] or {}).get("id")
        if not loc:
            continue
        g = group(loc)
        y = int(r["date"][:4])
        years[y][g] += 1
        top_by_year[y][up(loc)] += 1
        per_day.append((r["date"], up(loc), g))
    year_rows = []
    for y in sorted(years):
        tops = sorted(top_by_year[y].items(), key=lambda x: -x[1])[:60]
        year_rows.append({"year": y, "counts": dict(years[y]), "distinct_places": len(top_by_year[y]),
                          "places": [{"id": k, "name": place_by_id.get(k, {}).get("name", k), "days": v,
                                      "lat": place_by_id.get(k, {}).get("lat"), "lon": place_by_id.get(k, {}).get("lon"),
                                      "group": group(k)} for k, v in tops]})
    dump(OUT / "time-and-place/years.json", {"groups": [{"id": a, "label": b} for a, b in GROUPS], "years": year_rows})

    out = []
    for per in periods["periods"]:
        counts, gcounts = defaultdict(int), defaultdict(int)
        for d, top, g in per_day:
            if per["start"] <= d <= per["end"]:
                counts[top] += 1
                gcounts[g] += 1
        total = sum(counts.values())
        places = []
        for k, v in sorted(counts.items(), key=lambda x: -x[1])[:60]:
            p = place_by_id.get(k, {})
            places.append({"id": k, "name": p.get("name", k), "days": v, "lat": p.get("lat"), "lon": p.get("lon"),
                           "kind": p.get("kind"), "group": group(k)})
        out.append({**{k: per[k] for k in ("id", "facet", "label", "start", "end")}, "days": total,
                    "groups": dict(gcounts), "distinct_places": len(counts), "places": places})
    dump(OUT / "time-and-place/periods.json", {"groups": [{"id": a, "label": b} for a, b in GROUPS], "periods": out})


BROAD_KINDS = {"state", "country", "region", "continent", "territory", "province", "body_of_water"}


def visit_stats(entries):
    """Days the record puts T.R. at a place (entries marked here), as opposed to days it is only named."""
    ds = sorted(e["date"] for e in entries if e.get("here"))
    return {"visit_days": len(ds), "visit_first": ds[0] if ds else None, "visit_last": ds[-1] if ds else None,
            "mention_days": sum(1 for e in entries if not e.get("here"))}


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    days = [json.loads(l) for l in open(ROOT / "data/days.jsonl")]
    people = json.load(open(ROOT / "data/people.json"))
    places = json.load(open(ROOT / "data/places.json"))
    periods = json.load(open(ROOT / "data/periods.json"))
    person_by_id = {p["id"]: p for p in people}
    place_by_id = {p["id"]: p for p in places}

    def person_ref(pid):
        p = person_by_id.get(pid)
        return {"id": pid, "name": p["name"] if p else pid}

    def place_ref(pid):
        p = place_by_id.get(pid)
        return {"id": pid, "name": p["name"] if p else pid, "lat": p.get("lat") if p else None,
                "lon": p.get("lon") if p else None}

    by_month, by_year, by_md = defaultdict(list), defaultdict(list), defaultdict(list)
    by_person, by_place, by_tag = defaultdict(list), defaultdict(list), defaultdict(list)
    for i, r in enumerate(days):
        full = dict(r)
        full["people"] = [{**person_ref(p["id"]), "role": p["role"]} for p in r["people"]]
        full["places"] = [place_ref(p) for p in r["places"]]
        full["letters"] = [{**l, "correspondent_name": person_by_id[l["correspondent"]]["name"]
                            if l.get("correspondent_resolved") and l["correspondent"] in person_by_id else l["correspondent"]}
                           for l in r["letters"]]
        full["prev"] = days[i - 1]["date"] if i else None
        full["next"] = days[i + 1]["date"] if i + 1 < len(days) else None
        full["url"] = f"{BASE_URL}/day.html?date={r['date']}"
        dump(OUT / f"days/{r['date']}.json", full)
        c = compact(r)
        by_month[r["date"][:7]].append(c)
        by_year[r["date"][:4]].append(c)
        if r["has_entry"]:
            by_md[r["date"][5:]].append(c)
        for p in r["people"]:
            by_person[p["id"]].append({"date": r["date"], "headline": r["headline"], "role": p["role"]})
        # "here": the record puts T.R. at this place that day (the day's location, unless only carried
        # forward, or a stop the place-names index gives for the date), not just a mention of it.
        loc = r.get("location") or {}
        here = set(loc.get("also") or []) | ({loc["id"]} if loc.get("id") and loc.get("source") != "carried" else set())
        # A place named that day also counts when it is at the same spot as, inside, or the parent of a place
        # he was (Camp Wood shares San Antonio's coordinates; Sagamore Hill sits inside Oyster Bay).
        for p in r["places"]:
            if p in here:
                continue
            pp = place_by_id.get(p, {})
            for h in list(here):
                hp = place_by_id.get(h, {})
                if pp.get("parent") == h or hp.get("parent") == p or (
                        pp.get("lat") is not None and hp.get("lat") is not None and pp.get("kind") not in BROAD_KINDS
                        and abs(pp["lat"] - hp["lat"]) < 0.02 and abs(pp["lon"] - hp["lon"]) < 0.02):
                    here.add(p)
                    break
        # "probable": he is only carried forward from the last place heading in the record
        prob = {loc["id"]} if loc.get("id") and loc.get("source", "").startswith("heading-carried") else set()
        for p in r["places"]:
            by_place[p].append({"date": r["date"], "headline": r["headline"], "here": p in here,
                                **({"probable": True} if p in prob else {})})
        for p in here - set(r["places"]):
            by_place[p].append({"date": r["date"], "headline": r["headline"], "here": True,
                                **({"probable": True} if p in prob else {})})
        for t in r["tags"]:
            by_tag[t].append(r["date"])
    for k, v in by_month.items():
        dump(OUT / f"months/{k}.json", v)
    for k, v in by_year.items():
        dump(OUT / f"years/{k}.json", v)
    for k, v in by_md.items():
        v.sort(key=lambda x: (-x["significance"], x["date"]))
        dump(OUT / f"on-this-day/{k}.json", {"month_day": k, "count": len(v), "days": v})
    dump(OUT / "people/index.json", [
        {"id": p["id"], "name": p["name"], "group": p.get("group"), "description": p.get("description"),
         "mentions": p.get("mentions", 0), "first": p.get("first"), "last": p.get("last")}
        for p in sorted(people, key=lambda x: -x.get("mentions", 0))])
    for p in people:
        dump(OUT / f"people/{p['id']}.json", {
            **{k: v for k, v in p.items() if k not in ("top_places", "top_companions")},
            "top_places": [place_ref(x) for x in p.get("top_places", [])],
            "top_companions": [person_ref(x) for x in p.get("top_companions", [])],
            "days": by_person.get(p["id"], [])})
    dump(OUT / "places/index.json", [
        {"id": p["id"], "name": p["name"], "kind": p["kind"], "region": p.get("region"), "country": p.get("country"),
         "lat": p.get("lat"), "lon": p.get("lon"), "days_present": p.get("days_present", 0),
         "first": p.get("first"), "last": p.get("last"), "parent": p.get("parent"),
         **visit_stats(by_place.get(p["id"], []))}
        for p in sorted(places, key=lambda x: -x.get("days_present", 0))])
    for p in places:
        dump(OUT / f"places/{p['id']}.json", {**p, **visit_stats(by_place.get(p["id"], [])),
                                              "days": sorted(by_place.get(p["id"], []), key=lambda x: x["date"])})
    pcount = defaultdict(int)
    for r in days:
        for pid in r["periods"]:
            pcount[pid] += 1
    dump(OUT / "periods.json", {"facets": periods["facets"],
                                "periods": [{**p, "days": pcount[p["id"]]} for p in periods["periods"]]})
    for t, v in by_tag.items():
        dump(OUT / f"tags/{t}.json", {"tag": t, "count": len(v), "dates": v})
    dump(OUT / "tags/index.json", sorted(({"tag": t, "count": len(v)} for t, v in by_tag.items()), key=lambda x: -x["count"]))

    stays, cur = [], None
    for r in days:
        loc = (r["location"] or {}).get("id")
        if cur and cur["place"] == loc:
            cur["end"] = r["date"]
            cur["days"] += 1
        else:
            cur = {"place": loc, "start": r["date"], "end": r["date"], "days": 1}
            stays.append(cur)
    for s in stays:
        p = place_by_id.get(s["place"]) or {}
        s.update({"name": p.get("name"), "lat": p.get("lat"), "lon": p.get("lon"), "kind": p.get("kind"),
                  "precise": p.get("coord_precision") == "exact"})
    dump(OUT / "stays.json", stays)
    # grid: [date, significance(-1 = no entry), location_id, headline]
    dump(OUT / "grid.json", {"fields": ["date", "significance", "location_id", "headline", "tags"],
                             "rows": [[r["date"], r["significance"] if r["has_entry"] else -1,
                                       (r["location"] or {}).get("id"), r["headline"], r["tags"]] for r in days]})
    dump(OUT / "search.json", [[r["date"], r["headline"], r["summary"],
                                [p["id"] for p in r["people"]], (r["location"] or {}).get("name")]
                               for r in days if r["has_entry"]])
    dump(OUT / "highlights.json", [compact(r) for r in days if r["significance"] >= 4])

    build_time_and_place(days, place_by_id, periods)

    meta = {
        "title": "Theodore Roosevelt Day by Day",
        "publisher": "Theodore Roosevelt Presidential Library",
        "url": BASE_URL,
        "version": "1.0",
        "coverage": {"start": days[0]["date"], "end": days[-1]["date"]},
        "counts": {"days": len(days), "days_with_entry": sum(r["has_entry"] for r in days),
                   "people": len(people), "places": len(places),
                   "letters": sum(len(r["letters"]) for r in days),
                   "letters_linked_to_trc": sum(1 for r in days for l in r["letters"] if l.get("trc")),
                   "days_with_archive_items": sum(1 for r in days if r.get("archive")), "tr_quotes": sum(len(r["tr_quotes"]) for r in days)},
        "source": "Facts are drawn from the Theodore Roosevelt Association's Chronological Record (TRC-CR-1, "
                  "compiled by Robert J. Moore Jr., 1985), cited by page on every day. All summaries and "
                  "descriptions are original writing by the Theodore Roosevelt Presidential Library.",
        "quotes_note": "tr_quotes are Theodore Roosevelt's own words as transcribed in the source record. "
                       "They are marked verified:false until checked against the original document. Each carries a source: "
                       "the record page it was transcribed from (cited_in) and, where it can be tied to one, the original "
                       "(original): the diary page at the Library of Congress for 1878-1884 diary entries, or the letter at "
                       "the Theodore Roosevelt Center when T.R. wrote only one recorded letter that day.",
        "archive": "Archive links point to the Theodore Roosevelt Center Digital Library at Dickinson State University "
                   "(theodorerooseveltcenter.org). Items are matched by date; letters by date plus correspondent name.",
        "geodata": "Coordinates from OpenStreetMap Nominatim (© OpenStreetMap contributors, ODbL).",
        "license": "Data: CC BY 4.0, Theodore Roosevelt Presidential Library. Code: MIT.",
        "endpoints": {
            "day": "/api/v1/days/{YYYY-MM-DD}.json", "month": "/api/v1/months/{YYYY-MM}.json",
            "year": "/api/v1/years/{YYYY}.json", "on_this_day": "/api/v1/on-this-day/{MM-DD}.json",
            "people": "/api/v1/people/index.json", "person": "/api/v1/people/{id}.json",
            "places": "/api/v1/places/index.json", "place": "/api/v1/places/{id}.json",
            "periods": "/api/v1/periods.json", "tags": "/api/v1/tags/index.json", "tag": "/api/v1/tags/{tag}.json",
            "stays": "/api/v1/stays.json", "grid": "/api/v1/grid.json", "search": "/api/v1/search.json",
            "highlights": "/api/v1/highlights.json"},
        "downloads": ["/data/days.jsonl", "/data/days.csv", "/data/people.json", "/data/places.json",
                      "/data/periods.json", "/data/letters.jsonl", "/data/quotes.jsonl", "/data/events.jsonl"],
    }
    dump(OUT / "index.json", meta)
    dl = ROOT / "site/data"
    dl.mkdir(parents=True, exist_ok=True)
    for f in ["days.jsonl", "days.csv", "people.json", "places.json", "periods.json", "letters.jsonl",
              "quotes.jsonl", "events.jsonl"]:
        shutil.copy(ROOT / "data" / f, dl / f)
    n = sum(1 for _ in OUT.rglob("*.json"))
    print(f"API built: {n} files")


if __name__ == "__main__":
    main()
