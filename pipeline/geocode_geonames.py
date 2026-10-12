"""Offline geocoding of cities and towns against GeoNames (cities500), before Nominatim.

Usage: python pipeline/geocode_geonames.py <dir with cities500.txt, admin1CodesASCII.txt, countryInfo.txt>
Writes hits into data/geocode_cache.json under the place's geocode query, tagged source "geonames",
so pipeline/geocode.py skips them. GeoNames data CC BY 4.0 (geonames.org).
"""
import json
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CACHE = ROOT / "data/geocode_cache.json"
US_ALIASES = {"usa": "US", "u.s.a.": "US", "united states": "US", "us": "US", "united states of america": "US"}
COUNTRY_FIX = {"england": "GB", "scotland": "GB", "wales": "GB", "united kingdom": "GB", "uk": "GB",
               "holland": "NL", "the netherlands": "NL", "czech republic": "CZ", "czechia": "CZ",
               "south korea": "KR", "russia": "RU", "turkey": "TR", "türkiye": "TR"}
STATE_ABBR = {"AL": "Alabama", "AK": "Alaska", "AZ": "Arizona", "AR": "Arkansas", "CA": "California", "CO": "Colorado",
              "CT": "Connecticut", "DE": "Delaware", "FL": "Florida", "GA": "Georgia", "HI": "Hawaii", "ID": "Idaho",
              "IL": "Illinois", "IN": "Indiana", "IA": "Iowa", "KS": "Kansas", "KY": "Kentucky", "LA": "Louisiana",
              "ME": "Maine", "MD": "Maryland", "MA": "Massachusetts", "MI": "Michigan", "MN": "Minnesota",
              "MS": "Mississippi", "MO": "Missouri", "MT": "Montana", "NE": "Nebraska", "NV": "Nevada",
              "NH": "New Hampshire", "NJ": "New Jersey", "NM": "New Mexico", "NY": "New York", "NC": "North Carolina",
              "ND": "North Dakota", "OH": "Ohio", "OK": "Oklahoma", "OR": "Oregon", "PA": "Pennsylvania",
              "RI": "Rhode Island", "SC": "South Carolina", "SD": "South Dakota", "TN": "Tennessee", "TX": "Texas",
              "UT": "Utah", "VT": "Vermont", "VA": "Virginia", "WA": "Washington", "WV": "West Virginia",
              "WI": "Wisconsin", "WY": "Wyoming", "DC": "District of Columbia"}


def key(s):
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    s = re.sub(r"\bst\.?\s", "saint ", s)
    s = re.sub(r"\bft\.?\s", "fort ", s)
    s = re.sub(r"\bmt\.?\s", "mount ", s)
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def main(src):
    src = Path(src)
    countries = {}
    for line in open(src / "countryInfo.txt", encoding="utf-8"):
        if line.startswith("#"):
            continue
        f = line.rstrip("\n").split("\t")
        countries[key(f[4])] = f[0]
    countries.update({key(k): v for k, v in {**US_ALIASES, **COUNTRY_FIX}.items()})
    admin1 = {}
    for line in open(src / "admin1CodesASCII.txt", encoding="utf-8"):
        code, name, ascii_, _ = line.rstrip("\n").split("\t")
        cc, a1 = code.split(".")
        admin1[(cc, key(name))] = a1
        admin1[(cc, key(ascii_))] = a1
    for ab, name in STATE_ABBR.items():
        if ("US", key(name)) in admin1:
            admin1[("US", key(ab))] = admin1[("US", key(name))]
    names = defaultdict(list)
    for line in open(src / "cities500.txt", encoding="utf-8"):
        f = line.rstrip("\n").split("\t")
        row = (float(f[4]), float(f[5]), f[8], f[10], int(f[14] or 0), f[0], f[1])
        names[key(f[1])].append(row)
        names[key(f[2])].append(row)
        for alt in f[3].split(",")[:40]:
            if alt:
                names[key(alt)].append(row)

    cache = json.load(open(CACHE)) if CACHE.exists() else {}
    places = json.load(open(ROOT / "data/places.json"))
    hits = misses = 0
    for p in places:
        q = p.get("geocode")
        if not q or cache.get(q) or p["kind"] not in ("city", "town", "camp", "other"):
            continue
        parts = [x.strip() for x in q.split(",") if x.strip()]
        cc = countries.get(key(parts[-1])) if len(parts) > 1 else None
        if not cc and p.get("country"):
            cc = countries.get(key(p["country"]))
        a1 = None
        for part in parts[1:]:
            a1 = admin1.get((cc, key(part))) or a1
        if not a1 and p.get("region"):
            a1 = admin1.get((cc, key(p["region"])))
        cands = {r[5]: r for r in names.get(key(parts[0]), []) + names.get(key(p["name"]), [])}.values()
        cands = [r for r in cands if not cc or r[2] == cc]
        if a1:
            cands = [r for r in cands if r[3] == a1] or ([] if cc == "US" else cands)
        if not cands:
            misses += 1
            continue
        best = max(cands, key=lambda r: r[4])
        cache[q] = {"lat": round(best[0], 5), "lon": round(best[1], 5), "osm_type": None, "osm_id": None,
                    "display_name": f"{best[6]} ({best[2]}{'/' + best[3] if best[3] else ''})", "source": "geonames",
                    "geonames_id": int(best[5]), "ambiguous": len(cands) > 1 and not a1}
        hits += 1
    json.dump(cache, open(CACHE, "w"), indent=0, ensure_ascii=False)
    print(f"geonames hits {hits}, misses {misses}; cache size {len(cache)}")


if __name__ == "__main__":
    main(sys.argv[1])
