---
description: Write a tailored application for one or more offers (IDs), respecting each company's rules
argument-hint: <offer-id> [offer-id ...]
---

Offers: $ARGUMENTS

Read `docs/email-guide.md` first, along with `me/profile.yaml` and the CV in `me/`.

For each company among the given offers:

1. Run `python -m pfe show <ids>` and read the full text and the "Application rules" block.
2. **Check eligibility and limits before writing anything:**
   - Level: if the offer says "X only ✖", tell the student and ask before continuing.
   - Max subjects vs "Already applied at": if the cap would be exceeded, stop and ask which subjects to keep.
   - Expired or portal-only: no email. For portal offers, write a short motivation paragraph (80–120 words) they can paste into the form, and give the portal link.
3. Write the email following the guide: subject per the company's rule, the offer's missions tied to real CV facts, honest about gaps, 150–250 words, in French.
4. Save the body to `output/bodies/<company-slug>.txt`, then run:
   `python -m pfe draft <ids> --subject "<subject>" --body-file output/bodies/<company-slug>.txt`
5. Show the student the subject and body, the .eml path, and anything else required (cover letter, photo, Europass).

When the student confirms they sent it, run `python -m pfe track <ids> applied`.
Never send an email yourself, even if an email tool is available. The student reviews and sends.
