"""Parsing tests built from real offer phrasings. Run: python -m unittest discover tests"""
import datetime as dt
import tempfile
import unittest
from pathlib import Path

from pfe import drafts, rank, rules, tracker
from pfe.profile import load


def offer(text="", **kw):
    base = {"id": "pb-1", "source": "pfebooks", "date": "2026-11-18", "title": "Sujet test", "company": "Acme",
            "location": "Tunis, Tunisie", "remote": False, "levels": [], "categories": ["informatique-ia-data"],
            "apply": "", "apply_email": "", "link": "https://example.com/1", "technologies": "", "formation": "",
            "deadline_raw": "", "how_to_apply": "", "text": text}
    base.update(kw)
    return base


PROFILE_YAML = """
name: Test Student
email: t@example.com
level: licence
intro: Étudiant en Licence
categories: [informatique-ia-data]
skills:
  - {name: Java, weight: 3}
  - {name: Angular, weight: 3}
  - {name: JavaScript, weight: 1}
highlights:
  - {skills: [Java], text: j’ai développé une API Spring Boot}
"""


class MaxSubjects(unittest.TestCase):
    def test_phrasings(self):
        cases = {
            "Chaque étudiant peut choisir 2 références maximum : toute référence supplémentaire...": 2,
            "puis candidature à 3 sujets au maximum": 3,
            "(trois offres maximum par candidat)": 3,
            "Chaque étudiant peut choisir jusqu’à deux sujets ; toute candidature dépassant": 2,
            "en choisissant au maximum 3 sujets": 3,
            "Envoyez votre CV à rh@acme.tn": None,
        }
        for text, expected in cases.items():
            self.assertEqual(rules.max_subjects(text), expected, text)


class Reference(unittest.TestCase):
    def test_field_line(self):
        self.assertEqual(rules.reference(offer("- Référence du sujet : WB-001\n")), "WB-001")

    def test_parenthesised(self):
        self.assertEqual(rules.reference(offer("le sujet de PFE X (réf. PRX-2027-19). Une plateforme")), "PRX-2027-19")
        self.assertEqual(rules.reference(offer("thématique Dev (référence SE04_2026). Le sujet")), "SE04_2026")

    def test_bare_number_gets_label(self):
        self.assertEqual(rules.reference(offer("propose à Tunis le sujet PFE 18 : Conception")), "Sujet 18")
        self.assertEqual(rules.reference(offer("- Sujet : n° 6\n")), "Sujet n° 6")


class Extract(unittest.TestCase):
    def test_emails_deduped_and_found_in_text(self):
        o = offer("Candidature : contact@acme.tn ou contact@acme.tn.", how_to_apply="contact@acme.tn")
        self.assertEqual(rules.extract(o)["emails"], ["contact@acme.tn"])

    def test_subject_rule_strips_other_fields(self):
        o = offer(how_to_apply="22 novembre 2026 | envoyer à rh@x.tn en indiquant la référence dans l’objet du mail")
        self.assertTrue(rules.extract(o)["subject_rule"].startswith("envoyer à rh@x.tn"))

    def test_documents_only_from_instructions(self):
        o = offer("- Avantages : une attestation de stage\n- Dossier : lettre de motivation et photo",
                  how_to_apply="lettre de motivation et photo")
        self.assertEqual(rules.extract(o)["documents"], ["Lettre de motivation", "Photo"])

    def test_dates(self):
        self.assertEqual(rules.parse_date("Date limite : 1er décembre 2026"), dt.date(2026, 12, 1))
        self.assertEqual(rules.parse_date("22/11/2026"), dt.date(2026, 11, 22))
        self.assertIsNone(rules.parse_date("dès que possible"))


class Ranking(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        p = Path(self.tmp.name) / "profile.yaml"
        p.write_text(PROFILE_YAML)
        self.profile = load(p)

    def tearDown(self):
        self.tmp.cleanup()

    def test_levels(self):
        self.assertEqual(rank.offer_levels(offer(formation="licence, master ou diplôme d’ingénieur")),
                         {"licence", "master", "ingenieur"})
        self.assertEqual(rank.offer_levels(offer(formation="profil ingénieur")), {"ingenieur"})
        self.assertEqual(rank.offer_levels(offer(formation="Bac+5")), {"ingenieur", "master"})

    def test_level_mismatch_scores_lower(self):
        ok = rank.score(offer(technologies="Java, Angular", formation="Licence"), self.profile)
        ko = rank.score(offer(technologies="Java, Angular", formation="Cycle ingénieur"), self.profile)
        self.assertTrue(ok.level_ok)
        self.assertFalse(ko.level_ok)
        self.assertGreater(ok.score, ko.score)

    def test_javascript_is_not_java(self):
        m = rank.score(offer(technologies="JavaScript"), self.profile)
        self.assertEqual(m.matched, ["JavaScript"])

    def test_template_cites_matching_highlight(self):
        o = offer(technologies="Java")
        body = drafts.template_body([o], [rank.score(o, self.profile)], self.profile)
        self.assertIn("API Spring Boot", body)
        self.assertIn("Test Student", body)


class Tracking(unittest.TestCase):
    def test_slots_and_followups(self):
        with tempfile.TemporaryDirectory() as d:
            t = tracker.Tracker(Path(d) / "apps.json")
            t.set(offer(), "applied", today=dt.date(2026, 11, 1))
            t.set(offer(id="pb-2"), "skip", today=dt.date(2026, 11, 1))
            self.assertEqual(t.used_slots("Acme"), 1)
            self.assertEqual(len(t.due_followups(today=dt.date(2026, 11, 10))), 0)
            self.assertEqual(len(t.due_followups(today=dt.date(2026, 11, 20))), 1)
            t.set(offer(), "applied", note="relance", today=dt.date(2026, 11, 20))
            self.assertEqual(len(t.due_followups(today=dt.date(2026, 11, 25))), 0)  # relance resets the clock


if __name__ == "__main__":
    unittest.main()
