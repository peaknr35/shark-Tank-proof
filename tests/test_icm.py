"""The founder folder as an ICM workspace: a stage map, labelled handoff files, and a trace back to the sources."""

import json
import os
import shutil
import tempfile
import unittest

from _load import load, example

ledger = load("receipts", "ledger")
ue = load("burn-test", "unit_economics")
plan = load("kill-or-build", "compile")
vw = load("litmus", "van_westendorp")


class Workspace(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        ledger.init(self.d)
        with open(os.path.join(self.d, "evidence", "evidence-log.md"), "a", encoding="utf-8") as fh:
            fh.write("| e01 | Pre-order export | Shopify | 2026-11-01 | PRIVATE |\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def rows(self):
        return {r["id"]: r for r in ledger.load(self.d)}

    def numbers(self, **change):
        with open(example("burn-test", "example.json")) as fh:
            s = json.load(fh)
        s.update(change)
        path = os.path.join(self.d, "numbers.json")
        with open(path, "w") as fh:
            json.dump(s, fh)
        return path

    def simulated_price(self):
        rng = ledger.add(self.d, "Panel acceptable price range", "price", "SIMULATED", "PRIVATE", "$5.80 to $7.40")
        return ledger.add(self.d, "Recommended price", "price", None, "PRIVATE", "$6.50", derived_from=rng["id"])

    def test_init_writes_the_stage_map_and_handoff_folder(self):
        self.assertTrue(os.path.isdir(os.path.join(self.d, "handoff")))
        with open(os.path.join(self.d, "CONTEXT.md"), encoding="utf-8") as fh:
            text = fh.read()
        for stage in ("| 04 | `/litmus`", "| 06 | `/burn-test`", "| 11 | `/kill-or-build`", "handoff/06_burn-test.json"):
            self.assertIn(stage, text)
        self.assertEqual(ledger.init(self.d), [])

    def test_trace_walks_the_from_column(self):
        price = self.simulated_price()
        lines = ledger.trace(self.rows(), price["id"])
        self.assertIn("SIMULATED: Recommended price", lines[0])
        self.assertIn("  [c01] SIMULATED: Panel acceptable price range", lines[1])
        self.assertIn("not in the ledger", ledger.trace(self.rows(), "c99")[0])

    def test_burn_test_hands_off_labelled_results(self):
        price = self.simulated_price()
        path = self.numbers(sources={"price": price["id"]})
        self.assertEqual(ue.main([path, "--handoff", self.d, "--out", os.path.join(self.d, "cfo.md")]), 0)
        with open(os.path.join(self.d, "handoff", "06_burn-test.json"), encoding="utf-8") as fh:
            h = json.load(fh)
        self.assertEqual(h["stage"], "06_burn-test")
        self.assertEqual(h["results"]["margin_at_plan"]["status"], "SIMULATED")
        self.assertIn("price [c02]", h["results"]["margin_at_plan"]["set_by"])
        self.assertTrue(h["results"]["fits_capacity"]["value"])

    def test_a_what_if_is_never_handed_off(self):
        self.assertEqual(ue.main([self.numbers(), "--handoff", self.d, "--price", "7"]), 2)
        self.assertFalse(os.path.exists(os.path.join(self.d, "handoff", "06_burn-test.json")))

    def test_litmus_hands_off_the_range_with_its_label(self):
        res = {"n": 20, "points": {"PMC": 5.8, "OPP": 6.4, "IPP": 6.8, "PME": 7.4}}
        vw.write_handoff(res, self.d, "SIMULATED", "founder/panel/answers")
        with open(os.path.join(self.d, "handoff", "04_litmus.json"), encoding="utf-8") as fh:
            h = json.load(fh)
        self.assertEqual(h["results"]["pme"], {"value": 7.4, "status": "SIMULATED", "set_by": ["founder/panel/answers"]})

    def test_the_plan_flags_a_stale_handoff(self):
        # burn-test ran while the price was a real sale; the sale claim is later corrected to a planned price
        sale = ledger.add(self.d, "Pop-up pre-orders at $6.50", "demand", "MEASURED", "ANONYMISED", "62", "e01")
        path = self.numbers(sources={"price": sale["id"]})
        ue.main([path, "--handoff", self.d])
        v, text = plan.compile_plan(self.d)
        self.assertNotIn("Stale handoff", text)
        with open(os.path.join(self.d, "handoff", "06_burn-test.json"), encoding="utf-8") as fh:
            h = json.load(fh)
        h["results"]["contribution"]["status"] = "MEASURED"
        h["results"]["year1_profit"]["status"] = "MEASURED"  # hand-edited stronger than its sources
        with open(os.path.join(self.d, "handoff", "06_burn-test.json"), "w", encoding="utf-8") as fh:
            json.dump(h, fh)
        v, text = plan.compile_plan(self.d)
        self.assertIn("**Stale handoff**", text)
        self.assertIn("- year1_profit: MEASURED in the handoff, PLANNED now", text)

    def test_the_verdict_ignores_a_hand_edited_handoff(self):
        price = self.simulated_price()
        ledger.add(self.d, "Pop-up pre-orders at $6.50", "demand", "MEASURED", "ANONYMISED", "62", "e01")
        path = self.numbers(sources={"price": price["id"]})
        ue.main([path, "--handoff", self.d])
        hp = os.path.join(self.d, "handoff", "06_burn-test.json")
        with open(hp, encoding="utf-8") as fh:
            h = json.load(fh)
        for r in h["results"].values():
            r["status"] = "MEASURED"
        with open(hp, "w", encoding="utf-8") as fh:
            json.dump(h, fh)
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Unproven")
        self.assertIn("Stale handoff", text)


if __name__ == "__main__":
    unittest.main()
