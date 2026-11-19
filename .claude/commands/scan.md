---
description: Fetch new PFE offers, rank them, and brief the student on what to act on
---

1. Run `python -m pfe scrape`, then `python -m pfe rank --top 40`.
2. Brief the student in a short table: the best offers they haven't applied to, split into
   - **Urgent:** deadline within 7 days.
   - **New since last scan** (● in the output).
   - **Best of the rest.**
   For each: ID, company, title, score, and how to apply (email or portal).
3. Flag company caps: run `python -m pfe show <id>` for the top candidates and mention any company where the student has few subject slots left, so they choose deliberately.
4. Point out patterns worth knowing, e.g. "8 of your top 20 ask for Docker, which isn't on your profile" or "Next has 8 matching subjects but takes portal applications only".
5. End with a recommendation: which 3–5 offers to `/apply` to next, and why.
