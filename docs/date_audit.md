# Day by Day: date and fact audit

Scope: all 184 days with significance 4 or higher in `data/enrich`, plus a scan of every day for births, deaths and marriages in TR's immediate family, TR's oaths of office, and family birthday and anniversary entries. Checks used general historical knowledge, the raw parse (`work/chunks`), and targeted web lookups (Wikipedia, Barry Popik on the muck-rake speech).

Type **a** = event on the wrong date. Type **b** = factual error in the headline or summary. Corrections are in `work/date_audit_fixes.json` (action `flag`; corrected prose only where the record states something wrong).

## Totals

- High-significance days audited: 184; flagged: 27 (11 wrong date, 16 factual).
- All flagged days, any significance: 94 (73 wrong date, 21 factual).

## Systematic parse slips found

1. **October 10-24, 1901 runs one week early.** The parse lost the real Oct. 10-16 entries and slid everything after up by seven days, leaving Oct. 25-30 empty. Anchors: the Booker T. Washington dinner (Oct. 16, press notice Oct. 17), the Yale Bicentennial degree (Oct. 23), TR's 43rd birthday (Oct. 27), Sheffield Cowles's birthday (Oct. 18). The weekdays still line up, which is why this went unnoticed.
2. **November 6-30, 1906 runs five days late.** The parse leaves Nov. 1-4 empty. Anchors: Election Day (Tue. Nov. 6; the parse has it on a Sunday), sailing for Panama Nov. 8, Colón Nov. 14, Ponce Nov. 21, Quentin's birthday Nov. 19, Bamie's anniversary Nov. 25.
3. **April 10-12, 1898 runs one day late** (no Apr. 9 entry): Lee recall and Archie's birthday (Apr. 9), Easter (Apr. 10), McKinley's war message (Apr. 11).
4. **One-line family notes on blank days** often land a day or so off: birthdays and anniversaries for Elliott, Mittie, Alice Lee, Edith, Bamie, TR and Corinne, and the parents' anniversaries in 1870, 1875 and 1877.

Other gaps of three or more empty days in the parse (Jan. 1884, Dec. 1896, Sept. 1902, July 1908, July 1913, Mar. 1915) were spot-checked. No shift was confirmed, but late July 1908 and the July 1913 Grand Canyon trip deserve a closer look.

## Flagged days

| Date in record | Type | Problem | Correct date | Evidence | Confidence |
|---|---|---|---|---|---|
| 1860-02-29 | a | Elliott's birth one day late | 1860-02-28 | Elliott Roosevelt born Feb. 28, 1860 (the record itself later keeps Feb. 28 as his birthday). | high |
| 1862-02-25 | a | Ellie's 2nd birthday logged on wrong day | 1862-02-28 | Elliott born Feb. 28, 1860 | high |
| 1863-07-28 | a | Alice Lee's 2nd birthday logged on wrong day | 1863-07-29 | Alice Lee born July 29, 1861 | high |
| 1864-07-09 | a | Mittie's 29th birthday logged on wrong day | 1864-07-08 | Mittie born July 8, 1835 | high |
| 1869-10-28 | a | TR's 11th birthday logged on wrong day | 1869-10-27 | TR born Oct. 27, 1858; source logs the birthday on both Oct. 27 and 28 | medium |
| 1870-12-21 | a | Parents' 17th anniversary logged Dec. 21 | 1870-12-22 | Married Dec. 22, 1853. | high |
| 1873-01-19 | a | Bamie's 18th birthday logged on wrong day | 1873-01-18 | Bamie born Jan. 18, 1855 | medium |
| 1875-12-11 | a | Parents' 22nd anniversary logged Dec. 11 | 1875-12-22 | Theodore Sr. and Mittie married Dec. 22, 1853. | high |
| 1877-12-23 | a | AMNH opening and parents' 24th anniversary logged Dec. 23 | 1877-12-22 | Parents married Dec. 22, 1853; AMNH building opened by President Hayes Dec. 22, 1877. | high |
| 1878-02-09 (sig ≥4) | b | Says father died 1 a.m. Feb. 10 | 1878-02-09 | Theodore Roosevelt Sr. died late on Feb. 9, 1878 (standard references; Wikipedia, NPS). The TRA time is an outlier. | medium |
| 1881-07-30 | a | Alice's 20th birthday logged on wrong day | 1881-07-29 | Alice Lee born July 29, 1861; parse attached the line to the next day | high |
| 1881-08-04 | a | Edith's 20th birthday logged on wrong day | 1881-08-06 | Edith born Aug. 6, 1861; parse attached the line to the Matterhorn day | high |
| 1882-09-27 | b | "Unexplained" 21st birthday | 1882-09-27 | Corinne born Sept. 27, 1861. | high |
| 1883-09-07 (sig ≥4) | a | Arrival at Little Missouri | 1883-09-08 | Most accounts (Morris, Di Silvestro) put the arrival at about 2-3 a.m. on Sept. 8, 1883. | medium |
| 1886-11-02 (sig ≥4) | b | Hewitt vote total wrong (70,522) | 1886-11-02 | Hewitt received 90,552 votes (official canvass); the TRA figure is a source error. | high |
| 1887-04-28 | a | Corinne's 5th anniversary logged on wrong day | 1887-04-29 | Corinne married Apr. 29, 1882 | high |
| 1887-12-31 (sig ≥4) | a | Founding placed Dec. 31 at Sagamore Hill; month-level date used as a day | Dec. 1887 (exact day unrecorded) | The club grew out of a December 1887 dinner Roosevelt gave in New York (Bamie's house, 689 Madison Ave.) and was formally organized in early 1888. | medium |
| 1889-10-01 | a | Elliott Roosevelt Jr.'s birth | 1889-09-29 | Wikipedia (Elliott Roosevelt, socialite): Elliott Jr. born Sept. 29, 1889. | medium |
| 1890-08-07 | a | Edith's 29th birthday logged on wrong day | 1890-08-06 | Edith born Aug. 6, 1861 | high |
| 1892-10-26 | a | TR's 34th birthday logged on wrong day | 1892-10-27 | TR born Oct. 27, 1858 | high |
| 1894-01-19 | a | Bamie's 39th birthday logged on wrong day | 1894-01-18 | Bamie born Jan. 18, 1855 | medium |
| 1894-04-06 (sig ≥4) | a | Archie's birth logged on wrong day (duplicate entries) | 1894-04-09 | Archibald Bulloch Roosevelt born Apr. 9, 1894. | high |
| 1894-04-16 (sig ≥4) | a | Archie's birth logged on wrong day (duplicate entries) | 1894-04-09 | Archibald Bulloch Roosevelt born Apr. 9, 1894. | high |
| 1896-06-02 | a | De Mores's killing logged June 2 | 1896-06-09 | The Marquis de Mores was killed June 9, 1896, near El Ouatia, Tunisia. | high |
| 1896-06-09 | b | Missing De Mores's death (misplaced to June 2) | 1896-06-09 | De Mores killed June 9, 1896. | high |
| 1896-10-26 | a | TR's 38th birthday logged on wrong day | 1896-10-27 | TR born Oct. 27, 1858 | high |
| 1897-01-19 | a | Bamie's 42nd birthday logged on wrong day | 1897-01-18 | Bamie born Jan. 18, 1855 | medium |
| 1898-02-15 (sig ≥4) | b | Maine death toll given as 262 | 1898-02-15 | 260 died that night; 6 more died later (266 total). | medium |
| 1898-04-10 | a | Lee recall and Archie's 4th birthday logged a day late (parse has no Apr. 9) | 1898-04-09 | Archie born Apr. 9, 1894; Fitzhugh Lee left Havana Apr. 9, 1898. | high |
| 1898-04-11 | a | Easter logged on a Monday | 1898-04-10 | Easter 1898 = Sunday Apr. 10. | high |
| 1898-04-12 | a | McKinley war message logged a day late | 1898-04-11 | McKinley sent the Cuba message to Congress Mon. Apr. 11, 1898. | high |
| 1898-04-23 (sig ≥4) | b | Says TR received lieutenant colonel's commission Apr. 23 | 1898-05-06 (commission) | TR resigned from the Navy and was commissioned May 6, 1898 (see that record; his commission was backdated to Apr. 25 per the source). On Apr. 23 he had only been offered the post. | medium |
| 1900-04-28 | a | Corinne's 18th anniversary logged on wrong day | 1900-04-29 | Corinne married Apr. 29, 1882 | high |
| 1901-09-13 (sig ≥4) | b | Summary ends "McKinley dies" on Sept. 13 | 1901-09-14 (death) | McKinley died about 2:15 a.m. Sept. 14, 1901. | high |
| 1901-09-14 (sig ≥4) | b | Oath time 3:15 p.m. | 1901-09-14 | Most accounts (NPS Wilcox Mansion) put the oath at about 3:30 p.m. | medium |
| 1901-10-10 (sig ≥4) | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-17 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-11 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-18 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-12 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-19 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-13 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-20 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-14 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-21 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-15 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-22 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-16 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-23 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-17 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-24 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-18 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-25 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-19 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-26 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-20 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-27 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-21 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-28 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-22 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-29 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-23 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-30 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1901-10-24 | a | Block of Oct. 10-24, 1901 entries runs one week early in the parse (BTW dinner, Yale degree, 43rd birthday all 7 days early) | 1901-10-31 | Booker T. Washington dined Oct. 16, 1901 (press notice Oct. 17); Yale Bicentennial degree Oct. 23; TR turned 43 Oct. 27; Sheffield Cowles born Oct. 18, 1898. Real Oct. 25-31 slots are empty in the parse. | high |
| 1902-02-19 (sig ≥4) | b | Says the suit was lodged at St. Paul this day | 1902-03-10 (filing) | Knox announced the suit Feb. 19, 1902; the bill was filed in U.S. Circuit Court at St. Paul Mar. 10, 1902. | high |
| 1902-10-13 (sig ≥4) | b | Puts TR aboard Morgan's yacht Corsair | 1902-10-13 (meeting at Jackson Place); Corsair talk was Oct. 11 | Root met Morgan aboard the Corsair in New York on Oct. 11, 1902; on Oct. 13 Morgan and Bacon came to Washington and met the still-lame TR at 22 Jackson Place, where the commission plan was agreed. | high |
| 1902-10-16 (sig ≥4) | b | Garbles commissioners' roles (calls Judge Gray the railway conductors' chief) | 1902-10-16 | E. E. Clark headed the Order of Railway Conductors (seated as the "eminent sociologist"); George Gray was a federal circuit judge from Delaware. | high |
| 1903-02-03 (sig ≥4) | b | Says all three trust measures passed Congress this day | Feb. 11 / 14 / 19, 1903 | Expedition Act signed Feb. 11, Dept. of Commerce and Labor Feb. 14, Elkins Act Feb. 19, 1903; final congressional votes came over the following days. | medium |
| 1905-03-04 (sig ≥4) | b | Inaugural quotation altered | 1905-03-04 | Inaugural Address text: "Much has been given us, and much will rightfully be expected from us." | high |
| 1905-06-10 (sig ≥4) | b | Says Russia accepted peace talks this day | 1905-06-12 (Russia) | Japan accepted June 10, 1905; Russia's formal acceptance came June 12. | medium |
| 1906-01-27 (sig ≥4) | a | Muck-rake Gridiron speech placed on Jan. 27 | 1906-03-17 | Roosevelt first used the muck-rake image at the Gridiron Club dinner of March 17, 1906, and repeated it publicly Apr. 14 (Popik; Library of Congress). | high |
| 1906-03-17 | b | Omits that this is the muck-rake Gridiron dinner | 1906-03-17 | Gridiron Club dinner of March 17, 1906 is where TR first used the muck-rake comparison. | high |
| 1906-04-14 (sig ≥4) | a | Uncle Robert B. Roosevelt's death placed Apr. 14 | 1906-06-14 | Robert Barnwell Roosevelt died June 14, 1906. | high |
| 1906-04-29 | b | Calls it Roosevelt and Edith's 24th anniversary | 1906-04-29 | TR and Edith married Dec. 2, 1886; Corinne married Douglas Robinson Apr. 29, 1882, so this is her 24th. | high |
| 1906-06-14 | b | Uncle Robert B. Roosevelt's death missing (misplaced to Apr. 14) | 1906-06-14 | Robert Barnwell Roosevelt died June 14, 1906. | high |
| 1906-06-29 (sig ≥4) | b | Credits Pure Food and Drug Act (and agricultural appropriation) to June 29 | 1906-06-30 | Hepburn Act signed June 29, 1906; Pure Food and Drug Act and the agricultural appropriation carrying meat inspection signed June 30. | high |
| 1906-06-30 (sig ≥4) | b | Credits Hepburn Act to June 30 | 1906-06-29 | Hepburn Act signed June 29; Pure Food and Drug and meat inspection June 30, 1906. | high |
| 1906-11-06 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-01 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-07 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-02 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-08 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-03 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-09 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-04 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-10 (sig ≥4) | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-05 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-11 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-06 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-12 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-07 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-13 (sig ≥4) | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-08 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-14 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-09 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-15 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-10 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-16 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-11 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-17 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-12 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-18 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-13 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-19 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-14 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-20 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-15 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-21 (sig ≥4) | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-16 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-22 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-17 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-23 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-18 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-24 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-19 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-25 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-20 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-26 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-21 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-27 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-22 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-28 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-23 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-29 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-24 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1906-11-30 | a | Block of Nov. 6-30, 1906 entries runs five days late in the parse | 1906-11-25 | Election Day was Tue Nov. 6, 1906 (parse: Sun Nov. 11); TR sailed for Panama Nov. 8, reached Colon Nov. 14, Ponce Nov. 21; Quentin born Nov. 19; Bamie wed Nov. 25. Parse leaves Nov. 1-4 empty. | high |
| 1908-10-31 (sig ≥4) | a | Root-Takahira Agreement dated Oct. 31 | 1908-11-30 | The Root-Takahira notes were exchanged Nov. 30, 1908 (Takahira's draft arrived late Oct.). | high |
| 1912-02-21 (sig ≥4) | b | Says he formally became a candidate this day | 1912-02-24 | "Hat in the ring" was an informal remark to reporters Feb. 21; the formal declaration was his Feb. 24 reply to the seven governors (published Feb. 25-26). | medium |
| 1914-04-06 (sig ≥4) | b | Places the Colombia treaty signing in Washington | 1914-04-06 | Thomson-Urrutia Treaty signed at Bogota by U.S. Minister Thaddeus Thomson (also flagged in work/factcheck_report.md). | high |
| 1915-04-05 | a | Easter Sunday logged on wrong day | 1915-04-04 | Easter 1915 = Apr. 4 | high |
| 1915-04-28 | a | Corinne's 33rd anniversary logged on wrong day | 1915-04-29 | Corinne married Apr. 29, 1882 | high |
| 1916-08-07 | a | Edith's 55th birthday logged on wrong day | 1916-08-06 | Edith born Aug. 6, 1861 | high |

## Checked and confirmed (high significance, not flagged)

All other significance ≥4 days check out on date and substance. Among them are the births of TR, Ted, Quentin and Alice; the deaths of Mittie and Alice (Feb. 14, 1884), Elliott (Aug. 14, 1894), Quentin (July 14, 1918) and TR (Jan. 6, 1919); the weddings of Oct. 27, 1880 and Dec. 2, 1886; and the oaths of office for the Assembly (Jan. 3, 1882), Police Board (May 6, 1895), Assistant Secretary of the Navy (Apr. 19, 1897), Governor (Dec. 31, 1898 / Jan. 2, 1899), Vice President (Mar. 4, 1901), President (Sept. 14, 1901) and the 1905 inauguration. The marriages of Elliott, Corinne, Bamie, Alice, Ted, Ethel, Kermit and Archie, and the births of Corinne, Kermit and Ethel, are all on the correct dates.

## Minor issues left unflagged

- 1898-04-24: Spain's declaration is variously dated Apr. 23 or 24.
- 1898-07-17: "17,000" surrendered mixes the city garrison with the wider district.
- 1907-03-02: the count of 32 midnight forests is as given in the source.
- 1886-10-15: the "headless" Statue of Liberty is the source's claim and is doubtful.
- 1870-02-03: "Ellie's birthday" party in Rome (his birthday is Feb. 28) is unexplained.
