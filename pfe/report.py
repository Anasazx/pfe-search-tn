"""Excel tracker: ranked offers with company rules, plus your applications."""
from openpyxl import Workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

HEADER_FILL = PatternFill("solid", fgColor="1F4E78")
MATCH_COLS = [("Rank", 6), ("ID", 10), ("Score", 7), ("New", 5), ("Status", 10), ("Title", 45), ("Company", 22),
              ("Location", 18), ("Level", 16), ("Matched skills", 40), ("Gaps", 30), ("Deadline", 11),
              ("Apply (email / portal)", 34), ("Max subjects", 8), ("Slots left", 8), ("Reference", 14),
              ("Subject rule", 45), ("Documents", 22), ("Offer link", 30)]
APP_COLS = [("ID", 10), ("Company", 22), ("Title", 50), ("Status", 10), ("Sent on", 11), ("Last update", 11),
            ("Notes", 40), ("Offer link", 30)]


def _sheet(ws, cols, rows, wrap=()):
    ws.append([c for c, _ in cols])
    for cell in ws[1]:
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = HEADER_FILL
    for r in rows:
        ws.append(r)
    for i, (_, w) in enumerate(cols, 1):
        ws.column_dimensions[get_column_letter(i)].width = w
    for row in ws.iter_rows(min_row=2):
        for c in row:
            c.alignment = Alignment(vertical="top", wrap_text=cols[c.column - 1][0] in wrap)
            if isinstance(c.value, str) and c.value.startswith("http"):
                c.hyperlink = c.value
                c.font = Font(color="0563C1", underline="single")
    ws.freeze_panes = "G2" if cols is MATCH_COLS else "C2"
    ws.auto_filter.ref = ws.dimensions


def write(path, ranked, tracker):
    """ranked: list of (offer, match, rules, is_new) already sorted."""
    wb = Workbook()
    rows = []
    for i, (o, m, r, new) in enumerate(ranked, 1):
        slots = "" if r["max_subjects"] is None else max(r["max_subjects"] - tracker.used_slots(o["company"]), 0)
        rows.append([i, o["id"], m.score, "●" if new else "", tracker.status(o["id"]), o["title"], o["company"],
                     o["location"], m.level_note, ", ".join(m.matched), ", ".join(m.gaps),
                     r["deadline"].isoformat() if r["deadline"] else "", ", ".join(r["emails"]) or r["portal"],
                     r["max_subjects"] or "", slots, r["reference"] or "", r["subject_rule"] or "",
                     ", ".join(r["documents"]), o["link"]])
    ws = wb.active
    ws.title = "Offers"
    _sheet(ws, MATCH_COLS, rows, wrap=("Title", "Matched skills", "Gaps", "Subject rule"))
    for row in ws.iter_rows(min_row=2):
        s = row[2].value
        row[2].fill = PatternFill("solid", fgColor="C6EFCE" if s >= 75 else "FFEB9C" if s >= 55 else "FFC7CE")

    apps = [[oid, a["company"], a["title"], a["status"], a.get("sent_on", ""), a["history"][-1]["date"],
             "; ".join(h["note"] for h in a["history"] if h.get("note")), a["link"]]
            for oid, a in sorted(tracker.apps.items(), key=lambda x: x[1].get("sent_on", ""), reverse=True)]
    _sheet(wb.create_sheet("Applications"), APP_COLS, apps, wrap=("Title", "Notes"))
    path.parent.mkdir(parents=True, exist_ok=True)
    wb.save(path)
    return path
