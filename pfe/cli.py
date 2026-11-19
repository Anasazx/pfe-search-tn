"""pfe: find, rank and apply to Tunisian PFE offers.  Run `python -m pfe -h`."""
import argparse
import datetime as dt
import json
import shutil
import sys
from pathlib import Path

from . import drafts, profile as profile_mod, rank, report, rules
from .sources import SOURCES
from .tracker import STATUSES, Tracker

ROOT = Path(__file__).resolve().parents[1]
ME = ROOT / "me"
DATA = ROOT / "data"
OUT = ROOT / "output"
OFFERS = DATA / "offers.json"
SEEN = DATA / "seen.json"


def load_offers():
    if not OFFERS.exists():
        sys.exit("No offers yet. Run `python -m pfe scrape` first.")
    return {o["id"]: o for o in json.loads(OFFERS.read_text())}


def get_offer(offers, oid):
    if oid not in offers and f"pb-{oid}" in offers:
        oid = f"pb-{oid}"
    if oid not in offers:
        sys.exit(f"Unknown offer id {oid!r}. IDs are in the ID column of the report / `pfe rank` output.")
    return offers[oid]


def tracker():
    return Tracker(DATA / "applications.json")


# ---------------------------------------------------------------- commands
def cmd_init(args):
    ME.mkdir(exist_ok=True)
    target = ME / "profile.yaml"
    if target.exists():
        print(f"{target} already exists; leaving it alone.")
    else:
        shutil.copy(ROOT / "profile.example.yaml", target)
        print(f"Created {target}.")
    print("Next: put your CV PDF in me/, fill in me/profile.yaml (or run /setup in Claude Code), "
          "then `python -m pfe scrape` and `python -m pfe rank`.")


def cmd_scrape(args):
    existing = {o["id"]: o for o in json.loads(OFFERS.read_text())} if OFFERS.exists() and not args.full else {}
    added = 0
    for name, fetch in SOURCES.items():
        print(f"Fetching {name}{' (full)' if args.full else ''}...")
        known = {oid for oid, o in existing.items() if o["source"] == name}
        for o in fetch(known_ids=known, full=args.full, log=print):
            added += o["id"] not in existing
            existing[o["id"]] = o
    DATA.mkdir(exist_ok=True)
    OFFERS.write_text(json.dumps(sorted(existing.values(), key=lambda o: o["date"], reverse=True),
                                 ensure_ascii=False, indent=1))
    print(f"{len(existing)} offers saved ({added} new) -> {OFFERS}")


def ranked_offers(prof, offers, include_mismatch):
    today = dt.date.today()
    seen = set(json.loads(SEEN.read_text())) if SEEN.exists() else set()
    out = []
    for o in offers.values():
        r = rules.extract(o)
        if r["deadline"] and r["deadline"] < today:
            continue
        m = rank.score(o, prof)
        if m.level_ok is False and not include_mismatch:
            continue
        out.append((o, m, r, bool(seen) and o["id"] not in seen))
    out.sort(key=lambda x: (x[1].score, x[0]["date"]), reverse=True)
    return out, seen


def cmd_rank(args):
    prof = profile_mod.load(ME / "profile.yaml")
    offers = load_offers()
    ranked, seen = ranked_offers(prof, offers, args.all_levels)
    t = tracker()
    path = report.write(OUT / "pfe_offers.xlsx", ranked, t)
    SEEN.write_text(json.dumps(sorted(set(offers) | seen)))

    shown = [x for x in ranked if not (args.new and not x[3]) and t.status(x[0]["id"]) in ("", None)][:args.top]
    print(f"{'ID':10} {'Sc':>3} {'':1} {'Deadline':10} {'Company':22} Title")
    for o, m, r, new in shown:
        dl = r["deadline"].isoformat() if r["deadline"] else ""
        print(f"{o['id']:10} {m.score:3d} {'●' if new else ' '} {dl:10} {o['company'][:22]:22} {o['title'][:70]}")
    soon = [x for x in ranked if x[2]["deadline"] and (x[2]["deadline"] - dt.date.today()).days <= 7 and x[1].score >= 60
            and not t.status(x[0]["id"])]
    if soon:
        print(f"\n⚠ {len(soon)} good match{'es' if len(soon) > 1 else ''} closing within 7 days: "
              + ", ".join(f"{o['company']} ({r['deadline']:%d/%m})" for o, _, r, _ in soon[:6]))
    print(f"\n{len(ranked)} eligible offers ranked -> {path}  (● = new since last rank)")


def cmd_show(args):
    offers = load_offers()
    prof = profile_mod.load(ME / "profile.yaml") if (ME / "profile.yaml").exists() else None
    t = tracker()
    for oid in args.ids:
        o = get_offer(offers, oid)
        r = rules.extract(o)
        print(f"=== {o['id']} | {o['company']} | {o['title']}")
        print(f"Location: {o['location']}   Published: {o['date']}   Link: {o['link']}")
        if prof:
            m = rank.score(o, prof)
            print(f"Score: {m.score}   Level: {m.level_note}   Matched: {', '.join(m.matched)}")
            print(f"Gaps: {', '.join(m.gaps) or '-'}")
        print("--- Application rules")
        print(f"Apply via: {', '.join(r['emails']) or r['portal'] or 'see text'}")
        print(f"Deadline: {r['deadline'] or 'not stated'}   Reference: {r['reference'] or '-'}")
        used = t.used_slots(o["company"])
        print(f"Max subjects: {r['max_subjects'] or 'not stated'}   Already applied at {o['company']}: {used}")
        print(f"Subject rule: {r['subject_rule'] or '-'}")
        print(f"Documents: {', '.join(r['documents']) or 'CV'}   Status: {t.status(o['id']) or 'not applied'}")
        print("--- Offer text")
        print(o["text"])
        print()


def cmd_draft(args):
    prof = profile_mod.load(ME / "profile.yaml")
    offers = load_offers()
    chosen = [get_offer(offers, i) for i in args.ids]
    companies = {o["company"] for o in chosen}
    if len(companies) > 1:
        sys.exit("One email per company: pass ids from the same company only.")
    company = companies.pop()
    rl = [rules.extract(o) for o in chosen]
    t = tracker()

    caps = [r["max_subjects"] for r in rl if r["max_subjects"]]
    if caps and t.used_slots(company) + len(chosen) > min(caps):
        print(f"⚠ {company} allows {min(caps)} subject(s); you'd be at {t.used_slots(company) + len(chosen)}. "
              "Over the cap usually means disqualification.")
    to = [args.to] if args.to else next((r["emails"] for r in rl if r["emails"]), [])
    if not to:
        sys.exit(f"No application email found ({rl[0]['portal'] or 'see offer text'}). Apply on the portal, "
                 "or pass --to.")
    subject = args.subject or drafts.subject_for(chosen, rl, prof)
    if args.body_file:
        body = Path(args.body_file).read_text().strip()
    else:
        body = drafts.template_body(chosen, [rank.score(o, prof) for o in chosen], prof)
    attachments = [prof.cv] if prof.cv and prof.cv.exists() else []
    if not attachments:
        print("⚠ No CV attached: set `cv:` in me/profile.yaml to your PDF (relative to me/).")
    path = OUT / "eml" / f"{drafts.slug(company)}_{'_'.join(o['id'] for o in chosen)}.eml"
    drafts.write_eml(path, f"{prof.name} <{prof.email}>", to, subject, body, attachments)

    print(f"Draft -> {path}\nTo: {', '.join(to)}\nSubject: {subject}")
    for r in rl:
        if r["subject_rule"]:
            print(f"Check the subject against the company rule: {r['subject_rule']}")
        if set(r["documents"]) - {"CV Europass"}:
            print(f"Also required: {', '.join(r['documents'])}")
    print("Open it, review, send, then: python -m pfe track " + " ".join(o["id"] for o in chosen) + " applied")


def cmd_track(args):
    t = tracker()
    if not args.ids:
        for oid, a in sorted(t.apps.items(), key=lambda x: x[1].get("sent_on", ""), reverse=True):
            print(f"{oid:10} {a['status']:10} {a.get('sent_on', ''):10} {a['company'][:22]:22} {a['title'][:60]}")
        print(f"{len(t.apps)} applications") if t.apps else print("No applications tracked yet.")
        return
    offers = load_offers()
    for oid in args.ids:
        o = get_offer(offers, oid)
        t.set(o, args.status, args.note)
        print(f"{o['id']} {o['company']} -> {args.status}")
    t.save()


def cmd_followups(args):
    due = tracker().due_followups(days=args.days)
    if not due:
        print(f"Nothing to follow up (no open application older than {args.days} days without news).")
    for oid, a, age in due:
        print(f"{oid:10} sent {a['sent_on']} ({age} days)  {a['company']} | {a['title'][:60]}")


def main(argv=None):
    p = argparse.ArgumentParser(prog="pfe", description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)
    sub.add_parser("init", help="create me/profile.yaml from the example").set_defaults(fn=cmd_init)

    s = sub.add_parser("scrape", help="fetch new offers from every source")
    s.add_argument("--full", action="store_true", help="re-download everything instead of only new offers")
    s.set_defaults(fn=cmd_scrape)

    s = sub.add_parser("rank", help="score offers against your profile and write output/pfe_offers.xlsx")
    s.add_argument("--top", type=int, default=25)
    s.add_argument("--new", action="store_true", help="only print offers new since the last rank")
    s.add_argument("--all-levels", action="store_true", help="keep offers reserved for other levels")
    s.set_defaults(fn=cmd_rank)

    s = sub.add_parser("show", help="full offer text + extracted application rules")
    s.add_argument("ids", nargs="+")
    s.set_defaults(fn=cmd_show)

    s = sub.add_parser("draft", help="write an .eml draft (CV attached) for one or more subjects of ONE company")
    s.add_argument("ids", nargs="+")
    s.add_argument("--subject")
    s.add_argument("--body-file", help="email body to use instead of the template (e.g. written by /apply)")
    s.add_argument("--to", help="override recipient")
    s.set_defaults(fn=cmd_draft)

    s = sub.add_parser("track", help="record a status, or list applications when no ids are given")
    s.add_argument("ids", nargs="*")
    s.add_argument("status", nargs="?", choices=STATUSES)
    s.add_argument("--note", default="")
    s.set_defaults(fn=cmd_track)

    s = sub.add_parser("followups", help="applications with no news for N days")
    s.add_argument("--days", type=int, default=14)
    s.set_defaults(fn=cmd_followups)

    args = p.parse_args(argv)
    if args.cmd == "track" and args.ids and not args.status:
        # argparse puts a trailing status into ids; split it back out
        if args.ids[-1] in STATUSES:
            args.status = args.ids.pop()
        else:
            p.error(f"track: give a status ({', '.join(STATUSES)})")
    args.fn(args)
