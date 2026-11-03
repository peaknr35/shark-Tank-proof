"""The eight ways a plan could say Profitable without a real buyer, found in review, each one closed.

1. compile.py trusted claims.csv as written (a hand-edited MEASURED demand claim with no evidence passed).
2. A blank number, "not yet", "zero" or "n/a" counted as a real buyer.
3. "MEASURED demand" was only a label: "200 free signups" passed as a paying buyer.
4. A computed claim needed no evidence of its own, so a "buyer" could be computed from a supplier quote.
5. The price's label came from the cited claim, but its value was never compared with it.
6. A THEY SAID IT price ("a friend said they would pay $6.50") counted as a real price.
7. The use label did not follow the sources: a claim computed from a PRIVATE one could go PUBLIC.
8. unit_economics.py read claims.csv on its own, so a broken cost claim still made every cost MEASURED.
"""

import csv
import json
import os
import shutil
import tempfile
import unittest

from _load import load, example

ledger = load("receipts", "ledger")
ue = load("burn-test", "unit_economics")
plan = load("kill-or-build", "compile")


class Base(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        ledger.init(self.d)
        with open(os.path.join(self.d, "evidence", "evidence-log.md"), "a", encoding="utf-8") as fh:
            fh.write("| e01 | Pre-order export | Shopify | 2026-11-01 | PRIVATE |\n")
            fh.write("| e02 | Supplier and landlord quotes | Email | 2026-11-01 | PRIVATE |\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def hand_row(self, **kw):
        """A line typed straight into claims.csv, the way a person editing the file would."""
        row = dict(id="", claim="", number="", kind="demand", status="MEASURED", use="PRIVATE", evidence="",
                   checked="2026-11-01", by="", commitment="")
        row["from"] = ""
        row.update(kw)
        with open(os.path.join(self.d, "evidence", "claims.csv"), "a", encoding="utf-8", newline="") as fh:
            csv.DictWriter(fh, fieldnames=ledger.FIELDS).writerow(row)

    def quotes(self):
        return ledger.add(self.d, "Supplier and landlord quotes", "cost", "MEASURED", "PRIVATE", "", "e02")["id"]

    def numbers(self, price_src, cost_src=None, **change):
        cost_src = cost_src or self.quotes()
        with open(example("burn-test", "example.json"), encoding="utf-8") as fh:
            s = json.load(fh)
        for it in s["variable"] + s["fixed_monthly"]:
            it["claim"] = cost_src
        s["sources"] = {"price": price_src}
        s.update(change)
        with open(os.path.join(self.d, "numbers.json"), "w", encoding="utf-8") as fh:
            json.dump(s, fh)

    def sale(self, number="62", claim="62 pre-orders paid at $6.50"):
        return ledger.add(self.d, claim, "demand", "MEASURED", "ANONYMISED", number, "e01", commitment="paid")["id"]

    def verdict(self):
        return plan.compile_plan(self.d)


class TheHappyPath(Base):
    def test_a_real_sale_and_quoted_costs_is_profitable(self):
        self.numbers(self.sale())
        v, _ = self.verdict()
        self.assertEqual(v, "Profitable")


class HandEditedLedger(Base):  # 1
    def test_a_hand_edited_buyer_with_no_evidence_does_not_count(self):
        self.hand_row(id="c01", claim="62 pre-orders paid at $6.50", number="62", commitment="paid")
        self.numbers("c01")
        v, text = self.verdict()
        self.assertEqual(v, "Unproven")
        self.assertIn("✗ No real buyer has paid, signed or booked yet", text)
        self.assertIn("c01: MEASURED needs an evidence id", text)
        self.assertIn("**Claims the ledger rejects**", text)

    def test_load_checked_downgrades_and_load_does_not(self):
        self.hand_row(id="c01", claim="62 pre-orders paid", number="62", commitment="paid")
        self.assertEqual(ledger.load(self.d)[0]["status"], "MEASURED")
        rows, rejected = ledger.load_checked(self.d)
        self.assertEqual(rows[0]["status"], "SIMULATED")
        self.assertTrue(rejected[0].startswith("c01: "))

    def test_gate_and_scan_read_checked_claims(self):
        self.hand_row(id="c01", claim="62 pre-orders paid", number="62", use="PUBLIC", commitment="paid")
        self.assertEqual(ledger.gate(ledger.load_checked(self.d)[0], "public"), [])
        path = os.path.join(self.d, "pitch.md")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("Validated: 62 buyers paid [c01].\n")
        problems = ledger.scan(self.d, path, "public")
        self.assertTrue(any("[c01] is SIMULATED" in p for p in problems), problems)
        self.assertTrue(any("validated" in p for p in problems), problems)


class BuyerCounts(Base):  # 2
    def test_only_a_positive_count_is_a_buyer(self):
        for n, real in (("", False), ("not yet", False), ("zero", False), ("n/a", False), ("-", False),
                        ("pending", False), ("0", False), ("0 of 5", False), ("1", True), ("1 of 5", True),
                        ("62 at $6.50", True), ("1,200", True)):
            r = {"kind": "demand", "status": "MEASURED", "number": n, "commitment": "paid", "evidence": "e01"}
            self.assertEqual(ledger.is_commitment(r), real, n)

    def test_add_refuses_measured_demand_with_no_count(self):
        for n in ("", "not yet", "zero"):
            with self.assertRaisesRegex(ledger.LedgerError, "needs a number"):
                ledger.add(self.d, "Pre-orders", "demand", "MEASURED", "PRIVATE", n, "e01", commitment="paid")

    def test_a_hand_edited_not_yet_does_not_count(self):
        self.hand_row(id="c01", claim="Pre-orders", number="not yet", evidence="e01", commitment="paid")
        self.assertEqual(ledger.summarise(ledger.load_checked(self.d)[0])["demand_measured"], 0)


class Commitments(Base):  # 3
    def test_a_signup_is_not_a_buyer(self):
        with self.assertRaisesRegex(ledger.LedgerError, "needs --commitment"):
            ledger.add(self.d, "200 waitlist signups", "demand", "MEASURED", "PUBLIC", "200", "e01")

    def test_only_named_commitments_count(self):
        with self.assertRaisesRegex(ledger.LedgerError, "is not one of"):
            ledger.add(self.d, "200 signups", "demand", "MEASURED", "PUBLIC", "200", "e01", commitment="signup")
        for c in ledger.COMMITMENTS:
            ledger.add(self.d, "A real yes", "demand", "MEASURED", "PRIVATE", "1", "e01", commitment=c)
        self.assertEqual(ledger.summarise(ledger.load_checked(self.d)[0])["demand_measured"], len(ledger.COMMITMENTS))

    def test_a_hand_edited_buyer_with_no_commitment_is_rejected(self):
        self.hand_row(id="c01", claim="200 signups", number="200", evidence="e01")
        self.numbers("c01")
        v, text = self.verdict()
        self.assertEqual(v, "Unproven")
        self.assertIn("needs --commitment", text)

    def test_signup_words_warn_even_with_a_commitment(self):
        ledger.add(self.d, "200 waitlist signups", "demand", "MEASURED", "PUBLIC", "200", "e01", commitment="paid")
        _, warnings = ledger.check(self.d)
        self.assertTrue(any("sounds like interest, not a commitment" in w for w in warnings), warnings)

    def test_a_logged_no_still_needs_no_commitment(self):
        ledger.add(self.d, "Firms asked for a pilot", "demand", "MEASURED", "PUBLIC", "0 of 10", "e01")
        s = ledger.summarise(ledger.load_checked(self.d)[0])
        self.assertEqual((s["demand_measured"], s["demand_refusals"]), (0, 1))

    def test_only_demand_has_a_commitment(self):
        with self.assertRaisesRegex(ledger.LedgerError, "only a demand claim"):
            ledger.add(self.d, "Quote", "cost", "MEASURED", "PRIVATE", "$1", "e02", commitment="paid")


class ComputedBuyers(Base):  # 4
    def test_a_buyer_cannot_be_computed(self):
        q = self.quotes()
        with self.assertRaisesRegex(ledger.LedgerError, "needs its own evidence id"):
            ledger.add(self.d, "Buyers (computed)", "demand", None, "PRIVATE", "40", derived_from=q, commitment="paid")

    def test_other_computed_claims_still_carry_their_sources_evidence(self):
        q = self.quotes()
        r = ledger.add(self.d, "Cost per cup (computed)", "cost", None, "PRIVATE", "$1.74", derived_from=q)
        self.assertEqual(r["status"], "MEASURED")


class RealPrice(Base):  # 5 and 6
    def test_the_price_must_match_the_sale(self):
        self.numbers(self.sale(), price=19.0)
        v, text = self.verdict()
        self.assertEqual(v, "Unproven")
        self.assertIn("records a sale, but not at $19.00", text)

    def test_a_they_said_it_price_is_not_a_real_price(self):
        self.sale()
        said = ledger.add(self.d, "A friend said they would pay $6.50", "price", "THEY SAID IT", "PRIVATE", "$6.50",
                          "e01")["id"]
        self.numbers(said)
        v, text = self.verdict()
        self.assertEqual(v, "Unproven")
        self.assertIn("is THEY SAID IT: a price is real only when a buyer paid it", text)

    def test_the_price_cannot_cite_a_cost_quote(self):
        self.sale()
        q = self.quotes()
        self.numbers(q, cost_src=q)
        v, text = self.verdict()
        self.assertEqual(v, "Unproven")
        self.assertIn("is a cost claim, not a price or a sale", text)

    def test_a_measured_price_claim_at_the_price_counts(self):
        self.sale(claim="62 pre-orders paid")
        p = ledger.add(self.d, "Price on the paid pre-orders", "price", "MEASURED", "PRIVATE", "$6.50", "e01")["id"]
        self.numbers(p)
        self.assertEqual(self.verdict()[0], "Profitable")


class UseLabels(Base):  # 7
    def test_a_computed_claim_cannot_be_wider_than_its_sources(self):
        priv = ledger.add(self.d, "Client fee", "price", "MEASURED", "PRIVATE", "$4,000", "e01")["id"]
        with self.assertRaisesRegex(ledger.LedgerError, "use leak"):
            ledger.add(self.d, "Average fee", "price", None, "PUBLIC", "$4,000", derived_from=priv)
        r = ledger.add(self.d, "Average fee", "price", None, "PRIVATE", "$4,000", derived_from=priv)
        self.assertEqual(r["use"], "PRIVATE")

    def test_a_hand_edited_use_leak_never_passes_the_gate(self):
        ledger.add(self.d, "Client fee", "price", "MEASURED", "PRIVATE", "$4,000", "e01")
        self.hand_row(id="c02", claim="Average fee", kind="price", use="PUBLIC", number="$4,000", **{"from": "c01"})
        self.assertEqual(ledger.gate(ledger.load_checked(self.d)[0], "public"), [])


class BurnTestReadsCheckedClaims(Base):  # 8
    def test_a_broken_cost_claim_makes_the_costs_simulated(self):
        self.hand_row(id="c01", claim="Quotes", kind="cost", evidence="e99")  # an evidence id that is not in the log
        rows = ue.load_ledger(self.d)
        self.assertEqual(rows["c01"]["status"], "SIMULATED")
        self.numbers(self.sale(), cost_src="c01")
        v, text = self.verdict()
        self.assertEqual(v, "Unproven")
        self.assertIn("evidence e99 is not in evidence-log.md", text)


if __name__ == "__main__":
    unittest.main()
