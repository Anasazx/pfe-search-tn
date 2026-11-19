"""Application tracker (data/applications.json): what you sent, when, and what came back."""
import datetime as dt
import json
from pathlib import Path

STATUSES = ("applied", "interview", "offer", "accepted", "rejected", "no-reply", "skip")
OPEN = {"applied"}            # still waiting on the company
FOLLOW_UP_DAYS = 14


class Tracker:
    def __init__(self, path):
        self.path = Path(path)
        self.apps = json.loads(self.path.read_text()) if self.path.exists() else {}

    def save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.path.write_text(json.dumps(self.apps, ensure_ascii=False, indent=1))

    def set(self, offer, status, note="", today=None):
        if status not in STATUSES:
            raise SystemExit(f"status must be one of {STATUSES}")
        today = (today or dt.date.today()).isoformat()
        app = self.apps.setdefault(offer["id"], {"company": offer["company"], "title": offer["title"],
                                                 "link": offer["link"], "history": []})
        if status == "applied" and not app.get("sent_on"):
            app["sent_on"] = today
        app["status"] = status
        app["history"].append({"date": today, "status": status, **({"note": note} if note else {})})
        return app

    def status(self, offer_id):
        return self.apps.get(offer_id, {}).get("status", "")

    def used_slots(self, company):
        """Subjects already applied to at this company (counts against its max-subjects rule)."""
        return sum(1 for a in self.apps.values() if a["company"] == company and a["status"] != "skip")

    def due_followups(self, today=None, days=FOLLOW_UP_DAYS):
        today = today or dt.date.today()
        due = []
        for oid, a in self.apps.items():
            if a["status"] in OPEN and a.get("sent_on"):
                last = max(dt.date.fromisoformat(h["date"]) for h in a["history"])
                if (today - last).days >= days:
                    due.append((oid, a, (today - dt.date.fromisoformat(a["sent_on"])).days))
        return sorted(due, key=lambda x: -x[2])
