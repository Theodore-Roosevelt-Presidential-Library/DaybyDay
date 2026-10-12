# Day by Day: independent fact-check sample

Sample: `random.seed(7)`. The script took `random.sample(hi, 25)` and then `random.sample(lo, 25)` from the date-sorted lists of `data/enrich` records. `hi` holds the 184 days with significance of 4 or higher; `lo` holds the 14,370 days with significance 1 to 3. Every day was checked against `work/chunks/*.json` `days[].text`, and some outside facts were spot-checked.

What each verdict means:
- **OK**: nothing to fix.
- **MINOR**: a wording, sequence or nuance issue, or a source error repeated without a flag. It does not change the basic facts.
- **ERROR**: a wrong date, place or attribution that a reader would take as fact.

## Significance >= 4 (25)

| Date | Verdict | Note |
|---|---|---|
| 1903-03-14 | OK | Pelican Island and the five reclamation projects are correct. "Harding" → Darling is fixed and flagged. "First of its kind" is not in the source but is accurate. |
| 1897-11-19 | OK | Quentin's birth. Quotes are verbatim, apart from OCR punctuation. |
| 1904-11-08 | MINOR | The Leupp/returns event is placed at Sagamore Hill and comes before the return to D.C. The source line is ambiguous, and TR heard the returns at the White House. Vote figures and the pledge quote are correct. |
| 1914-04-06 | **ERROR** | The record adds "In Washington" for the Colombia treaty. It was signed at Bogotá by U.S. Minister Thomson, and the source only says Bryan signs. The event is also tagged `legislation`. Fix written. |
| 1883-09-07 | OK | The possible Sept 8 arrival is already flagged in `uncertain`. |
| 1884-02-13 | MINOR | COPYING: the summary follows the source clause by clause (fog → two telegrams → rushes → 10:30 → comatose). It passes the 6-word check but is a structural paraphrase. |
| 1908-06-18 | MINOR | The headline "Taft nominated after a Roosevelt stampede" suggests the stampede happened. Lodge stopped it. The summary is accurate. |
| 1886-10-15 | MINOR | The "headless" Statue of Liberty comes from the source but is doubtful 13 days before the dedication. It should be verified or flagged. |
| 1903-12-17 | OK | Cuban reciprocity and the Wright flights are correct. (The place name "Washington" vs "Washington, D.C." is inconsistent in `places`.) |
| 1910-05-31 | OK | The Guildhall quote is verbatim from the source and marked unverified. |
| 1883-09-16 | OK | |
| 1907-11-04 | OK | The TC&I account follows the source. The source's editorial aside was correctly left out. |
| 1898-12-31 | MINOR | The summary presents undated items from the back pages (Albany Military Academy, the governess, the first Scribner's installment, which was in the Jan 1899 issue) as events of the day. `uncertain` flags this, but the summary does not. |
| 1880-10-27 | MINOR | "Edith Carow dances the evening away": the reception ended about 4 p.m. The source says she danced "the soles off her shoes." Quotes are fine, with the OCR fix 'Qur' → 'Our'. |
| 1886-04-01 | OK | The long quote is TR's own account as quoted by Hagedorn, labelled correctly. "Earlier" for the doe is a mild inference. |
| 1906-01-27 | **ERROR** | The headline makes this the muck-rake debut. Standard dating (AP "Today in History") puts TR's first Gridiron muck-rake remarks at the **17 March 1906** dinner, and the dataset also has a Gridiron dinner on that date. The source date was repeated without a flag. Fix: hedged wording plus an `uncertain` note. |
| 1905-07-06 | OK | |
| 1884-02-12 | OK | Follows the source's 10 a.m. time. The order is changed enough not to count as a paraphrase. |
| 1900-06-21 | OK | The 926/925 vote totals are correct. |
| 1886-09-20 | OK | The quote is verbatim. |
| 1908-11-03 | OK | Electoral and popular votes are correct. The "frazzle" remark is marked as a remark. |
| 1905-08-05 | OK | |
| 1883-09-18 | OK | |
| 1909-03-04 | MINOR | "National Bison Range is created": the range was created by the act of 23 May 1908 (the dataset has this too). The act of 4 March 1909 (35 Stat. 1051) **enlarged** it. "Opened the house" is quoted as diary, with an `uncertain` flag. |
| 1894-04-06 | **ERROR** | The headline presents Archie's birth as happening this day. The same source text appears again on 16 April, and Archibald was born **9 April 1894**. `uncertain` notes this, but the headline, summary and significance 4 still assert it. Fix written. |

## Significance 1–3 (25)

| Date | Verdict | Note |
|---|---|---|
| 1882-11-05 | OK | Location only. "Final days of the campaign" is an inference, but true (Assembly election 7 Nov). |
| 1907-09-24 | OK | |
| 1907-08-01 | OK | |
| 1905-07-07 | OK | The NEA speech at Ocean Grove is correct. [G] guests are listed. |
| 1873-05-20 | OK | |
| 1905-03-29 | OK | Sheffield Cowles Jr. is correctly identified as his nephew. |
| 1905-08-19 | OK | Repeats the source's "Canada" (Newfoundland was a separate dominion). Acceptable. |
| 1896-06-04 | OK | |
| 1872-10-30 | OK | |
| 1882-08-06 | OK | Edith was born 6 Aug 1861, so 21 is correct. |
| 1871-10-08 | OK | |
| 1904-04-17 | OK | |
| 1918-03-01 | OK | |
| 1878-06-06 | OK | The diary quotes are verbatim. |
| 1886-07-18 | OK | |
| 1897-11-29 | MINOR | The headline says "Orders for the North Atlantic Squadron", but the source says only a letter "on" the squadron. |
| 1878-12-06 | OK | |
| 1903-07-19 | OK | |
| 1877-09-24 | MINOR | The headline and summary say "Summer at Oyster Bay" for 24 September. The source gives only a location. |
| 1904-12-15 | OK | The two-day source block is split correctly (the Dec 14 record holds the first half). |
| 1887-08-23 | OK | |
| 1904-06-17 | OK | The Cortelyou telegram quotes are verbatim, with the source's ellipsis kept. |
| 1916-03-29 | OK | "Meets again" is a small addition. The Wilson "with whiskers" quote is verbatim. |
| 1910-02-02 | OK | |
| 1880-07-29 | OK | |

## Summary

| | OK | MINOR | ERROR |
|---|---|---|---|
| Sig >= 4 (25) | 14 | 8 | 3 |
| Sig 1–3 (25) | 23 | 2 | 0 |
| **Total (50)** | **37 (74%)** | **10 (20%)** | **3 (6%)** |

What I found by check:

- **Quotes:** I found no misquotes or misattributions in any of the 15 days that have `tr_quotes`. Every quote is in the source, the only changes are OCR fixes, and each is TR's own words.
- **Copying:** Verbatim 4-gram overlap with the source is negligible. One summary is a structural, clause-by-clause paraphrase (1884-02-13).
- **Voice:** I found no museum-speak or partisan editorializing. Where the source editorializes (1907-11-04), that aside was left out correctly.

Patterns:

1. **Source dating errors are passed through.** All three ERRORs, and the Bison Range and Statue of Liberty MINORs, come from the TRA chronology's own misdated or misattributed items. The rewrite repeats them, and at best notes them in `uncertain`. The headline and summary still state them as fact. This matters most on the significance-4+ days, which are the ones most likely to be featured.
2. **Duplicate milestones.** Archie's birth is asserted on both 1894-04-06 and 1894-04-16, and neither is the true date (9 April). The National Bison Range is "created" on both 1908-05-23 and 1909-03-04. A dataset-wide check for repeated `birth`/`death`/`marriage`/creation events is worth running.
3. **Small additions in headlines.** Headlines add words that sharpen the claim beyond the source ("Orders", "Summer", "after a Roosevelt stampede", "In Washington").

Outside this sample: the 1908-05-23 record gives "18,000 acres" from the source. The 1908 statute authorized up to 12,800 acres. The 1894-04-16 record also needs the April 9 correction.

Fixes for the 3 ERRORs are in `work/factcheck_fixes.jsonl`. Each line is the full record with only the corrected fields changed. All three pass `validate_enrich.check_chunk`, tested in a scratch copy. `data/enrich` itself was not changed.
