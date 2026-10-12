# How Day by Day was built

## 1. Source

The Theodore Roosevelt Association's *Chronological Record* (TRC-CR-1), compiled by Robert J. Moore Jr. (1985): ten typed calendar volumes, 1858–1919, plus a place-names index. Scans were OCR'd (tesseract) into a day-by-day parse of 21,860 records (14,554 with text), with weekday checks against the civil calendar (98.1% match). That parse lives in `private/` and is never committed — the record is copyrighted.

## 2. Place-names index → where TR was (`pipeline/parse_placenames.py`)

The index lists each place with the dates TR was there ("ALBANY, New York — 1882 Jan. 2 – 5 …"). It was re-OCR'd at 300 dpi with word coordinates so the heading column and date column could be separated on skewed pages, then parsed into 1,266 place entries with 3,943 date ranges (day precision, or month precision for childhood residences such as "June – Sept"). It places TR on 17,644 of his 21,986 days.

## 3. Rewrite (`pipeline/rewrite_brief.md`, `pipeline/prepare_chunks.py`, `pipeline/validate_enrich.py`)

The parse was split into 124 chunks of about 120 days. Each chunk was rewritten by an AI worker following the brief: an original headline and summary in the Library's voice, structured events with a controlled action list, people, places, letters, works, references, guests, tags and a 1–5 significance score. TR's own words were copied exactly into `tr_quotes`; nothing else from the record's prose was kept.

Every chunk passed `validate_enrich.py` before acceptance: schema and vocabulary checks, one output per input day, every quote found in the source, and an originality check that rejects any run of six consecutive words shared with the source outside a TR quotation.

## 4. Registries (`pipeline/curate_brief.md`, `pipeline/merge_registries.py`)

The rewrite produced 5,427 person-name variants and 3,142 place variants. These were collapsed by AI curators working through surname- and name-sorted slices into 4,750 people and 2,827 places, with every variant mapped exactly once. `data/people_seed.json` fixed canonical names for the ~100 people who recur most. Places carry a parent (building → town), modern region and country, the name of record where different (Dakota Territory), and a geocoding query.

## 5. Coordinates (`pipeline/geocode_geonames.py`, `pipeline/geocode.py`)

Cities and towns were matched offline against GeoNames (cities500) by name, state and country. Buildings, ranches, parks, waters and other landmarks were looked up with OpenStreetMap Nominatim at one request per second, cached in `data/geocode_cache.json`. Places with no result inherit their parent's coordinates.

## 6. Assembly (`pipeline/build_dataset.py`) and API (`pipeline/build_api.py`)

One record per calendar day of TR's life. Location comes from the place-names index, refined by a more specific place named that day (Elkhorn Ranch rather than "Medora area"); days with no information carry forward the last known place and are marked `carried`. The API is a set of static JSON files generated on every push by GitHub Actions and served by GitHub Pages.

## 7. Fact-check and date corrections (`pipeline/apply_corrections.py`, `data/corrections.json`)

An independent reviewer checked a random sample of 50 days (37 clean, 10 minor, 3 errors, all three inherited from the source) and then audited all 184 days rated 4 or 5, plus every family birth, death, marriage and oath of office. That audit found that the OCR parse had shifted three runs of days while keeping weekdays aligned:

| Run in the parse | Correction | Anchors |
| --- | --- | --- |
| Oct. 10–23, 1901 | +7 days | Booker T. Washington dinner Oct. 16; Yale degree Oct. 23; 43rd birthday Oct. 27 |
| Nov. 6–30, 1906 | −5 days | Election Day Nov. 6; sailed for Panama Nov. 8; Colón Nov. 14 |
| Apr. 10–12, 1898 | −1 day | Archie's birthday Apr. 9; Easter Apr. 10; McKinley's war message Apr. 11 |

Those records were moved (each keeps `redated_from` and its original TRA page citation), and 51 further days received corrected headlines, summaries or an `uncertain` note. `data/corrections_applied.json` logs every applied change. The full audit is in `docs/date_audit.md`.

## 8. Links to the Theodore Roosevelt Center (`pipeline/link_trc.py`)

The TRC Digital Library at Dickinson State University catalogs 141,609 items; 127,873 carry an exact date within TR's life. Using the Library's September 2026 harvest of that catalog (`TRPL/trc-rag/records.jsonl`), every dated item is attached to its day (`archive` on 8,296 days), and each Day by Day letter is matched to its TRC record when the date agrees and TR sits on one side while the correspondent's surname and first name (or initial) match the other side. 4,725 of 7,358 letters (64%) link to a TRC record. Unmatched letters are usually not in the TRC catalog or are addressed by title alone. Re-run `python pipeline/link_trc.py <trc_compact.jsonl>` after a fresh harvest.

## Known limitations

- A comparison of the day entries against the independent place-names index suggests other short runs may be shifted (late Nov. 1876, Feb. 1883, Apr. 1886, late June 1888, early Oct. 1898, Nov. 1907, Dec. 1914, Mar. 1915). None is confirmed; check these before relying on exact dates there.
- 152 days could not be placed by the original OCR parse and have no entry.
- Life-period boundaries (`data/periods.json`) are editorial and marked `verified: false`.
- Person identification is uncertain for bare surnames; those entities carry `uncertain: true`.
- `significance` is an editorial judgment made chunk by chunk; treat it as a ranking aid, not a fact.
- TR quotations are unverified transcriptions. Check the original before publishing.
