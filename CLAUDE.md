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
- Preview: `python -m http.server -d site 8000`.

## Layout
`data/` canonical dataset · `pipeline/` build scripts and worker briefs · `site/` pages, `assets/`, `widgets/daybyday.js` (`site/api/` and `site/data/` are generated) · `docs/` schema and methods.
