"""Geocode data/places.json with OpenStreetMap Nominatim (1 request/second, cached).

Cache: data/geocode_cache.json  {query: {"lat", "lon", "osm_type", "osm_id", "display_name"} | null}
Places without a geocode query inherit their parent's coordinates (precision "parent").
Data © OpenStreetMap contributors, ODbL.
"""
import json
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data/geocode_cache.json"
UA = "TRPL-DaybyDay/1.0 (Theodore Roosevelt Presidential Library; https://daybyday.labs.trlibrary.com)"


def lookup(q):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": q, "format": "jsonv2", "limit": 1, "accept-language": "en"})
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        res = json.load(r)
    if not res:
        return None
    x = res[0]
    return {"lat": round(float(x["lat"]), 5), "lon": round(float(x["lon"]), 5),
            "osm_type": x.get("osm_type"), "osm_id": x.get("osm_id"), "display_name": x.get("display_name")}


def fallback_queries(q):
    """'Elkhorn Ranch Site, Billings County, North Dakota, USA' -> drop leading parts one by one."""
    parts = [p.strip() for p in q.split(",")]
    return [", ".join(parts[i:]) for i in range(1, len(parts) - 1)]


def main():
    cache = json.load(open(CACHE)) if CACHE.exists() else {}
    places = json.load(open(ROOT / "data/places.json"))
    todo = sorted({p["geocode"] for p in places if p.get("geocode")} - {k for k, v in cache.items() if v or k in cache})
    only = next((a.split("=", 1)[1] for a in sys.argv if a.startswith("--only=")), None)
    if only:
        todo = [q for q in json.load(open(only)) if q not in cache]
    print(f"{len(todo)} queries to run", flush=True)
    budget = float(next((a.split("=")[1] for a in sys.argv if a.startswith("--budget=")), "1e9"))
    t0 = time.time()
    for i, q in enumerate(todo, 1):
        if time.time() - t0 > budget:
            print(f"budget reached after {i - 1} queries", flush=True)
            break
        for attempt in range(3):
            try:
                cache[q] = lookup(q)
                break
            except Exception as e:
                print("retry", q, e, flush=True)
                time.sleep(5 * (attempt + 1))
        time.sleep(1.1)
        if i % 10 == 0:
            json.dump(cache, open(CACHE, "w"), indent=0, ensure_ascii=False)
    json.dump(cache, open(CACHE, "w"), indent=0, ensure_ascii=False)
    apply(places, cache)


def apply(places, cache):
    by_id = {p["id"]: p for p in places}
    for p in places:
        hit = cache.get(p.get("geocode") or "")
        p["lat"] = p["lon"] = None
        p["coord_source"] = None
        if hit:
            p["lat"], p["lon"], p["coord_source"] = hit["lat"], hit["lon"], hit.get("source", "nominatim")
            p["osm"] = f"{hit['osm_type']}/{hit['osm_id']}" if hit.get("osm_type") else None
    # precision: "exact" only when the match plausibly is the place itself
    import math, re as _re
    def dist_km(a, b):
        r = 6371
        la1, lo1, la2, lo2 = map(math.radians, (a[0], a[1], b[0], b[1]))
        h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
        return 2 * r * math.asin(math.sqrt(h))
    stop = {"the", "of", "and", "house", "hotel", "club", "street", "avenue", "new", "york", "city", "site", "historic"}
    for p in places:
        p["coord_precision"] = None
        if p["lat"] is None:
            continue
        hit = cache.get(p.get("geocode") or "") or {}
        if p["kind"] in ("city", "town", "state", "country", "region", "body_of_water", "mountain"):
            p["coord_precision"] = "exact" if p["coord_source"] in ("nominatim", "geonames") else "approximate"
            continue
        exact = False
        if p["coord_source"] == "nominatim":
            first = (hit.get("display_name") or "").split(",")[0].lower()
            words = {w for w in _re.findall(r"[a-z]+", p["name"].lower()) if len(w) > 3 and w not in stop}
            is_address = bool(_re.match(r"^\d", (p.get("geocode") or "").strip())) or first.strip().isdigit()
            exact = is_address or any(w in first for w in words)
            par = by_id.get(p.get("parent") or "")
            if exact and par and par.get("lat") is not None and dist_km((p["lat"], p["lon"]), (par["lat"], par["lon"])) > (80 if p["kind"] in ("ranch", "camp", "park", "battlefield") else 30):
                exact = False
        p["coord_precision"] = "exact" if exact else "approximate"
    for p in places:   # inherit from parent
        if p["lat"] is None and p.get("parent") in by_id and by_id[p["parent"]].get("lat") is not None:
            p["lat"], p["lon"], p["coord_source"] = by_id[p["parent"]]["lat"], by_id[p["parent"]]["lon"], "parent"
            p["coord_precision"] = "approximate"
    json.dump(places, open(ROOT / "data/places.json", "w"), indent=1, ensure_ascii=False)
    n = sum(1 for p in places if p["lat"] is not None)
    print(f"coordinates for {n}/{len(places)} places")


if __name__ == "__main__":
    if "--apply" in sys.argv:
        apply(json.load(open(ROOT / "data/places.json")), json.load(open(CACHE)))
    else:
        main()
