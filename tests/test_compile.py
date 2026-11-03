import json
import os
import shutil
import tempfile
import unittest

from _load import load, example

plan = load("kill-or-build", "compile")
ledger = load("receipts", "ledger")


class Compile(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        with open(os.path.join(self.d, "idea.md"), "w") as fh:
            fh.write("# Moss Matcha Bar\n\nA walk-in matcha cafe on King St W.\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def numbers(self, **change):
        with open(example("burn-test", "example.json")) as fh:
            s = json.load(fh)
        s.update(change)
        with open(os.path.join(self.d, "numbers.json"), "w") as fh:
            json.dump(s, fh)

    def panel(self, buys, n=100):
        os.makedirs(os.path.join(self.d, "panel"), exist_ok=True)
        with open(os.path.join(self.d, "panel", "results.json"), "w") as fh:
            json.dump({"buys": buys, "passes": n - buys, "answered": n, "buy_rate": buys / float(n)}, fh)

    def real_buyer(self):
        os.makedirs(os.path.join(self.d, "evidence"), exist_ok=True)
        ledger.init(self.d)
        with open(os.path.join(self.d, "evidence", "evidence-log.md"), "a", encoding="utf-8") as fh:
            fh.write("| e01 | Pre-order export | Shopify | 2026-11-01 | PRIVATE |\n")
        ledger.add(self.d, "Pop-up pre-orders at $6.50", "demand", "MEASURED", "ANONYMISED", "62", "e01", commitment="paid")

    def test_no_numbers_is_incomplete(self):
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Incomplete")
        self.assertIn("run /burn-test", text)

    def test_good_numbers_and_panel_alone_is_unproven(self):
        self.numbers()
        self.panel(90)
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Unproven")
        self.assertIn("✗ No real buyer has paid, signed or booked yet", text)

    def test_a_simulated_demand_claim_does_not_count(self):
        self.numbers()
        ledger.init(self.d)
        ledger.add(self.d, "Simulated panel buy rate", "demand", "SIMULATED", "PRIVATE", "90 of 100")
        v, _ = plan.compile_plan(self.d)
        self.assertEqual(v, "Unproven")

    def quotes(self):
        with open(os.path.join(self.d, "evidence", "evidence-log.md"), "a", encoding="utf-8") as fh:
            fh.write("| e02 | Supplier and landlord quotes | Email | 2026-11-01 | PRIVATE |\n")
        return ledger.add(self.d, "Supplier and landlord quotes", "cost", "MEASURED", "PRIVATE", "", "e02")["id"]

    def real_numbers(self):
        """The price a real buyer paid (c01) and a quote behind every cost."""
        q = self.quotes()
        with open(example("burn-test", "example.json")) as fh:
            s = json.load(fh)
        for it in s["variable"] + s["fixed_monthly"]:
            it["claim"] = q
        s["sources"] = {"price": "c01"}
        with open(os.path.join(self.d, "numbers.json"), "w") as fh:
            json.dump(s, fh)

    def test_a_real_buyer_with_estimated_costs_is_unproven(self):
        self.numbers()
        self.panel(40)
        self.real_buyer()
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Unproven")
        self.assertIn("✗ Rests on estimates that could be real today", text)
        self.assertIn("price (no source)", text)

    def test_good_numbers_a_real_buyer_and_real_inputs_is_profitable(self):
        self.panel(40)
        self.real_buyer()
        self.real_numbers()
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Profitable")
        self.assertNotIn("Rests on estimates", text)
        self.assertIn("✓ 1 real commitment from buyers", text)
        self.assertTrue(text.startswith("# Moss Matcha Bar · Business plan"))
        self.assertIn("| Profit margin at plan | 38% per cup |", text)
        self.assertIn("| Buyer panel (simulated) | 40 buy · 60 pass |", text)
        self.assertIn("- The buyer panel: run /truth-serum", text.replace("## Not done yet", ""))

    def test_a_weak_panel_means_not_yet_even_with_a_real_buyer(self):
        self.numbers()
        self.panel(12)
        self.real_buyer()
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Not yet")
        self.assertIn("✗ 12 of 100 simulated buyers buy", text)

    def test_losing_money_means_not_yet(self):
        self.numbers(price=3.00)
        v, _ = plan.compile_plan(self.d)
        self.assertEqual(v, "Not yet")


if __name__ == "__main__":
    unittest.main()
