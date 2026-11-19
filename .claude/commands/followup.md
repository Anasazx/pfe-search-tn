---
description: Draft polite follow-ups for applications with no answer after 14 days
---

1. Run `python -m pfe followups`. If nothing is due, say so and stop.
2. Read `docs/email-guide.md` (Follow-ups section). Group the due applications by company: one follow-up per company, even if several subjects were sent.
3. For each company, write a 3–4 sentence relance in French: « Relance – » plus the original subject; the reference(s) and the date sent; continued interest; one new fact if there is one (e.g. a project finished since). Save it to `output/bodies/relance-<company-slug>.txt` and run
   `python -m pfe draft <ids> --subject "Relance – <original subject>" --body-file output/bodies/relance-<company-slug>.txt`
4. List the drafts for the student. When they confirm sending, record it with `python -m pfe track <ids> applied --note "relance envoyée"`. This resets the 14-day clock. If a company still doesn't answer after the relance, suggest `no-reply`.
