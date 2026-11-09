"""Tours: Theodore Roosevelt's trips, tours and expeditions (data/tours.json), built into the API.

  /api/v1/tours/index.json      every tour, compact, with stats and a simplified route for thumbnails
  /api/v1/tours/{id}.json       one tour: summary, stats, the route stop by stop, highlights, every day

Route stops come only from days whose location the record states or the place-names index gives
(not days that merely carry forward the last known place), so the line on the map follows where he
is recorded as being. Places as broad as a country or state are left off the line. Distance is the straight-line sum between
stops: a floor, not miles traveled. States and countries come from every day with a stated place.
Days are counted inclusively (the day he set out and the day he got
home both count). States leave out home bases (Oyster Bay, New York City, Washington) and count a state
visited before its admission as a territory.
"""
import json
import math
from collections import Counter, defaultdict

FIRM = {"heading", "heading+refined", "index", "index+refined", "entry", "entry+refined",
        "arrival", "arrival+refined", "correction"}
US = "United States"
# Places too broad to put on a route line (a country's or state's center is not where he was).
BROAD = {"country", "state", "continent", "province", "territory"}
# Home bases: days at home don't add a state to a tour's count.
HOME = {"oyster-bay-ny", "sagamore-hill", "new-york-ny", "washington-dc"}
# Statehood dates for states admitted during or near T.R.'s lifetime. A visit before the date was
# to a territory, and is counted and labeled that way.
ADMITTED = {"Nebraska": "1867-03-01", "Colorado": "1876-08-01", "North Dakota": "1889-11-02",
            "South Dakota": "1889-11-02", "Montana": "1889-11-08", "Washington": "1889-11-11",
            "Idaho": "1890-07-03", "Wyoming": "1890-07-10", "Utah": "1896-01-04", "Oklahoma": "1907-11-16",
            "New Mexico": "1912-01-06", "Arizona": "1912-02-14", "Alaska": "1959-01-03", "Hawaii": "1959-08-21"}
NOT_STATES = {"District of Columbia", "Puerto Rico"}


def daterange(days, start, end):
    return [r for r in days if start <= r["date"] <= end]


def km(a, b):
    la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371 * 2 * math.asin(math.sqrt(h))


def simplify(pts, n=60):
    """Keep at most n points, evenly spaced, always keeping the first and last."""
    if len(pts) <= n:
        return pts
    step = (len(pts) - 1) / (n - 1)
    return [pts[round(i * step)] for i in range(n)]


def load(root):
    return json.load(open(root / "data/tours.json"))


def by_date(tours):
    """date -> [(tour, day_number, total_days)]"""
    from datetime import date, timedelta
    out = defaultdict(list)
    for t in tours["tours"]:
        d0, d1 = date.fromisoformat(t["start"]), date.fromisoformat(t["end"])
        n = (d1 - d0).days + 1
        for i in range(n):
            out[(d0 + timedelta(days=i)).isoformat()].append((t, i + 1, n))
    return out


def build(days, tours, place_by_id, person_by_id, dump, out_dir, base_url):
    def ancestors(pid):
        out, n = [pid], 0
        while place_by_id.get(pid, {}).get("parent") and n < 6:
            pid, n = place_by_id[pid]["parent"], n + 1
            out.append(pid)
        return out

    def region_country(pid):
        p, n = place_by_id.get(pid, {}), 0
        while p and not p.get("country") and p.get("parent") and n < 5:
            p, n = place_by_id.get(p["parent"], {}), n + 1
        return (p or {}).get("region"), (p or {}).get("country")

    index = []
    for t in tours["tours"]:
        span = daterange(days, t["start"], t["end"])
        # route: runs of consecutive firm days at one place with coordinates
        stops = []
        for r in span:
            loc = r.get("location") or {}
            pid = loc.get("id")
            p = place_by_id.get(pid or "", {})
            if not pid or loc.get("source") not in FIRM or p.get("lat") is None or p.get("kind") in BROAD:
                continue
            if stops and stops[-1]["id"] == pid:
                stops[-1]["end"] = r["date"]
                stops[-1]["days"] += 1
                continue
            stops.append({"id": pid, "name": p["name"], "kind": p.get("kind"), "lat": p["lat"], "lon": p["lon"],
                          "start": r["date"], "end": r["date"], "days": 1})
        dist = sum(km((a["lat"], a["lon"]), (b["lat"], b["lon"])) for a, b in zip(stops, stops[1:]))

        # States and countries come from every day whose place the record states (a state-level heading
        # such as "Indiana" counts here even though it is too broad for the route line).
        states, countries, territories = set(), set(), set()
        for r in span:
            loc = r.get("location") or {}
            pid = loc.get("id")
            if not pid or loc.get("source") not in FIRM:
                continue
            reg, c = region_country(pid)
            if c:
                countries.add(c)
            if c == US and reg and reg not in NOT_STATES and not HOME & set(ancestors(pid)):
                states.add(reg)
                if r["date"] < ADMITTED.get(reg, "0000"):
                    territories.add(reg)
        people = Counter()
        for r in span:
            for p in r["people"]:
                people[p["id"]] += 1
        letters = sum(len(r["letters"]) for r in span)
        speeches = sum(len(r.get("speeches") or []) for r in span)
        quotes = sum(len(r["tr_quotes"]) for r in span)
        entries = [r for r in span if r["has_entry"]]
        hi = sorted(entries, key=lambda r: (-r["significance"], r["date"]))[:8]
        hi.sort(key=lambda r: r["date"])
        stats = {"days": len(span), "days_with_entry": len(entries), "stops": len(stops),
                 "distinct_places": len({s["id"] for s in stops}), "states": sorted(states),
                 "territories": sorted(territories), "abroad": sorted(countries - {US}),
                 "countries": sorted(countries), "straight_line_km": round(dist), "letters": letters,
                 "speeches": speeches, "tr_quotes": quotes, "people": len(people)}
        url = f"{base_url}/tour.html?id={t['id']}"
        record = {**{k: v for k, v in t.items()}, "kind_label": tours["kinds"][t["kind"]], "url": url,
                  "stats": stats, "route": stops,
                  "highlights": [{"date": r["date"], "headline": r["headline"], "summary": r["summary"],
                                  "significance": r["significance"],
                                  "location": (r["location"] or {}).get("name")} for r in hi],
                  "people": [{"id": pid, "name": person_by_id.get(pid, {}).get("name", pid), "days": n}
                             for pid, n in people.most_common(24)],
                  "days": [{"date": r["date"], "n": i + 1, "has_entry": r["has_entry"], "headline": r["headline"],
                            "summary": r["summary"], "significance": r["significance"] if r["has_entry"] else -1,
                            "location": (r["location"] or {}).get("name"), "location_id": (r["location"] or {}).get("id"),
                            "lat": (r["location"] or {}).get("lat"), "lon": (r["location"] or {}).get("lon"),
                            "firm": (r["location"] or {}).get("source") in FIRM,
                            "broad": place_by_id.get((r["location"] or {}).get("id") or "", {}).get("kind") in BROAD,
                            "speeches": len(r.get("speeches") or []), "letters": len(r["letters"])}
                           for i, r in enumerate(span)]}
        dump(out_dir / f"tours/{t['id']}.json", record)
        lats = [s["lat"] for s in stops] or [0]
        lons = [s["lon"] for s in stops] or [0]
        index.append({**{k: t[k] for k in ("id", "title", "kind", "start", "end", "short")},
                      "kind_label": record["kind_label"], "url": url,
                      "stats": {k: stats[k] for k in ("days", "stops", "straight_line_km", "speeches")}
                      | {"states": len(states), "territories": len(territories), "countries": len(countries),
                         "abroad": sorted(countries - {US})},
                      "bbox": [min(lons), min(lats), max(lons), max(lats)],
                      "line": [[round(s["lon"], 3), round(s["lat"], 3)] for s in simplify(stops)]})
    dump(out_dir / "tours/index.json", {"kinds": tours["kinds"], "tours": index})
    return index
