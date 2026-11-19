"""Candidate profile (me/profile.yaml): who you are, what you know, and the proof points emails cite."""
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from . import skills as skill_catalog

LEVELS = ("licence", "ingenieur", "master")


@dataclass
class Skill:
    name: str
    weight: float
    rx: object


@dataclass
class Profile:
    name: str
    email: str
    phone: str
    links: list
    intro: str           # first sentence of every email, e.g. "Étudiant en dernière année de Licence ..."
    level: str           # licence | ingenieur | master
    cv: Path
    skills: list
    highlights: list     # [{"skills": [...], "text": "..."}]
    categories: list = field(default_factory=list)
    locations: list = field(default_factory=list)

    @property
    def signature(self):
        lines = [self.name, " | ".join(x for x in (self.phone, self.email) if x)]
        if self.links:
            lines.append(" | ".join(self.links))
        return "\n".join(lines)

    @property
    def saturation(self):
        """Skill points that count as a perfect overlap (half of everything you know)."""
        return max(10.0, 0.5 * sum(s.weight for s in self.skills))


def load(path):
    path = Path(path)
    if not path.exists():
        raise SystemExit(f"No profile at {path}. Run `python -m pfe init`, then fill it in (or run /setup in Claude Code).")
    d = yaml.safe_load(path.read_text()) or {}
    level = str(d.get("level", "")).lower()
    if level not in LEVELS:
        raise SystemExit(f"profile.yaml: level must be one of {LEVELS}, got {level!r}")
    parsed = []
    for s in d.get("skills", []):
        s = {"name": s} if isinstance(s, str) else s
        parsed.append(Skill(s["name"], float(s.get("weight", 2)), skill_catalog.pattern(s["name"], s.get("match"))))
    return Profile(
        name=d.get("name", ""), email=d.get("email", ""), phone=d.get("phone", ""),
        links=d.get("links", []) or [], intro=d.get("intro", "").strip(), level=level,
        cv=(path.parent / d["cv"]) if d.get("cv") else None,
        skills=parsed, highlights=d.get("highlights", []) or [],
        categories=d.get("categories", []) or [], locations=d.get("locations", []) or [],
    )
