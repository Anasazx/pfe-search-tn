"""pfebooks.com: aggregator of Tunisian company PFE Books (public WordPress REST API).

Every source module exposes `fetch(known_ids, full, log) -> list[offer]` where an offer is a dict
with the keys documented in pfe/sources/__init__.py.
"""
import html
import re
import time

import requests

BASE = "https://pfebooks.com/wp-json/wp/v2"
HEADERS = {"User-Agent": "pfe-search-tn/0.1 (personal PFE search tool)"}
PER_PAGE = 25
FIELDS = "id,date,link,title,content,meta,job-types,job-categories"

# pfebooks level tags -> normalized levels
LEVEL_TAGS = {"bac-plus-3-licence": "licence", "bac-plus-5-ing": "ingenieur", "bac-plus-5-master": "master"}


def _get(endpoint, params, log, retries=5):
    for attempt in range(retries):
        try:
            r = requests.get(f"{BASE}/{endpoint}", headers=HEADERS, params=params, timeout=90)
            r.raise_for_status()
            return r
        except requests.RequestException as e:
            if attempt == retries - 1:
                raise
            wait = 5 * (attempt + 1)
            log(f"  retry {attempt + 1}/{retries} in {wait}s ({e.__class__.__name__})")
            time.sleep(wait)


def to_text(fragment):
    fragment = re.sub(r"<(br|/p|/li|/h\d)[^>]*>", "\n", fragment)
    fragment = re.sub(r"<li[^>]*>", "- ", fragment)
    text = html.unescape(re.sub(r"<[^>]+>", "", fragment))
    return "\n".join(line.strip() for line in text.splitlines() if line.strip())


def field(text, label_rx):
    """Join the values of every '- Label : value' line whose label matches label_rx."""
    vals = [m.group(2).strip() for m in re.finditer(r"^- ([^:\n]{2,45}?)\s*:\s*(.+)$", text, re.M)
            if re.search(label_rx, m.group(1), re.I)]
    return " | ".join(vals)


def normalize(j, types, cats):
    m = j["meta"]
    text = to_text(j["content"]["rendered"])
    tags = [types.get(t, "") for t in j["job-types"]]
    app = (m.get("_application") or "").strip()
    return {
        "id": f"pb-{j['id']}",
        "source": "pfebooks",
        "date": j["date"][:10],
        "title": html.unescape(j["title"]["rendered"]),
        "company": m.get("_company_name", ""),
        "tagline": m.get("_company_tagline", ""),
        "location": m.get("_job_location", ""),
        "remote": bool(m.get("_remote_position")) or "teletravail" in tags,
        "levels": sorted({LEVEL_TAGS[t] for t in tags if t in LEVEL_TAGS}),
        "categories": [cats.get(c, "") for c in j["job-categories"]],
        "apply": app,
        "apply_email": app if "@" in app and not app.startswith("http") else "",
        "company_website": m.get("_company_website", ""),
        "link": j["link"],
        "technologies": field(text, r"technolog|comp[ée]tences|outils|langages|connaissances|stack"),
        "formation": field(text, r"formation|dipl[ôo]me|niveau|sp[ée]cialit|profil"),
        "deadline_raw": field(text, r"date limite"),
        "duration": field(text, r"dur[ée]e"),
        "how_to_apply": field(text, r"candidature|dossier|contact|postuler"),
        "text": text,
    }


def fetch(known_ids=frozenset(), full=False, log=print):
    """Newest first; stops at the first page made only of known offers unless full=True."""
    types = {t["id"]: t["slug"] for t in _get("job-types", {"per_page": 100}, log).json()}
    cats = {c["id"]: c["slug"] for c in _get("job-categories", {"per_page": 100}, log).json()}
    offers, page = [], 1
    while True:
        r = _get("job-listings", {"per_page": PER_PAGE, "page": page, "orderby": "date",
                                  "order": "desc", "_fields": FIELDS}, log)
        batch = [normalize(j, types, cats) for j in r.json()]
        offers += batch
        total = int(r.headers.get("X-WP-TotalPages", 1))
        log(f"  pfebooks: page {page}/{total}")
        if page >= total or (not full and known_ids and all(o["id"] in known_ids for o in batch)):
            return offers
        page += 1
        time.sleep(0.5)  # be polite
