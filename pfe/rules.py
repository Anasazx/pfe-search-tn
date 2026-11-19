"""Read a company's application rules out of an offer: where to apply, how many subjects you may pick,
the reference to quote, what the email subject must contain, required documents and the deadline.
Breaking these (too many subjects, missing reference) gets applications silently discarded."""
import datetime as dt
import re

NUM = {"un": 1, "une": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5}
_N = r"(\d|un|une|deux|trois|quatre|cinq)"
_ITEM = r"(?:sujets?|r[ée]f[ée]rences?|offres?|choix|candidatures?|projets?)"
MAX_PATTERNS = [
    rf"{_N}\s+{_ITEM}\s+(?:au\s+)?maximum",
    rf"maximum\s+(?:de\s+)?{_N}\s+{_ITEM}",
    rf"jusqu[’']?\s*[àa]\s+{_N}\s+{_ITEM}",
    rf"{_N}\s+{_ITEM}\s+(?:au\s+)?plus",
]
MONTHS = {m: i for i, m in enumerate(["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
                                        "août", "septembre", "octobre", "novembre", "décembre"], 1)}
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
DOCUMENTS = {
    "Lettre de motivation": r"lettre de (motivation|candidature)",
    "Photo": r"\bphoto\b",
    "Relevés de notes": r"relev[ée]s? de notes",
    "CV Europass": r"europass",
    "Portfolio": r"portfolio",
    "Demande de stage": r"demande de stage",
}


def parse_date(text):
    text = (text or "").lower()
    m = re.search(r"(\d{1,2})(?:er)?\s+(" + "|".join(MONTHS) + r")\s+(20\d\d)", text)
    if m:
        return dt.date(int(m.group(3)), MONTHS[m.group(2)], int(m.group(1)))
    m = re.search(r"(\d{1,2})/(\d{1,2})/(20\d\d)", text)
    return dt.date(int(m.group(3)), int(m.group(2)), int(m.group(1))) if m else None


def max_subjects(text):
    found = []
    for rx in MAX_PATTERNS:
        for m in re.finditer(rx, text, re.I):
            n = m.group(1).lower()
            found.append(int(n) if n.isdigit() else NUM[n])
    return min(found) if found else None


def reference(offer):
    text = offer["text"]
    m = re.search(r"^- (?:r[ée]f[ée]rence(?: du sujet)?|r[ée]f\.?|sujet)\s*:\s*(.+)$", text, re.M | re.I)
    ref = m.group(1).strip().rstrip(".") if m else None
    if not ref:
        for rx in (r"\(r[ée]f(?:[ée]rence)?\.?\s*([^)]+)\)", r"(?i:r[ée]f[ée]rence)\s+([A-Z][\w\-/]*\d[\w\-/]*)",
                   r"(?i:sujet\s+(?:PFE\s+)?(?:n°\s*)?)(\d{1,3})\b"):
            m = re.search(rx, text)
            if m:
                ref = m.group(1).strip()
                break
    if ref and re.fullmatch(r"(?:n°\s*)?\d{1,3}", ref):
        ref = "Sujet " + ref  # a bare "10" means nothing in an email subject
    return ref


def subject_instruction(text):
    """The sentence telling you what to put in the email subject ("objet"), if any."""
    for sentence in re.split(r"(?<=[.;])\s+|\n|\s\|\s", text):
        if re.search(r"\bobjet\b", sentence, re.I):
            return sentence.strip(" -")
    return None


def extract(offer):
    text = offer["text"]
    apply_text = offer.get("how_to_apply", "") + "\n" + text
    emails = [offer["apply_email"]] if offer.get("apply_email") else []
    for e in EMAIL.findall(apply_text):
        e = e.rstrip(".")
        if e not in emails:
            emails.append(e)
    portal = offer["apply"] if offer.get("apply", "").startswith("http") else ""
    return {
        "emails": emails,
        "portal": portal,
        "max_subjects": max_subjects(apply_text),
        "reference": reference(offer),
        "subject_rule": subject_instruction(apply_text),
        # only the application instructions: "attestation de stage" in the perks is not a requirement
        "documents": [name for name, rx in DOCUMENTS.items() if re.search(rx, offer.get("how_to_apply", ""), re.I)],
        "deadline": parse_date(offer.get("deadline_raw", "")),
    }
