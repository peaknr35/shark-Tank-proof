"""Rule 10: a number takes the weakest label of anything it was computed from.

The scenario this guards: /litmus sets a price from the simulated buyers,
/burn-test works out the margin from that price, and /kill-or-build adds it up.
The margin must arrive SIMULATED, not looking MEASURED because arithmetic made it.
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
vw = load("litmus", "van_westendorp")


class Base(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        ledger.init(self.d)
        with open(os.path.join(self.d, "evidence", "evidence-log.md"), "a", encoding="utf-8") as fh:
            fh.write("| e01 | Supplier quote | Email | 2026-11-01 | PRIVATE |\n")
            fh.write("| e02 | Pre-order export | Shopify | 2026-11-01 | PRIVATE |\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def rows(self):
        return {r["id"]: r for r in ledger.load(self.d)}


class Ledger(Base):
    def test_weakest_order(self):
        self.assertEqual(ledger.weakest(["MEASURED", "SIMULATED", "PLANNED"]), "SIMULATED")
        self.assertEqual(ledger.weakest(["MEASURED", "THEY SAID IT"]), "THEY SAID IT")
        self.assertEqual(ledger.weakest(["MEASURED", "PLANNED"]), "PLANNED")
        self.assertEqual(ledger.weakest(["MEASURED", "whatever"]), "SIMULATED")

    def test_a_computed_claim_inherits_the_weakest_label(self):
        ledger.add(self.d, "Matcha quote", "cost", "MEASURED", "PRIVATE", "$0.92", "e01")       # c01
        ledger.add(self.d, "Panel price range", "price", "SIMULATED", "PRIVATE", "$5.80-$7.40")  # c02
        r = ledger.add(self.d, "Contribution per cup", "cost", None, "PRIVATE", "$4.76", derived_from="c01,c02")
        self.assertEqual(r["status"], "SIMULATED")
        self.assertEqual(r["from"], "c01,c02")

    def test_a_stronger_label_than_the_sources_is_refused(self):
        ledger.add(self.d, "Panel price range", "price", "SIMULATED", "PRIVATE", "$5.80-$7.40")
        for st in ("MEASURED", "THEY SAID IT", "PLANNED"):
            with self.assertRaises(ledger.LedgerError) as e:
                ledger.add(self.d, "Recommended price", "price", st, "PRIVATE", "$6.50", derived_from="c01")
            self.assertIn("label leak", str(e.exception))
        self.assertEqual(ledger.add(self.d, "Recommended price", "price", "SIMULATED", "PRIVATE",
                                    derived_from="c01")["status"], "SIMULATED")

    def test_computed_from_measured_needs_no_evidence_of_its_own(self):
        ledger.add(self.d, "Matcha quote", "cost", "MEASURED", "PRIVATE", "$0.92", "e01")
        ledger.add(self.d, "Real sale price", "price", "MEASURED", "PRIVATE", "$6.50", "e02")
        r = ledger.add(self.d, "Contribution per cup", "cost", None, "PRIVATE", derived_from="c01 c02")
        self.assertEqual(r["status"], "MEASURED")

    def test_an_unknown_source_is_refused(self):
        with self.assertRaises(ledger.LedgerError):
            ledger.add(self.d, "Margin", "cost", None, "PRIVATE", derived_from="c09")

    def test_check_finds_a_leak_written_by_hand(self):
        ledger.add(self.d, "Panel price range", "price", "SIMULATED", "PRIVATE")
        with open(os.path.join(self.d, "evidence", "claims.csv"), "a", encoding="utf-8", newline="") as fh:
            csv.DictWriter(fh, fieldnames=ledger.FIELDS).writerow(dict(
                id="c02", claim="Margin", number="38%", kind="cost", status="MEASURED", use="PRIVATE",
                evidence="", checked="2026-11-01", by="", **{"from": "c01"}))
        errors, _ = ledger.check(self.d)
        self.assertTrue(any("c02" in e and "label leak" in e for e in errors), errors)

    def test_an_old_ledger_gets_the_from_column(self):
        path = os.path.join(self.d, "evidence", "claims.csv")
        with open(path, "w", encoding="utf-8", newline="") as fh:
            fh.write("id,claim,number,kind,status,use,evidence,checked,by\n")
            fh.write("c01,Panel range,$6,price,SIMULATED,PRIVATE,,2026-11-01,\n")
        ledger.add(self.d, "Price", "price", None, "PRIVATE", derived_from="c01")
        with open(path, encoding="utf-8") as fh:
            self.assertEqual(next(csv.reader(fh)), ledger.FIELDS)
        self.assertEqual([r["status"] for r in ledger.load(self.d)], ["SIMULATED", "SIMULATED"])

    def test_cli_add_from_without_status(self):
        ledger.add(self.d, "Panel price range", "price", "SIMULATED", "PRIVATE")
        self.assertEqual(ledger.main(["--dir", self.d, "add", "--claim", "Price", "--kind", "price",
                                      "--use", "PRIVATE", "--from", "c01"]), 0)
        self.assertEqual(ledger.load(self.d)[1]["status"], "SIMULATED")
        self.assertEqual(ledger.main(["--dir", self.d, "add", "--claim", "Price", "--kind", "price",
                                      "--use", "PRIVATE", "--status", "MEASURED", "--from", "c01"]), 1)


def spec(**change):
    with open(example("burn-test", "example.json"), encoding="utf-8") as fh:
        s = json.load(fh)
    s.update(change)
    return s


class UnitEconomics(Base):
    def test_no_sources_is_planned(self):
        a = ue.analyse(spec())
        for k in ue.DEPENDS:
            self.assertEqual(a["labels"][k]["status"], "PLANNED", k)

    def test_a_simulated_price_makes_the_margin_simulated(self):
        ledger.add(self.d, "Recommended price", "price", "SIMULATED", "PRIVATE", "$6.50")
        a = ue.analyse(spec(sources={"price": "c01"}), ledger=self.rows())
        for k in ue.DEPENDS:
            self.assertEqual(a["labels"][k]["status"], "SIMULATED", k)
        self.assertIn("price [c01]", a["labels"]["contribution"]["weakest"])
        self.assertAlmostEqual(a["contribution"], 4.76, places=2)  # the number is the same; only its label changed

    def test_measured_inputs_keep_measured_until_a_plan_joins(self):
        ledger.add(self.d, "Real sale price", "price", "MEASURED", "PRIVATE", "$6.50", "e02")  # c01
        ledger.add(self.d, "Supplier quotes", "cost", "MEASURED", "PRIVATE", "", "e01")          # c02
        s = spec(sources={"price": "c01"})
        for it in s["variable"]:
            it["claim"] = "c02"
        a = ue.analyse(s, ledger=self.rows())
        self.assertEqual(a["labels"]["contribution"]["status"], "MEASURED")
        self.assertEqual(a["labels"]["breakeven_per_day"]["status"], "PLANNED")  # rent and labour not quoted yet
        self.assertEqual(a["labels"]["margin_at_plan"]["status"], "PLANNED")  # the plan volume is a plan

    def test_breakeven_is_measured_when_every_cost_is_quoted(self):
        ledger.add(self.d, "Real sale price", "price", "MEASURED", "PRIVATE", "$6.50", "e02")  # c01
        ledger.add(self.d, "Supplier and landlord quotes", "cost", "MEASURED", "PRIVATE", "", "e01")  # c02
        s = spec(sources={"price": "c01"})
        for it in s["variable"] + s["fixed_monthly"]:
            it["claim"] = "c02"
        a = ue.analyse(s, ledger=self.rows())
        self.assertEqual(a["labels"]["breakeven_per_day"]["status"], "MEASURED")
        self.assertEqual(a["labels"]["margin_at_plan"]["status"], "PLANNED")  # still uses the plan volume
        self.assertEqual(a["labels"]["fits_capacity"]["status"], "PLANNED")  # capacity and days have no source
        s["variable"][0].pop("claim")  # one unquoted cost brings it back down
        self.assertEqual(ue.analyse(s, ledger=self.rows())["labels"]["breakeven_per_day"]["status"], "PLANNED")
        s = spec(sources={"price": "c01"})
        for it in s["variable"] + s["fixed_monthly"]:
            it["claim"] = "c02"
        ledger.add(self.d, "Panel price", "price", "SIMULATED", "PRIVATE")  # c03
        s["sources"]["price"] = "c03"
        self.assertEqual(ue.analyse(s, ledger=self.rows())["labels"]["breakeven_per_day"]["status"], "SIMULATED")

    def test_a_missing_claim_counts_as_simulated(self):
        a = ue.analyse(spec(sources={"price": "c42"}), ledger=self.rows())
        self.assertEqual(a["labels"]["contribution"]["status"], "SIMULATED")
        self.assertTrue(any("c42" in w for w in a["label_warnings"]))

    def test_a_list_source_takes_the_weakest(self):
        ledger.add(self.d, "Real sale price", "price", "MEASURED", "PRIVATE", "$6.50", "e02")
        a = ue.analyse(spec(sources={"price": ["c01", "SIMULATED"]}), ledger=self.rows())
        self.assertEqual(a["inputs"]["price"]["status"], "SIMULATED")

    def test_a_what_if_never_raises_a_label(self):
        ledger.add(self.d, "Real sale price", "price", "MEASURED", "PRIVATE", "$6.50", "e02")
        s = spec(sources={"price": "c01"})
        self.assertEqual(ue.analyse(s, price=7.0, ledger=self.rows())["inputs"]["price"]["status"], "PLANNED")
        ledger.add(self.d, "Panel price", "price", "SIMULATED", "PRIVATE")
        s = spec(sources={"price": "c02"})
        self.assertEqual(ue.analyse(s, price=7.0, ledger=self.rows())["inputs"]["price"]["status"], "SIMULATED")

    def test_report_says_how_we_know(self):
        ledger.add(self.d, "Recommended price", "price", "SIMULATED", "PRIVATE", "$6.50")
        s = spec(sources={"price": "c01"})
        text = ue.report(s, ue.analyse(s, ledger=self.rows()), self.rows())
        self.assertIn("## How we know each number", text)
        self.assertIn("| Profit margin at plan | SIMULATED | price [c01] |", text)
        self.assertIn("**38%** of every sale, after every cost. [SIMULATED]", text)
        self.assertIn("Simulated inputs sit under these results", text)

    def test_cli_reads_the_ledger_next_to_the_numbers(self):
        ledger.add(self.d, "Recommended price", "price", "SIMULATED", "PRIVATE", "$6.50")
        path = os.path.join(self.d, "numbers.json")
        with open(path, "w") as fh:
            json.dump(spec(sources={"price": "c01"}), fh)
        out = os.path.join(self.d, "cfo.md")
        self.assertEqual(ue.main([path, "--out", out]), 0)
        with open(out, encoding="utf-8") as fh:
            self.assertIn("| Contribution per unit | SIMULATED | price [c01] |", fh.read())


class Handoff(Base):
    """litmus -> burn-test -> kill-or-build, the break this rule exists for."""

    def write_numbers(self, **change):
        with open(os.path.join(self.d, "numbers.json"), "w") as fh:
            json.dump(spec(**change), fh)

    def real_buyer(self):
        ledger.add(self.d, "Pop-up pre-orders", "demand", "MEASURED", "ANONYMISED", "62", "e02")

    def test_a_panel_price_cannot_make_the_plan_profitable(self):
        # litmus: the range is SIMULATED, the price is logged --from it, numbers.json points at it
        ledger.add(self.d, "Panel acceptable range", "price", "SIMULATED", "PRIVATE", "$5.80 to $7.40")  # c01
        price = ledger.add(self.d, "Recommended price", "price", None, "PRIVATE", "$6.50", derived_from="c01")
        self.assertEqual(price["status"], "SIMULATED")
        self.write_numbers(sources={"price": price["id"]})
        self.real_buyer()  # even with a real buyer on another claim
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Unproven")
        self.assertIn("[SIMULATED: price [c02]]", text)
        self.assertIn("passes only on simulated inputs", text)
        self.assertIn("| Profit margin at plan | 38% per cup | SIMULATED |", text)

    def test_once_a_real_buyer_pays_the_price_it_can_pass(self):
        ledger.add(self.d, "Panel acceptable range", "price", "SIMULATED", "PRIVATE", "$5.80 to $7.40")
        ledger.add(self.d, "62 pre-orders paid at $6.50", "price", "MEASURED", "PRIVATE", "$6.50", "e02")  # c02
        self.write_numbers(sources={"price": "c02"})
        self.real_buyer()
        v, text = plan.compile_plan(self.d)
        self.assertEqual(v, "Profitable")
        self.assertIn("[PLANNED:", text)  # still projections: the costs and ramp have no quotes behind them

    def test_a_simulated_pass_still_fails_when_the_numbers_fail(self):
        ledger.add(self.d, "Panel price", "price", "SIMULATED", "PRIVATE", "$3.00")
        self.write_numbers(price=3.00, sources={"price": "c01"})
        v, _ = plan.compile_plan(self.d)
        self.assertEqual(v, "Not yet")

    def test_the_plan_lists_label_leaks_in_the_ledger(self):
        ledger.add(self.d, "Panel range", "price", "SIMULATED", "PRIVATE")
        with open(os.path.join(self.d, "evidence", "claims.csv"), "a", encoding="utf-8", newline="") as fh:
            csv.DictWriter(fh, fieldnames=ledger.FIELDS).writerow(dict(
                id="c02", claim="Price", number="$6.50", kind="price", status="MEASURED", use="PRIVATE",
                evidence="", checked="2026-11-01", by="", **{"from": "c01"}))
        self.write_numbers()
        _, text = plan.compile_plan(self.d)
        self.assertIn("**Label leaks in the ledger**", text)


class Litmus(unittest.TestCase):
    def test_the_range_carries_its_label(self):
        rows = [(2.5 + i / 9.0, 4.0 + i / 9.0, 6.0 + i / 6.0, 7.5 + i / 4.5) for i in range(10)]
        text = vw.report(vw.analyse(rows), 0)
        self.assertIn("**How we know this range: SIMULATED.**", text)
        self.assertIn("THEY SAID IT", vw.report(vw.analyse(rows), 0, status="THEY SAID IT"))

    def test_the_panel_folder_is_always_simulated(self):
        d = tempfile.mkdtemp()
        try:
            self.assertEqual(vw.source_status(d, "MEASURED"), "SIMULATED")
            self.assertEqual(vw.source_status(os.path.join(d, "x.csv")), "SIMULATED")
            self.assertEqual(vw.source_status(os.path.join(d, "x.csv"), "THEY SAID IT"), "THEY SAID IT")
        finally:
            shutil.rmtree(d)


if __name__ == "__main__":
    unittest.main()
