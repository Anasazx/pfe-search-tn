---
description: Interview prep for an offer the student applied to
argument-hint: <offer-id>
---

Offer: $ARGUMENTS

1. Run `python -m pfe show $ARGUMENTS`, and read `me/profile.yaml` and the CV.
2. Research the company briefly (website from the offer, WebSearch if available): what they sell, their clients, their tech, and recent news.
3. Write `output/interview/<company-slug>-<id>.md` containing:
   - **The subject in plain words:** the problem, the likely architecture, and what a good 4–6 month deliverable looks like.
   - **Your pitch (2 minutes, in French):** who you are, then the 2 CV experiences closest to this subject, then why this subject.
   - **Technical questions likely for this subject**, with short model answers grounded in the student's real experience. Cover the stack in the offer, and the gaps especially (e.g. "Qu’est-ce que le RAG ?", "Différence entre JWT et session", "Comment fonctionne l’injection de dépendances dans Spring ?").
   - **HR questions** typical in Tunisian PFE interviews (« Présentez-vous », « Pourquoi notre entreprise ? », « Vos disponibilités et la durée du stage ? », « Avez-vous un binôme ? »), with suggested answers.
   - **Questions to ask them:** supervision, team, stack, hiring after the PFE.
   - **Prep checklist for the 48 hours before**, including a one-evening mini-project to cover the biggest gap.
4. After the interview, record the outcome: `python -m pfe track <id> interview --note "..."` (or rejected / offer).
