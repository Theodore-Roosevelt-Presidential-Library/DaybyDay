# Day by Day — working notes for Claude

TR's life, one record per day (1858-10-27 → 1919-01-06), served as a static JSON API + explorer + widgets at daybyday.labs.trlibrary.com (GitHub Pages, built by `.github/workflows/pages.yml`).

## Non-negotiables
- The TRA *Chronological Record* text is copyrighted (© 1985 Robert J. Moore Jr. / TRA). It is a research input only. Never commit `private/` or any TRA prose. All prose in `data/` must be original; run `python pipeline/validate_enrich.py --all` after touching `data/enrich/`.
- TR quotations stay verbatim and `verified: false` until checked against the original document.
- Library voice: plain, vivid, specific, warm; no museum-speak; nonpartisan.

## Common tasks
- Fix a day: edit its line in `data/enrich/<chunk>.jsonl`, validate, then `python pipeline/build_dataset.py && python pipeline/build_api.py`.
- Add/merge a person or place alias: edit `data/people.json` / `data/places.json` (aliases), rebuild.
- New coordinates: add to `data/geocode_cache.json` (or run `pipeline/geocode.py` from a machine Nominatim doesn't throttle), then `python pipeline/geocode.py --apply` and rebuild.
- Quote source links: `python pipeline/link_diaries.py ../DiaryExplorer` (after a build, since it reads `data/quotes.jsonl`), then rebuild.
- Speech links: `python pipeline/link_speeches.py` (pulls the speech bank's /api/v1/speeches.json into `data/speeches_by_day.json`), then rebuild.
- Add or change a tour: edit `data/tours.json` (dates anchored to the record's day entries, original prose only), then `python pipeline/build_api.py`. Tour pages are `site/tours.html` and `site/tour.html`; the `<trpl-tour>` / `<trpl-tours>` widgets live in `site/widgets/daybyday.js`. If a route shows a wild jump, fix the day's location in `data/corrections.json` ("locations") and rebuild the dataset.
- Preview: `python -m http.server -d site 8000`.

## Layout
`data/` canonical dataset · `pipeline/` build scripts and worker briefs · `site/` pages, `assets/`, `widgets/daybyday.js` (`site/api/` and `site/data/` are generated) · `docs/` schema and methods.
