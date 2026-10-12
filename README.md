# Theodore Roosevelt Day by Day

Every day of Theodore Roosevelt's life — 21,986 of them, from his birth on October 27, 1858 to his death on January 6, 1919 — as a structured, open dataset with a static JSON API, an explorer site and embeddable widgets.

**Live:** https://daybyday.labs.trlibrary.com · **API:** https://daybyday.labs.trlibrary.com/api/v1/index.json

| | |
| --- | --- |
| Days | 21,986 (14,551 with an entry in the record) |
| People | 4,750 canonical people, every mention linked |
| Places | 2,827 canonical places, most with coordinates |
| Letters | 7,358 letters to and from TR, with correspondent and topic; 4,725 linked to the letter itself at the Theodore Roosevelt Center |
| Archive | 127,873 dated TRC Digital Library items attached to 8,296 days |
| TR's own words | 3,179 diary, letter and speech passages (unverified transcriptions) |
| Life periods | 30 periods across four facets: life stage, office, journey, campaign |

## What's in a day

```json
{
  "date": "1884-06-25", "weekday": "Wed", "age": 25, "has_entry": true,
  "headline": "Finding the Elkhorn site",
  "summary": "After a mallard for the pot, Roosevelt scouts the river north of Medora for a new ranch site…",
  "significance": 3,
  "location": {"id": "elkhorn-ranch", "name": "Elkhorn Ranch", "lat": …, "lon": …, "source": "heading+refined"},
  "places": ["elkhorn-ranch", "medora-nd", "little-missouri-river"],
  "people": [{"id": "…", "role": "companion"}],
  "events": [{"seq": 1, "action": "hunting", "detail": "…", "people": [], "places": []}, …],
  "letters": [{"direction": "from_tr", "correspondent": "henry-cabot-lodge", "topic": "…"}],
  "tr_quotes": [{"text": "One mallard drake, shot with rifle for pot.", "kind": "diary", "verified": false}],
  "tags": ["badlands", "ranching", "business"],
  "periods": ["badlands-years"],
  "sources": [{"work": "TRA Chronological Record (TRC-CR-1)", "pages": ["V1884 p…"]}]
}
```

Full field reference: [docs/schema.md](docs/schema.md).

## Repository layout

```
data/                 canonical dataset (committed; contains no TRA text)
  enrich/*.jsonl      rewritten day records, one file per chunk of months
  days.jsonl/.csv     assembled day records (built)
  people.json         people registry        places.json   places registry + coordinates
  periods.json        editorial life periods places_index.json  TRA place-names index (place → dates)
  people_seed.json    canonical names for recurring people
  geocode_cache.json  geocoder results (GeoNames + OpenStreetMap)
pipeline/             scripts that build everything (see below)
site/                 explorer pages, widgets, and the generated API (site/api is built, not committed)
docs/                 schema and methods
private/              the TRA OCR parse — research input only, never committed (gitignored)
```

## Rebuilding

```bash
python pipeline/build_dataset.py   # data/enrich + registries → data/days.jsonl, stats, flat tables
python pipeline/build_api.py       # data → site/api/v1 (GitHub Actions runs this on every push)
python -m http.server -d site 8000 # preview at http://localhost:8000
```

The full pipeline, from source scans to the committed data, is described in [docs/methods.md](docs/methods.md).

## Source and copyright

The facts come from the Theodore Roosevelt Association's *Chronological Record* (TRC-CR-1), compiled by Robert J. Moore Jr. (© 1985 Robert J. Moore Jr. and the Theodore Roosevelt Association), held in the Theodore Roosevelt Collection at Harvard. That text is copyrighted and is **not** reproduced here: every headline, summary, event description and letter topic was written fresh by the Theodore Roosevelt Presidential Library, and an automated check rejects any six-word run copied from the source outside a Roosevelt quotation. Each day cites the record's volume and page.

Roosevelt's own words (`tr_quotes`) are his and in the public domain, but they are given as transcribed in the record and flagged `verified: false`. Verify any quotation against the original document (trlibrary.com/gpt) before publication.

## License

Data: CC BY 4.0, Theodore Roosevelt Presidential Library. Code: MIT (see LICENSE). Geodata © OpenStreetMap contributors (ODbL) and GeoNames (CC BY 4.0).
