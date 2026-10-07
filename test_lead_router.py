import unittest

from lead_router import decide, normalize, process, score


class LeadRouterTests(unittest.TestCase):
    def test_normalizes_email_phone_and_country(self):
        lead = normalize(
            {
                "name": "  Ana Silva ",
                "email": " ANA@EXAMPLE.COM ",
                "phone": "+55 (48) 99999-0000",
                "country": "br",
            }
        )
        self.assertEqual(lead["name"], "Ana Silva")
        self.assertEqual(lead["email"], "ana@example.com")
        self.assertEqual(lead["phone"], "5548999990000")
        self.assertEqual(lead["country"], "BR")

    def test_scores_high_intent_lead(self):
        value = score(
            normalize(
                {
                    "name": "Buyer",
                    "email": "buyer@example.com",
                    "budget": 12000,
                    "company_size": 60,
                    "service_interest": "AI agent CRM automation",
                    "message": "Need API webhook workflow and WhatsApp integration",
                    "source": "referral",
                }
            )
        )
        self.assertGreaterEqual(value, 90)

    def test_routes_latam_deterministically(self):
        first = decide(
            {
                "name": "Maria",
                "email": "maria@example.com",
                "country": "BR",
                "budget": 5000,
                "company_size": 12,
                "service_interest": "workflow automation",
            }
        )
        second = decide(
            {
                "name": "Maria Changed",
                "email": "MARIA@example.com",
                "country": "BR",
                "budget": 5000,
                "company_size": 12,
                "service_interest": "workflow automation",
            }
        )
        self.assertEqual(first.region, "latam")
        self.assertEqual(first.owner, second.owner)
        self.assertEqual(first.fingerprint, second.fingerprint)

    def test_deduplicates_and_rejects_invalid(self):
        leads = [
            {"name": "A", "email": "a@example.com", "country": "US"},
            {"name": "A2", "email": "A@example.com", "country": "US"},
            {"name": "Bad", "email": "not-an-email", "country": "CA"},
        ]
        result = process(leads)
        self.assertEqual(result["stats"]["input"], 3)
        self.assertEqual(result["stats"]["accepted"], 1)
        self.assertEqual(result["stats"]["duplicates"], 1)
        self.assertEqual(result["stats"]["invalid"], 1)

    def test_hot_lead_priority(self):
        d = decide(
            {
                "name": "Acme Ops",
                "email": "ops@acme.example",
                "country": "US",
                "budget": 15000,
                "company_size": 75,
                "source": "website",
                "service_interest": "AI agent and CRM automation",
                "message": "Need lead routing via API and webhook",
            }
        )
        self.assertEqual(d.priority, "hot")


if __name__ == "__main__":
    unittest.main()
