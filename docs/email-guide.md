# Writing PFE application emails (Tunisia)

Rules every email written by `/apply` or `/followup` follows.

## The company's rules come first
Run `python -m pfe show <id>` and obey its "Application rules" block exactly:
- **Subject line:** if the offer dictates a subject format (PwC: « Candidature PFE – Réf | Practice | École | Spécialité | Nom »), copy it to the letter. Otherwise start with the reference (`SE04_2026 – Candidature PFE – <titre> – <nom>`).
- **Max subjects:** never exceed it, and count subjects already sent (`Already applied at …`). Some companies disqualify over-limit candidates (Wevioo, Valeo).
- **One email per company.** When the company allows several subjects, cover them in one email unless it asks for one message per subject (OneTech).
- **Documents:** if a cover letter, photo or Europass CV is required, say so to the student; the email alone is not enough.
- **Portal-only offers** (Proxym, Sofrecom, Next…) get no email. Give the student the portal link and a short motivation text to paste.

## Language and tone
- French by default, formal register: « Madame, Monsieur, » … « Cordialement, ». Write in English only if the offer is entirely in English *and* the company is international.
- 150–250 words. Recruiters read dozens of these.
- Open with the profile's `intro`, then name the subject (and reference) in the first sentence.

## Content: specific, true, verifiable
- Tie 2–3 of the offer's **missions** to concrete facts from the CV/profile: what was built, with which stack, what result. Use the offer's own vocabulary where it is honest.
- **Never invent** experience, tools, results or dates. Only use what is in `me/profile.yaml`, the CV in `me/`, or what the student told you.
- **Name the gap honestly** when the offer requires something the student lacks (e.g. Qdrant, Kubernetes, .NET): one sentence presenting it as what they want to learn, backed by the closest real experience.
- No generic filler (« dynamique, motivé, rigoureux »), no copying the offer text back, no flattery of the company.
- Close with « Vous trouverez mon CV en pièce jointe. Je reste à votre disposition pour un entretien. » and the signature from the profile.

## Follow-ups (relances)
- After ~14 days without an answer. One follow-up only.
- 3–4 sentences, same subject prefixed with « Relance – », restate the reference, confirm continued interest, re-attach the CV.
