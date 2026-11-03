"""Rule 11 (after Ready, Fire, Aim): the first sale buys a customer, the back end pays.

burn-test works out the most the business can spend to win a customer (the first order plus what the
customer buys next), and kill-or-build checks what it really costs against that, with labels.
"""

import json
import os
import re
import shutil
import tempfile
import unittest

from _load import load, example, SKILLS_DIR

ledger = load("receipts", "ledger")
ue = load("burn-test", "unit_economics")
plan = load("kill-or-build", "compile")


def spec(**change):
    with open(example("burn-test", "example.json"), encoding="utf-8") as fh:
        s = json.load(fh)
    s.update(change)
    return s


class WhatACustomerIsWorth(unittest.TestCase):
    def test_front_end_only(self):
        a = ue.analyse(spec())
        self.assertAlmostEqual(a["allowable_acquisition_cost"], 4.76, places=2)  # one cup's contribution
        self.assertIsNone(a["acquisition_fits"])

    def test_first_order_and_back_end(self):
        a = ue.analyse(spec(units_per_customer=2, backend_per_customer=30))
        self.assertAlmostEqual(a["allowable_acquisition_cost"], 2 * 4.76 + 30, places=2)

    def test_too_expensive_to_win_a_customer_is_flagged(self):
        a = ue.analyse(spec(acquisition_cost=12))
        self.assertFalse(a["acquisition_fits"])
        self.assertTrue(any("every new customer loses money" in f for f in a["flags"]))
        self.assertTrue(ue.analyse(spec(acquisition_cost=12, backend_per_customer=20))["acquisition_fits"])

    def test_the_report_shows_it(self):
        s = spec(backend_per_customer=20, acquisition_cost=9)
        text = ue.report(s, ue.analyse(s))
        self.assertIn("## What one customer is worth", text)
        self.assertIn("**Most you can spend to win a customer: $24.76**", text)
        self.assertIn("What it costs now: $9.00, inside the limit.", text)

    def test_no_back_end_says_so(self):
        s = spec()
        self.assertIn("none given: what is the next thing they buy?", ue.report(s, ue.analyse(s)))


class Labels(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        ledger.init(self.d)
        with open(os.path.join(self.d, "evidence", "evidence-log.md"), "a", encoding="utf-8") as fh:
            fh.write("| e01 | Ad account export | Meta | 2026-11-01 | PRIVATE |\n")
            fh.write("| e02 | Pre-order export | Shopify | 2026-11-01 | PRIVATE |\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def rows(self):
        return {r["id"]: r for r in ledger.load(self.d)}

    def write(self, s):
        with open(os.path.join(self.d, "numbers.json"), "w", encoding="utf-8") as fh:
            json.dump(s, fh)

    def test_a_planned_back_end_keeps_the_limit_planned(self):
        ledger.add(self.d, "Real sale price", "price", "MEASURED", "PRIVATE", "$6.50", "e02")  # c01
        a = ue.analyse(spec(sources={"price": "c01"}, backend_per_customer=20), ledger=self.rows())
        self.assertEqual(a["labels"]["allowable_acquisition_cost"]["status"], "PLANNED")

    def test_a_simulated_price_makes_the_limit_simulated(self):
        ledger.add(self.d, "Panel price", "price", "SIMULATED", "PRIVATE", "$6.50")  # c01
        a = ue.analyse(spec(sources={"price": "c01"}), ledger=self.rows())
        self.assertEqual(a["labels"]["allowable_acquisition_cost"]["status"], "SIMULATED")

    def test_kill_or_build_checks_the_cost_of_a_customer(self):
        ledger.add(self.d, "Pop-up pre-orders at $6.50", "demand", "MEASURED", "ANONYMISED", "62", "e02")  # c01
        ledger.add(self.d, "Cost per pre-order, two-week test", "cost", "MEASURED", "PRIVATE", "$12", "e01")  # c02
        self.write(spec(acquisition_cost=12, sources={"acquisition_cost": "c02"}))
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Not yet")
        self.assertIn("✗ Winning a customer costs $12.00 against the $4.76 one is worth in year 1.", text)
        self.write(spec(acquisition_cost=4, sources={"acquisition_cost": "c02", "price": "c01"}))
        v, text = plan.compile_plan(self.d)
        self.assertIn("✓ Winning a customer costs $4.00 against the $4.76 one is worth in year 1.", text)

    def test_no_acquisition_cost_adds_no_check(self):
        self.write(spec())
        _, text = plan.compile_plan(self.d)
        self.assertNotIn("Winning a customer costs", text)


class Skills(unittest.TestCase):
    def read(self, rel):
        with open(os.path.join(SKILLS_DIR, rel), encoding="utf-8") as fh:
            return fh.read()

    def test_rule_11_exists_and_every_skill_points_at_it(self):
        self.assertIn("## 11. Ready, Fire, Aim", self.read("receipts/rules.md"))
        for s in sorted(os.listdir(SKILLS_DIR)):
            if os.path.isfile(os.path.join(SKILLS_DIR, s, "SKILL.md")):
                self.assertRegex(self.read(os.path.join(s, "SKILL.md")), r"[Rr]ule 11", s)

    def test_the_board_has_five_lenses(self):
        lenses = re.findall(r"^## The (\w+) lens", self.read("shark-board/lenses.md"), re.M)
        self.assertEqual(lenses, ["Offers", "Monopoly", "Product", "Evidence", "Selling"])
        self.assertIn("Launch five sub-agents", self.read("shark-board/SKILL.md"))


if __name__ == "__main__":
    unittest.main()
