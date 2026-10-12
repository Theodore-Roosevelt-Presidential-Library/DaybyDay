"""Validate a rewrite chunk: schema, coverage, controlled vocabularies, and originality.

Usage: python pipeline/validate_enrich.py <chunk-id> [--quiet]
       python pipeline/validate_enrich.py --all

Originality check: no run of 6 consecutive words in our prose fields (headline, summary,
event detail, letter topic) may match the TRA source text for that day, unless the run sits
inside a TR quotation. TR quotations must appear in the source (after normalising OCR spacing).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

ACTIONS = set("""travel arrival departure speech meeting conference correspondence writing reading publication
official_act appointment legislation election campaign ceremony social family guest hunting ranching
natural_history exercise sport military battle illness injury death birth marriage education religion legal
business press photograph film honor other""".split())
TAGS = set("""family childhood education harvard travel europe africa south-america badlands ranching hunting
natural-history conservation outdoors writing reading politics campaign legislature civil-service police navy
military rough-riders governor vice-presidency presidency foreign-policy diplomacy panama-canal labor business
trusts race immigration science health religion press society friendship grief celebration war world-war-i
progressive-party death""".split())
ROLES = set("family companion host guest correspondent official colleague visitor subject adversary other".split())
PLACE_KINDS = set("""city town ranch residence building institution region state country body_of_water mountain
ship train camp battlefield other""".split())
QUOTE_KINDS = set("diary letter speech remark writing".split())
WORK_KINDS = set("book article speech review message other".split())
NGRAM = 6


def words(s):
    return re.findall(r"[a-z0-9']+", s.lower().replace("’", "'"))


def ngrams(ws, n=NGRAM):
    return {" ".join(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def norm(s):
    return " ".join(words(s))


def check_chunk(cid):
    src = json.load(open(ROOT / f"work/chunks/{cid}.json"))
    out_path = ROOT / f"data/enrich/{cid}.jsonl"
    errs, warns = [], []
    if not out_path.exists():
        return [f"missing output {out_path}"], warns
    src_days = {d["date"]: d for d in src["days"]}
    got = {}
    for i, line in enumerate(out_path.read_text().splitlines(), 1):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except Exception as e:
            errs.append(f"line {i}: bad JSON ({e})")
            continue
        dte = r.get("moved_from") or r.get("date")   # re-dated records are checked against their source day
        if dte not in src_days:
            errs.append(f"line {i}: date {dte} not in chunk")
            continue
        if dte in got:
            errs.append(f"{dte}: duplicate")
        got[dte] = r
        text = src_days[dte]["text"]
        src_grams = ngrams(words(text))
        quote_grams = set()
        for q in r.get("tr_quotes") or []:
            quote_grams |= ngrams(words(q.get("text", "")))
            if q.get("kind") not in QUOTE_KINDS:
                errs.append(f"{dte}: quote kind {q.get('kind')!r}")
            qn = norm(q.get("text", ""))
            if qn and qn not in norm(text):
                # tolerate small OCR fixes: require 80% of quote 4-grams in source
                qg = ngrams(words(q["text"]), 4)
                hit = len(qg & ngrams(words(text), 4)) / max(1, len(qg))
                if hit < 0.8:
                    errs.append(f"{dte}: quote not found in source: {q['text'][:60]!r}")
        prose = [("headline", r.get("headline") or ""), ("summary", r.get("summary") or "")]
        prose += [("event", e.get("detail") or "") for e in r.get("events") or []]
        prose += [("letter", l.get("topic") or "") for l in r.get("letters") or []]
        for field, s in prose:
            hits = (ngrams(words(s)) & src_grams) - quote_grams
            if hits:
                errs.append(f"{dte}: {field} copies source wording: {sorted(hits)[0]!r}")
        if not r.get("headline") or len(words(r["headline"])) > 10:
            errs.append(f"{dte}: headline missing or > 10 words")
        if not r.get("summary"):
            errs.append(f"{dte}: summary missing")
        elif len(words(r["summary"])) > 75:
            warns.append(f"{dte}: summary {len(words(r['summary']))} words")
        for e in r.get("events") or []:
            if e.get("action") not in ACTIONS:
                errs.append(f"{dte}: action {e.get('action')!r}")
        for t in r.get("tags") or []:
            if t not in TAGS:
                errs.append(f"{dte}: tag {t!r}")
        for p in r.get("people") or []:
            if p.get("role") not in ROLES:
                errs.append(f"{dte}: role {p.get('role')!r} for {p.get('name')}")
        for p in r.get("places") or []:
            if p.get("kind") not in PLACE_KINDS:
                errs.append(f"{dte}: place kind {p.get('kind')!r} for {p.get('name')}")
        for l in r.get("letters") or []:
            if l.get("direction") not in ("from_tr", "to_tr"):
                errs.append(f"{dte}: letter direction {l.get('direction')!r}")
        for w in r.get("works") or []:
            if w.get("kind") not in WORK_KINDS:
                errs.append(f"{dte}: work kind {w.get('kind')!r}")
        if r.get("significance") not in (1, 2, 3, 4, 5):
            errs.append(f"{dte}: significance {r.get('significance')!r}")
    merged = {d for r in (json.loads(l) for l in out_path.read_text().splitlines() if l.strip()) for d in r.get("merged_with") or []}
    missing = sorted(set(src_days) - set(got) - merged)
    if missing:
        errs.append(f"{len(missing)} days missing, first: {missing[:5]}")
    order = [json.loads(l)["date"] for l in out_path.read_text().splitlines() if l.strip()]
    if order != sorted(order):
        warns.append("lines not in date order")
    return errs, warns


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    quiet = "--quiet" in sys.argv
    if "--all" in sys.argv:
        args = [c["chunk"] for c in json.load(open(ROOT / "work/chunks/index.json"))]
    bad = 0
    for cid in args:
        errs, warns = check_chunk(cid)
        status = "OK" if not errs else f"{len(errs)} errors"
        print(f"{cid}: {status}, {len(warns)} warnings")
        if not quiet:
            for e in errs[:80]:
                print("  ERROR", e)
            for w in warns[:20]:
                print("  warn ", w)
        bad += bool(errs)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
