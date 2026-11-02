import datetime
import json
import os
import shutil
import tempfile
import unittest

from _load import load

ledger = load("receipts", "ledger")


class Ledger(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        ledger.init(self.d)
        with open(os.path.join(self.d, "evidence", "evidence-log.md"), "a", encoding="utf-8") as fh:
            fh.write("| e01 | Signed pilot page | Email from the firm | 2026-11-01 | ASK FIRST |\n")

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_init_makes_the_folders(self):
        for sub in ("evidence", "evidence/calls", "opportunities", "outputs"):
            self.assertTrue(os.path.isdir(os.path.join(self.d, sub)), sub)
        self.assertEqual(ledger.init(self.d), [])

    def test_measured_needs_evidence_that_exists(self):
        with self.assertRaises(ledger.LedgerError):
            ledger.add(self.d, "3 firms paid", "demand", "MEASURED", "PUBLIC")
        with self.assertRaises(ledger.LedgerError):
            ledger.add(self.d, "3 firms paid", "demand", "MEASURED", "PUBLIC", evidence="e09")
        r = ledger.add(self.d, "1 firm signed a pilot", "demand", "MEASURED", "ASK FIRST", "1", "e01")
        self.assertEqual(r["id"], "c01")

    def test_simulated_and_planned_need_no_evidence(self):
        ledger.add(self.d, "Panel buy rate", "demand", "SIMULATED", "PRIVATE", "40 of 100")
        r = ledger.add(self.d, "3x faster triage", "product", "PLANNED", "PUBLIC")
        self.assertEqual(r["id"], "c02")

    def test_bad_labels_are_refused(self):
        with self.assertRaises(ledger.LedgerError):
            ledger.add(self.d, "x", "demand", "PROBABLY", "PUBLIC")
        with self.assertRaises(ledger.LedgerError):
            ledger.add(self.d, "x", "vibes", "PLANNED", "PUBLIC")

    def test_check_flags_stale_claims(self):
        ledger.add(self.d, "Supplier quote", "cost", "MEASURED", "PRIVATE", "$2.10", "e01", checked="2026-01-01")
        errors, warnings = ledger.check(self.d, today=datetime.date(2026, 11, 2))
        self.assertEqual(errors, [])
        self.assertEqual(len(warnings), 1)

    def test_summary_counts_real_demand_only(self):
        ledger.add(self.d, "Panel buy rate", "demand", "SIMULATED", "PRIVATE", "90 of 100")
        s = ledger.write_summary(self.d)
        self.assertEqual(s["demand_measured"], 0)
        with open(os.path.join(self.d, "evidence", "claims.md"), encoding="utf-8") as fh:
            self.assertIn("No real buyer has paid, signed or booked yet", fh.read())
        ledger.add(self.d, "1 firm signed a pilot", "demand", "MEASURED", "ASK FIRST", "1", "e01")
        s = ledger.write_summary(self.d)
        self.assertEqual(s["demand_measured"], 1)
        with open(os.path.join(self.d, "evidence", "summary.json"), encoding="utf-8") as fh:
            self.assertEqual(json.load(fh)["by_status"]["MEASURED"], 1)

    def test_a_logged_no_is_not_a_commitment(self):
        for n in ("0", "0 of 10", "none", "No"):
            ledger.add(self.d, "Firms that agreed to a pilot", "demand", "MEASURED", "PUBLIC", n, "e01")
        s = ledger.summarise(ledger.load(self.d))
        self.assertEqual(s["demand_measured"], 0)
        self.assertEqual(s["demand_refusals"], 4)
        ledger.add(self.d, "Firms that agreed to a pilot", "demand", "MEASURED", "PUBLIC", "1 of 10", "e01")
        self.assertEqual(ledger.summarise(ledger.load(self.d))["demand_measured"], 1)

    def test_gate_never_passes_simulated_or_private(self):
        ledger.add(self.d, "Panel buy rate", "demand", "SIMULATED", "PUBLIC", "90 of 100")
        ledger.add(self.d, "Our fee", "price", "PLANNED", "PRIVATE", "$750")
        ledger.add(self.d, "Signed pilot", "demand", "MEASURED", "ASK FIRST", "1", "e01")
        ledger.add(self.d, "Runs offline", "product", "PLANNED", "PUBLIC")
        rows = ledger.load(self.d)
        self.assertEqual([r["id"] for r in ledger.gate(rows, "public")], ["c04"])
        self.assertEqual([r["id"] for r in ledger.gate(rows, "permission")], ["c03", "c04"])

    def test_scan_catches_simulated_citations_and_hype(self):
        ledger.add(self.d, "Panel buy rate", "demand", "SIMULATED", "PRIVATE", "90 of 100")
        ledger.add(self.d, "Runs offline", "product", "PLANNED", "PUBLIC")
        out = os.path.join(self.d, "outputs", "pitch.md")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("Validated demand: 90% of buyers want it [c01]. It runs offline [c02].\n")
        problems = ledger.scan(self.d, out, "public")
        self.assertTrue(any("[c01]" in p and "may not go" in p for p in problems))
        self.assertTrue(any("'validated'" in p for p in problems))
        self.assertTrue(any("[c02]" in p and "PLANNED" in p for p in problems))

    def test_scan_reads_grouped_and_ranged_citations(self):
        ledger.add(self.d, "Runs offline", "product", "MEASURED", "PUBLIC", evidence="e01")
        ledger.add(self.d, "Panel buy rate", "demand", "SIMULATED", "PRIVATE", "90 of 100")
        ledger.add(self.d, "Our fee", "price", "PLANNED", "PRIVATE", "$750")
        out = os.path.join(self.d, "outputs", "pitch.md")
        for cite in ("[c01, c02]", "[c01-c03]"):
            with open(out, "w", encoding="utf-8") as fh:
                fh.write("It works %s.\n" % cite)
            self.assertTrue(any("[c02]" in p for p in ledger.scan(self.d, out, "public")), cite)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("It works [c01-c03].\n")
        self.assertTrue(any("[c03]" in p for p in ledger.scan(self.d, out, "public")))

    def test_scan_is_clean_for_an_honest_pitch(self):
        ledger.add(self.d, "Runs offline", "product", "MEASURED", "PUBLIC", evidence="e01")
        out = os.path.join(self.d, "outputs", "pitch.md")
        with open(out, "w", encoding="utf-8") as fh:
            fh.write("It runs with the network unplugged [c01]. We are looking for three pilot firms.\n")
        self.assertEqual(ledger.scan(self.d, out, "public"), [])


if __name__ == "__main__":
    unittest.main()
