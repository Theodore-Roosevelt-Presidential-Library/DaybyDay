# Day by Day — rewrite brief

You are turning one chunk of the Theodore Roosevelt Association's *Chronological Record*
(TRA, © 1985) into original, structured day records for the Theodore Roosevelt Presidential
Library's **Day by Day** dataset.

The TRA text is a **research source only**. Its wording is copyrighted and must never appear
in our output, except TR's own words (see `tr_quotes`). Facts — who, what, where, when — are
free to use. Write every sentence fresh.

## Input

`work/chunks/<chunk>.json` → `{"chunk": "...", "days": [{date, weekday, age, tra_pages, text}]}`.
The `text` is OCR of a typed calendar. Expect OCR noise (`1T.R.` = `T.R.`, `pever` = `never`,
`Unites` = `United`), and editorial markers:

| marker | meaning |
| --- | --- |
| `[D] "…"` | quotation from TR's own diary |
| `[G] names` | guests recorded at the house that day (guest book) |
| `[F]` | film footage of the day exists |
| `[H]` | source note (ignore) |
| `Letters:` then `T.R. to X: …` | letters TR wrote that day; `X to T.R.: …` letters he received |
| `[See … pp. …]` | bibliographic pointer — record in `references` as title + pages, never as prose |
| ALL CAPS place at line start | where TR was, e.g. `SAGAMORE HILL -` |

## Output

Write **one JSON object per line** (JSONL) to `data/enrich/<chunk>.jsonl`, one line for every
day in the input, in date order. Schema:

```json
{
  "date": "1884-06-09",
  "headline": "Back at the Little Missouri",
  "summary": "Roosevelt reaches Medora from the Chicago convention, where Joe Ferris and Bill Merrifield meet his train, and tells a St. Paul reporter he will not bolt the Republican ticket.",
  "events": [
    {"action": "travel", "detail": "Arrives in Medora by rail and goes on to his Chimney Butte ranch", "people": ["Joseph Ferris", "William Merrifield"], "places": ["Medora", "Chimney Butte Ranch"], "time": null},
    {"action": "press", "detail": "Interview with the St. Paul Pioneer Press about the 1884 Republican convention", "people": [], "places": [], "time": null}
  ],
  "people": [
    {"name": "Joseph Ferris", "role": "companion"},
    {"name": "William Merrifield", "role": "companion"}
  ],
  "places": [
    {"name": "Medora", "region": "Dakota Territory", "kind": "town"},
    {"name": "Chimney Butte Ranch", "region": "Dakota Territory", "kind": "ranch"}
  ],
  "letters": [],
  "tr_quotes": [
    {"text": "Arrived at my cattle ranche ('Chimney Butte Ranche') on the Little Missouri.", "kind": "diary"}
  ],
  "works": [],
  "references": [],
  "guests": [],
  "film": false,
  "tags": ["badlands", "ranching", "politics", "press"],
  "significance": 3,
  "uncertain": null
}
```

### Field rules

- **headline** — 3 to 9 words, sentence case, no period. Concrete: "Sworn in as President in Buffalo", not "A momentous day".
- **summary** — 1 to 3 sentences, max ~60 words, in the Library's voice: plain, vivid, specific, warm, never stuffy. Lead with what TR did. Call him "Roosevelt" (or "TR" sparingly); use family first names after the first mention of the day ("his wife Edith"). No museum-speak ("transformative", "iconic", "world-class"). No editorializing beyond what the source supports. Do not reuse any run of 6+ words from the TRA text outside a quotation.
- **events** — every distinct thing that happened, in order. `action` from this list only:
  `travel, arrival, departure, speech, meeting, conference, correspondence, writing, reading, publication, official_act, appointment, legislation, election, campaign, ceremony, social, family, guest, hunting, ranching, natural_history, exercise, sport, military, battle, illness, injury, death, birth, marriage, education, religion, legal, business, press, photograph, film, honor, other`.
  `detail` is our words, ≤ 25 words. People and places listed per event use the same names as the day-level lists.
- **people** — everyone named (not TR himself). Use the exact `name` from `data/people_seed.json` when the person is there (match nicknames: Edith, Bamie, Conie, Mittie, Ted, Lodge, etc.). Otherwise the fullest correct name the text supports ("Senator Thomas Platt" → "Thomas C. Platt"; "Steffens" → "Lincoln Steffens"). If only a surname is given and you cannot be sure who it is, use what is written plus a title ("Captain Bowman McCalla"). `role`: `family, companion, host, guest, correspondent, official, colleague, visitor, subject, adversary, other`.
- **places** — every place TR was or that matters to the day. Modern-standard spelling for well-known places (Aswan for "Assouan") but keep historic names when they are the name of record (Dakota Territory, Constantinople). `kind`: `city, town, ranch, residence, building, institution, region, state, country, body_of_water, mountain, ship, train, camp, battlefield, other`. Ships are places (`"S.S. Hamburg"`, kind `ship`). Only list a place the text names (an ALL-CAPS header counts); don't infer a specific place from a vague header like `MOUNTAINS` — use the vaguer name or leave it out, and say so in `uncertain`.
- **letters** — one entry per letter under `Letters:`. `{"direction": "from_tr" | "to_tr", "correspondent": name, "topic": "our words, ≤ 15 words"}`.
- **tr_quotes** — TR's own words only (diary `[D]`, his letters, speeches, remarks), copied **exactly** as they appear in the text, fixing only obvious OCR errors (note any fix in `uncertain`). `kind`: `diary, letter, speech, remark, writing`. Never quote anyone else's words, and never quote the TRA compiler.
- **works** — books, articles, speeches TR wrote, published or delivered that day: `{"title", "kind": "book|article|speech|review|message|other"}`.
- **references** — sources the entry cites: `{"title": "The Letters of Theodore Roosevelt", "pages": "V. 8, p. 1449"}`.
- **guests** — names from `[G]` lines (also add them to `people` with role `guest`).
- **film** — true if `[F]` appears.
- **tags** — 1 to 6 from: `family, childhood, education, harvard, travel, europe, africa, south-america, badlands, ranching, hunting, natural-history, conservation, outdoors, writing, reading, politics, campaign, legislature, civil-service, police, navy, military, rough-riders, governor, vice-presidency, presidency, foreign-policy, diplomacy, panama-canal, labor, business, trusts, race, immigration, science, health, religion, press, society, friendship, grief, celebration, war, world-war-i, progressive-party, death`.
- **significance** — 1 (routine) to 5 (a day schoolchildren learn about). Most days are 1–2. Reserve 5 for e.g. birth, death, San Juan Hill, becoming President, Milwaukee shooting.
- **uncertain** — short note if OCR garbling, a doubtful date, or an unclear name affected what you wrote; else null.

### Do not

- Invent facts, motives, weather, or feelings not in the source.
- Paraphrase sentence-by-sentence. Read the day, then write it new.
- Drop days. Every input day gets exactly one output line, even if thin ("Letters only").
- Put TRA bibliographic or editorial asides into the summary.

## Finish

Run `python3 pipeline/validate_enrich.py <chunk>` and fix every error it reports before you stop.
