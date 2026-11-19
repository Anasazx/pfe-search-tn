---
description: Build me/profile.yaml from the student's CV
---

Build the student's profile so ranking and emails work.

1. Run `python -m pfe init` (creates `me/profile.yaml` from the example if missing).
2. Find the CV: a PDF in `me/`. If there is none, ask the student to put their CV PDF in `me/` and stop.
3. Read the CV fully. Then ask the student, in one message, only what the CV doesn't answer:
   - level: licence, ingenieur or master (and which year)
   - preferred cities (or "anywhere")
   - domains they want (informatique-ia-data, dev-web-mobile-design-ux-ui, systemes-reseaux-cloud, industrie-ing-btp, business-marketing-rh, durabilite-technologie-verte)
   - how they want to be introduced (e.g. « Étudiante en 3e année du cycle ingénieur en génie logiciel à l’ENIT »)
4. Write `me/profile.yaml` following `profile.example.yaml`:
   - `skills`: only skills present in the CV. Use catalog names from `pfe/skills.py` where they exist. Weight 3 = used in internships or major projects, 2 = solid, 1 = familiar.
   - `highlights`: one per internship or significant project, written as a French clause that follows « Ce sujet correspond directement à mon parcours : … ». Use concrete facts from the CV (what, which stack, result or award). Tag each with the skills it proves.
   - `cv`: the PDF's filename.
5. Run `python -m pfe rank --top 10` and show the student the top matches as a sanity check. If the ranking looks wrong (for example, a backend student getting design offers), adjust weights or categories and rerun.

Never invent anything that is not in the CV or the student's answers.
