# Day by Day — data schema

All dates are ISO `YYYY-MM-DD` in the Gregorian calendar. IDs are lowercase slugs and stable across releases.

## Day (`data/days.jsonl`, `/api/v1/days/{date}.json`)

| Field | Type | Notes |
| --- | --- | --- |
| `date`, `weekday`, `year`, `month`, `day` | | calendar fields |
| `age` | int | TR's age that day (born 1858-10-27) |
| `has_entry` | bool | false when the record is silent for that day |
| `headline` | string | 3–9 words, Library's own wording |
| `summary` | string | 1–3 sentences, Library's own wording |
| `significance` | int 0–5 | 0 no entry · 1 routine · 2 notable · 3 important · 4 major · 5 history-making |
| `location` | object | `{id, name, lat, lon, source, also[]}` — where TR most likely was. `source`: `heading` (the day's own place heading in the record), `heading-carried` (last heading carried forward), `arrival` (an arrival event that day), `index` (TRA place-names index), `entry` (named in the day only), `carried` (no information; last known place carried forward), `correction` (set by hand in `data/corrections.json` → `locations`, with the reason); `+refined` means a more specific place inside it, named that day, was used |
| `places` | id[] | every place named that day plus the index places for that date |
| `people` | `{id, role}`[] | role: family, companion, host, guest, correspondent, official, colleague, visitor, subject, adversary, other |
| `events` | object[] | `{seq, action, detail, time, people[], places[]}`; `action` from the controlled list below |
| `letters` | object[] | `{direction: from_tr \| to_tr, correspondent (person id or name), correspondent_resolved, topic}` |
| `tr_quotes` | object[] | `{text, kind: diary \| letter \| speech \| remark \| writing, verified: false, source}` — TR's words as transcribed in the record. `source.cited_in` is `{work, pages[]}` in the record. `source.original`, when present, is the original document: `{type: diary_page, title, url, holder, explorer, match}` (LOC scan of the 1878–1884 pocket diaries; `explorer` is the same page at diary.labs.trlibrary.com; `match` is the share of the quote's words found in order on the page's transcription, or null when only the page's date is known) or `{type: letter, title, url, holder}` (TRC item, given only when T.R. wrote a single recorded letter that day) |
| `works` | object[] | `{title, kind: book \| article \| speech \| review \| message \| other}` written, published or delivered that day |
| `references` | object[] | `{title, pages}` — secondary sources the record points to |
| `guests` | id[] | Sagamore Hill guest-book names for the day |
| `tags` | string[] | controlled topic list below |
| `periods` | id[] | every period (any facet) containing the date |
| `film` | bool | motion-picture footage of the day exists |
| `redated_from` | date \| null | the record's original date in the source, when it was moved or split off by a correction |
| `sources` | object[] | `{work, pages[]}` — volume and page in the TRA Chronological Record |
| `uncertain` | string \| null | caveat about OCR, dating or identification |
| `speeches` | object[] | `{id, title, kind: speech \| message \| lecture, full_text, url}` — speeches in the Library's speech bank (speeches.labs.trlibrary.com) dated to this day; `full_text` false means the bank links to the original at an archive |

**Event actions:** travel, arrival, departure, speech, meeting, conference, correspondence, writing, reading, publication, official_act, appointment, legislation, election, campaign, ceremony, social, family, guest, hunting, ranching, natural_history, exercise, sport, military, battle, illness, injury, death, birth, marriage, education, religion, legal, business, press, photograph, film, honor, other.

**Tags:** family, childhood, education, harvard, travel, europe, africa, south-america, badlands, ranching, hunting, natural-history, conservation, outdoors, writing, reading, politics, campaign, legislature, civil-service, police, navy, military, rough-riders, governor, vice-presidency, presidency, foreign-policy, diplomacy, panama-canal, labor, business, trusts, race, immigration, science, health, religion, press, society, friendship, grief, celebration, war, world-war-i, progressive-party, death.

## Person (`data/people.json`)

`{id, name, aliases[], description, group, relation, uncertain, mentions, first, last, top_places[], top_companions[]}`

`group`: family, friend, household, badlands, harvard, politics, government, military, diplomacy, press, literature, science, business, religion, sport, expedition, other. `description` is null where identification is not certain. `uncertain: true` marks bare surnames and names that could not be pinned to one person.

## Place (`data/places.json`)

`{id, name, kind, region, country, historic_region, parent, geocode, lat, lon, coord_source, coord_precision, osm, aliases[], index_ids[], uncertain, days_present, first, last}`

`kind`: city, town, ranch, residence, building, institution, region, state, country, body_of_water, mountain, ship, train, camp, battlefield, park, other. `parent` is the enclosing place (White House → washington-dc). `coord_source`: `nominatim`, `geonames`, or `parent` (inherited from the enclosing place). `coord_precision`: `exact` when the coordinates are the place itself (a geocoder match that names it or is its street address, near its town), `approximate` when they stand in for it (the town's point, or a doubtful match). The map zooms to street level only for `exact` buildings and residences. Ships, trains and vague regions have no coordinates.

## Period (`data/periods.json`)

`{id, facet, label, start, end, anchor, verified}`. Facets: `life_stage` (every day belongs to exactly one), `office`, `journey`, `campaign`. `verified: false` until an editor confirms the boundary dates against a second source.

## Tour (`data/tours.json`, `/api/v1/tours/index.json`, `/api/v1/tours/{id}.json`)

`data/tours.json`: `{id, title, kind, start, end, short, summary, anchor, verified}`. `kind`: `speaking` (speaking tour), `campaign` (campaign tour), `expedition`, `abroad` (travel abroad), `hunting` (hunting trip), `military` (war service). `start` is the day he set out and `end` the day he reached home, or the record's last travel day; `anchor` cites the record's day entries for both. `short` and `summary` are original Library prose. Tours may overlap `journey` periods; they are a separate, fuller list.

`/api/v1/tours/{id}.json` adds `kind_label`, `url` and:

- `stats`: `{days, days_with_entry, stops, distinct_places, states[], territories[], countries[], abroad[], straight_line_km, letters, speeches, tr_quotes, people}`. Days count both the day he set out and the day he got home. States and countries come from every day with a stated place (not carried forward); `states` leaves out his home bases (Oyster Bay, New York City, Washington), and `territories` lists the states he reached before their admission (Dakota in 1883, Arizona and New Mexico before 1912, and so on). `abroad` is `countries` without the United States, in today's borders. `straight_line_km` sums straight lines between stops, so it is a floor, not the distance traveled.
- `route`: `{id, name, kind, lat, lon, start, end, days}[]` — runs of consecutive days at one place, using only days whose location the record states or the place-names index gives (not days carried forward from the last known place) and leaving out places as broad as a state or country.
- `highlights`: the eight most significant days, in date order. `people`: the 24 people named on the most days.
- `days`: every date in the tour, `{date, n, has_entry, headline, summary, significance, location, location_id, lat, lon, firm, broad, speeches, letters}`; `firm` is false when the location is only carried forward, `broad` true when it is a whole state or country.

`/api/v1/tours/index.json`: `{kinds, tours: [{id, title, kind, kind_label, start, end, short, url, stats: {days, stops, straight_line_km, speeches, states, territories, countries, abroad[]}, bbox, line}]}`, where `line` is the route simplified to at most 60 `[lon, lat]` points for thumbnails.

Each day in `/api/v1/days/{date}.json` also carries `tours`: `{id, title, day, of, prev, next}[]` for any tour that includes it.

## Stay (`/api/v1/stays.json`)

`{place, name, lat, lon, kind, precise, start, end, days}` — consecutive days at the same `location`.

## Place visits (`/api/v1/places/index.json`, `/api/v1/places/{id}.json`)

Each place also carries `visit_days`, `visit_first` and `visit_last`: the days the record puts T.R. *at* the place (the day's location, unless only carried forward with no information, or a stop the place-names index gives for that date), as opposed to `days_present`, which also counts days the place is only named; `mention_days` counts those named-only days. A named place also counts as visited when it shares the spot (within about 2 km), parent or child of a place he was that day. Entries in a place's `days[]` have `here: true` on visit days and `probable: true` when the location is carried forward from the last place heading. The "Was he here?" page (`near.html`) answers from visit days and lists named-only days under "Connected from afar".
