# Day by Day — registry curation brief

The rewrite pass named people and places freely, so the same person or place appears under
several spellings. Your job: collapse variants into **canonical entities** for one slice of the
alphabet. Work only from the names given, your general knowledge of Theodore Roosevelt's life,
and `data/people_seed.json`. Do not invent biographical facts; when unsure, leave a field null.

## People (`work/curate/people_partN.json` → `work/curate/people_partN.out.json`)

Input rows: `{name, mentions, role, first}` (`first` = first date the name appears).
Output: a JSON array of canonical people:

```json
{"id": "thomas-c-platt", "name": "Thomas C. Platt",
 "aliases": ["Senator Platt", "Thomas Platt", "Boss Platt"],
 "description": "New York Republican boss and U.S. senator",
 "group": "politics", "uncertain": false}
```

- Every input name must land in exactly one entity's `name` or `aliases`. Merge only when you are
  confident it is the same person (same surname + compatible first name/title + plausible era via
  `first`). "Mrs. Lodge" is NOT Henry Cabot Lodge — she is Anna Cabot Mills Lodge.
- Seed people (`data/people_seed.json`) keep the seed `id` and `name` exactly.
- `id`: lowercase slug of the canonical name.
- `name`: fullest standard form ("William H. Moody"). Keep titles out of `name` unless only a
  title + surname is known ("Captain Bowman McCalla" → "Bowman H. McCalla" if you are sure; else keep).
- `description`: ≤ 12 words, who they were relative to TR, only for people you can identify with
  confidence; otherwise null. Plain, factual, no adjectives of praise.
- `group`: one of `family, friend, household, badlands, harvard, politics, government, military,
  diplomacy, press, literature, science, business, religion, sport, expedition, other`.
- Generic or non-person names ("the Cabinet", "a reporter", "Unnamed cowboy") → one entity each with
  `group: "other"`, `uncertain: true`.

## Places (`work/curate/places_partN.json` → `work/curate/places_partN.out.json`)

Input rows are either `src: "rewrite"` (`{name, region, kind, mentions, first}`) or `src: "index"`
(the TRA place-names index: `{index_id, index_name, region, notes, visit_days, first}`).
Output: a JSON array of canonical places:

```json
{"id": "medora-nd", "name": "Medora", "kind": "town",
 "region": "North Dakota", "country": "United States",
 "historic_region": "Dakota Territory",
 "parent": null,
 "geocode": "Medora, Billings County, North Dakota, USA",
 "aliases": [{"name": "Medora", "region": "Dakota Territory"}, {"name": "Little Missouri", "region": "Dakota"}],
 "index_ids": ["medora-little-missouri-north-dakota-area-includes-elkhorn-chimney-butte-and-lang-ranches"],
 "uncertain": false}
```

- Every input row must land in exactly one place: rewrite rows via `aliases` (name + region exactly
  as given), index rows via `index_ids`.
- `id`: short slug, `name-stateabbr` for US places (`albany-ny`), `name-country` abroad
  (`dresden-germany`), plain slug for unique places (`sagamore-hill`, `white-house`, `ss-hamburg`).
- `kind`: `city, town, ranch, residence, building, institution, region, state, country,
  body_of_water, mountain, ship, train, camp, battlefield, park, other`.
- `region` / `country`: modern names. `historic_region` for the name of record when different
  (Dakota Territory, British East Africa, Ottoman Empire).
- `parent`: the `id` of the enclosing town/city when the place is a building, residence, ranch or
  institution in it (White House → `washington-dc`; Sagamore Hill → `oyster-bay-ny`). Use ids you
  create; if the parent is in another alphabet slice, use the obvious id pattern anyway.
- `geocode`: a query string OpenStreetMap Nominatim can resolve to the right spot, using modern
  names ("Aswan, Egypt", "Ki Jabe, Kenya" → "Kijabe, Kenya"). For a building, the building if it
  still exists ("White House, Washington, DC"), else its town. `null` for ships, trains, "at sea",
  and vague regions with no single point.
- Index entries that bundle several places (e.g. one heading listing ships, or two towns run
  together by OCR) → split sensibly or attach to the best single place and set `uncertain: true`.

## Output rules

Write valid JSON with `ensure_ascii=False`, then check yourself with a short python script that
every input name/row is covered exactly once. Reply with only: entity count, input rows covered,
and any rows you could not place.
