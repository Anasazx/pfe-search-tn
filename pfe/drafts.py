"""Email drafts: a no-AI French template from the profile, and .eml files with the CV attached
(double-click to open as an unsent draft in Apple Mail / Outlook / Thunderbird)."""
import re
from email.message import EmailMessage
from pathlib import Path

SKIP_IN_LIST = {"ai", "git", "full-stack", "legacy modernization"}
DISPLAY = {"llm": "l’intégration de LLM", "rest api": "les API REST", "computer vision": "la vision par ordinateur",
           "rag": "les architectures RAG", "machine learning": "le machine learning", "iot": "l’IoT"}


def subject_for(offers, rules_list, profile):
    """Reference(s) first, since companies sort their inbox by reference."""
    refs = [r["reference"] for r in rules_list if r["reference"]]
    title = offers[0]["title"] if len(offers) == 1 else " / ".join(o["title"][:50] for o in offers)
    parts = ([", ".join(refs)] if refs else []) + ["Candidature PFE", title, profile.name]
    return " – ".join(parts)


def template_body(offers, matches, profile):
    """Deterministic draft for when no AI is available. /apply in Claude Code writes a better one."""
    matched = []
    for m in matches:
        matched += [s for s in m.matched if s not in matched]
    lowered = {s.lower() for s in matched}
    ranked = sorted(profile.highlights, key=lambda h: len({s.lower() for s in h.get("skills", [])} & lowered),
                    reverse=True)
    points = [h["text"] for h in ranked if {s.lower() for s in h.get("skills", [])} & lowered][:2]
    points = points or [h["text"] for h in profile.highlights[:1]]

    shown = [DISPLAY.get(s.lower(), s) for s in matched if s.lower() not in SKIP_IN_LIST][:7]
    skills = (", ".join(shown[:-1]) + " et " + shown[-1]) if len(shown) > 1 else "".join(shown)

    company = offers[0]["company"]
    if len(offers) == 1:
        target = f"le sujet de PFE « {offers[0]['title']} » proposé par {company}"
    else:
        target = f"les sujets de PFE suivants proposés par {company} : " + "; ".join(f"« {o['title']} »" for o in offers)

    paras = ["Madame, Monsieur,", f"{profile.intro}, je vous adresse ma candidature pour {target}."]
    if points:
        paras.append(f"Ce sujet correspond directement à mon parcours : {points[0]}."
                     + (f" Par ailleurs, {points[1]}." if len(points) > 1 else ""))
    if skills:
        paras.append(f"Je maîtrise notamment {skills}, des compétences que je souhaite mettre "
                     "au service de votre équipe sur ce projet.")
    paras += ["Vous trouverez mon CV en pièce jointe. Je reste à votre disposition pour un entretien.",
              "Cordialement,", profile.signature]
    return "\n\n".join(paras)


def write_eml(path, sender, to, subject, body, attachments=()):
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(to)
    msg["Subject"] = subject
    msg["X-Unsent"] = "1"  # open as a draft, not a received message
    msg.set_content(body)
    for a in attachments:
        a = Path(a)
        msg.add_attachment(a.read_bytes(), maintype="application",
                           subtype="pdf" if a.suffix.lower() == ".pdf" else "octet-stream", filename=a.name)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(bytes(msg))
    return path


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:40]
