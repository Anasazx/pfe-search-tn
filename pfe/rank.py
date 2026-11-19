"""Score an offer against a profile: skills 65 + level 20 + domain 10 + location 5 = 100."""
import re
from dataclasses import dataclass

from . import skills as skill_catalog

LEVEL_RX = {
    "licence": r"licence|bac\s*\+\s*3|technicien",
    "ingenieur": r"ing[ée]nieur|cycle ing",
    "master": r"master|mast[èe]re",
}
LEVEL_LABEL = {"licence": "Licence", "ingenieur": "Ingénieur", "master": "Master"}


@dataclass
class Match:
    score: int
    matched: list
    gaps: list
    levels: set
    level_ok: object     # True / False / None (offer doesn't say)

    @property
    def level_note(self):
        if self.level_ok is None:
            return "Unspecified"
        names = "/".join(LEVEL_LABEL[lv] for lv in sorted(self.levels))
        return f"{names} ✔" if self.level_ok else f"{names} only ✖"


def offer_levels(offer):
    found = set(offer.get("levels", []))
    text = (offer.get("formation", "") + " " + offer["title"]).lower()
    for lv, rx in LEVEL_RX.items():
        if re.search(rx, text):
            found.add(lv)
    if re.search(r"bac\s*\+\s*5", text):
        found |= {"ingenieur", "master"}
    return found


def score(offer, profile):
    tech = offer.get("technologies", "").lower()
    body = (offer["title"] + "\n" + offer["text"]).lower()
    pts, matched = 0.0, []
    for s in profile.skills:
        if s.rx.search(tech):
            matched.append(s.name); pts += s.weight * 1.5   # explicitly required
        elif s.rx.search(body):
            matched.append(s.name); pts += s.weight * 0.6   # mentioned somewhere
    total = min(pts / profile.saturation, 1.0) * 65

    levels = offer_levels(offer)
    level_ok = None if not levels else profile.level in levels
    total += {None: 12, True: 20, False: 0}[level_ok]

    if not profile.categories or set(offer.get("categories", [])) & set(profile.categories):
        total += 10
    loc = offer.get("location", "").lower()
    if not profile.locations or offer.get("remote") or any(l.lower() in loc for l in profile.locations):
        total += 5

    tokens = [t.strip(" .") for t in re.split(r",|/|;|\||\n| et |\(|\)", offer.get("technologies", ""))]
    gaps = [t for t in tokens if t and len(t) < 30 and not any(s.rx.search(t) for s in profile.skills)]
    gaps = [t for t in gaps if skill_catalog.any_known(t) or t[:1].isupper()][:8]
    return Match(round(total), matched, gaps, levels, level_ok)
