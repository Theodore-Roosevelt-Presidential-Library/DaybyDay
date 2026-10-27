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

One record per calendar day of TR's life. Location is decided in this order (`location.source`):

1. `heading`: the day's own place heading in the record ("SAGAMORE HILL –", "MILWAUKEE, Wisconsin –"), resolved to the place registry by `pipeline/extract_headers.py` into `data/day_headers.json` (place ids only, no source prose). When headings are stacked ("KENTUCKY – SAGAMORE HILL"), the last one wins. 11,519 days have one.
2. `heading-carried`: between headings, the last stated place carries forward for up to 45 days, unless the index records a short (two weeks or less) day-precise visit somewhere else (`index`), or an arrival event that day names a new place (`arrival`), which later days then carry.
3. `index`: with no recent heading, the place-names index, shortest day-precise stay first. Index entries the OCR ran together (ship lists) are not used, and any index visit that every heading in its span contradicts is dropped as a misread date (17 visits). Two index entries filed under the wrong year are corrected in `data/places_index_overrides.json` (Cuba, 1913 → 1898; Meru Boma, 1912 → 1909).
4. `entry`: a place named in the day's entry; 5. `carried`: the last known place.

A more specific place inside the chosen one and named that day refines it (`+refined`: the Gilpatrick Hotel inside Milwaukee). Heading-first replaced an earlier index-first rule that let month-long index ranges ("Kentucky, Mar.–Apr. 1888", long Oyster Bay stays) override what the day itself said. The API is a set of static JSON files generated on every push by GitHub Actions and served by GitHub Pages.

## 7. Fact-check and date corrections (`pipeline/apply_corrections.py`, `data/corrections.json`)

An independent reviewer checked a random sample of 50 days (37 clean, 10 minor, 3 errors, all three inherited from the source) and then audited all 184 days rated 4 or 5, plus every family birth, death, marriage and oath of office. That audit found that the OCR parse had shifted three runs of days while keeping weekdays aligned:

| Run in the parse | Correction | Anchors |
| --- | --- | --- |
| Oct. 10–23, 1901 | +7 days | Booker T. Washington dinner Oct. 16; Yale degree Oct. 23; 43rd birthday Oct. 27 |
| Nov. 6–30, 1906 | −5 days | Election Day Nov. 6; sailed for Panama Nov. 8; Colón Nov. 14 |
| Apr. 10–12, 1898 | −1 day | Archie's birthday Apr. 9; Easter Apr. 10; McKinley's war message Apr. 11 |

Those records were moved (each keeps `redated_from` and its original TRA page citation), and 51 further days received corrected headlines, summaries or an `uncertain` note. `data/corrections_applied.json` logs every applied change. The full audit is in `docs/date_audit.md`.

### Chronology spot-check (October 2026)

Three reviewers each took one era (1858–1888, 1889–1908, 1909–1919) and checked 124 days against outside sources: a random sample plus targeted date anchors. Result: 105 correct, 13 minor issues, 6 errors. Roosevelt's own activities and every sampled quotation held up. The errors were all world events the record logs on the day the news reached him rather than the day they happened (Mount Pelée, the Entente Cordiale, Bryan's nomination, the Hayes inauguration, the Brooklyn Bridge cables); those days now say so in `uncertain` and the summaries were rewritten. The check also confirmed and fixed these date slips:

| Day(s) | Correction |
| --- | --- |
| July 14–16, 1913 (Grand Canyon) | July 14 split; descent moved to July 15, North Rim climb to July 16 |
| Aug. 24–26, 1913 (return from Arizona) | Chicago stop to Aug. 25, New York arrival to Aug. 26; Aug. 24 now the train east |
| Apr. 5, 1915 | Easter note moved to Easter Sunday, Apr. 4 |
| July 27, 1908 | Taft's acceptance speech moved to July 28 |
| Oct. 24, 1901 | items from the source's Oct. 24 entry moved to Oct. 31 with the rest of the shifted run |

Moves, splits (`splits` in `data/corrections.json`) and fixes are all logged in `data/corrections_applied.json`. Seven runs flagged earlier as possibly shifted (Nov. 1876, Feb. 1883, Apr. 1886, June 1888, Oct. 1898, Nov. 1907, Dec. 1914) were checked and cleared. Late March 1915 is compressed in the source; affected days carry an `uncertain` note.

### Notes for readers

Each day's `uncertain` field is shown on the site as "A note on this day." In October 2026 the 1,756 notes written in pipeline language ("OCR reads…", "source parse") were rewritten for the public by the same brief, keeping every fact and caveat; 187 that described only transcription fixes with no remaining doubt were dropped. Event lines on news-lag days now say the news arrived rather than that the event happened. `site/about.html` ("About the dates") explains the record, news lag, notes, moved days, locations and unverified quotations, and invites corrections to hello@trlibrary.com.

## 8. Links to the Theodore Roosevelt Center (`pipeline/link_trc.py`)

The TRC Digital Library at Dickinson State University catalogs 141,609 items; 127,873 carry an exact date within TR's life. Using the Library's September 2026 harvest of that catalog (`TRPL/trc-rag/records.jsonl`), every dated item is attached to its day (`archive` on 8,296 days), and each Day by Day letter is matched to its TRC record when the date agrees and TR sits on one side while the correspondent's surname and first name (or initial) match the other side. 4,725 of 7,358 letters (64%) link to a TRC record. Unmatched letters are usually not in the TRC catalog or are addressed by title alone. Re-run `python pipeline/link_trc.py <trc_compact.jsonl>` after a fresh harvest.

## Known limitations

- The record sometimes logs outside events on the day news reached Roosevelt, not the day they happened. Days found so far are noted in `uncertain`; treat world-event dates as approximate unless confirmed.
- Late March 1915 is compressed in the source; exact dates there are not confirmed.
- 152 days could not be placed by the original OCR parse and have no entry.
- Life-period boundaries (`data/periods.json`) are editorial and marked `verified: false`.
- Person identification is uncertain for bare surnames; those entities carry `uncertain: true`.
- `significance` is an editorial judgment made chunk by chunk; treat it as a ranking aid, not a fact.
- TR quotations are unverified transcriptions. Check the original before publishing.

## Linking quotations to the originals

Each quotation cites the record page it was transcribed from. Diary quotations from 1878–1884 also link to the page in T.R.'s pocket diaries (Library of Congress, Theodore Roosevelt Papers, Series 8, Vols. 1–7). `pipeline/link_diaries.py` compares each quotation with the Library's page-by-page transcription in the DiaryExplorer repo: first the pages dated within a day of it (kept when at least 60% of its words appear in order), then the rest of the volume at a stricter 80% bar. The wider search finds catch-up entries and the 1884 Bighorn log, which T.R. kept in his 1883 volume under printed 1883 dates. Of 1,033 such quotations, 1,017 are linked; 9 of those go only to the page for that date. Letter quotations link to the letter at the Theodore Roosevelt Center when T.R. wrote only one recorded letter that day (362). The links are a way to check the wording; they do not mark it verified.

## Linking speeches

`pipeline/link_speeches.py` takes the speech list from the Library's speech bank (speeches.labs.trlibrary.com/api/v1/speeches.json) and attaches each speech dated to the day to that day's record, with a link to its page in the bank. Speeches dated only to a month or year are left out. The snapshot lives in `data/speeches_by_day.json`; rerun the script when the bank grows.
