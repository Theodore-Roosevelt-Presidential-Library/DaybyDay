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
| `location` | object | `{id, name, lat, lon, source, also[]}` — where TR most likely was. `source`: `heading` (the day's own place heading in the record), `heading-carried` (last heading carried forward), `arrival` (an arrival event that day), `index` (TRA place-names index), `entry` (named in the day only), `carried` (no information; last known place carried forward); `+refined` means a more specific place inside it, named that day, was used |
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

## Stay (`/api/v1/stays.json`)

`{place, name, lat, lon, kind, precise, start, end, days}` — consecutive days at the same `location`.
