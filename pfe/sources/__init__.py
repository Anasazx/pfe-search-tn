"""Offer sources. To add a job board, write a module with a `fetch(known_ids, full, log)` function
returning a list of offer dicts, then register it in SOURCES.

Offer keys (strings unless noted; use "" / [] when unknown):
  id            unique and stable, prefixed by source ("pb-11523")
  source, date (YYYY-MM-DD), title, company, tagline, location, remote (bool)
  levels        list of "licence" | "ingenieur" | "master" the offer is tagged for
  categories    list of domain slugs
  apply         application URL or email; apply_email: the email if applying by email
  company_website, link (offer page)
  technologies, formation, deadline_raw, duration, how_to_apply   extracted fields
  text          full offer text (plain)
"""
from . import pfebooks

SOURCES = {"pfebooks": pfebooks.fetch}
