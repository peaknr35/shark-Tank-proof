#!/usr/bin/env python3
"""Compiles the business plan for kill-or-build. Standard library only, no network.

Reads everything the other skills wrote into founder/ and assembles one
document, founder/business-plan.md, with a verdict at the top. The verdict is
computed from the numbers, never written by hand:

    Profitable   every check passes AND a real buyer has paid, signed or booked
                 (a MEASURED demand claim in founder/evidence/claims.csv)
    Unproven     every check passes on paper, but no real buyer has committed yet:
                 the numbers rest on estimates and simulated buyers only
    Not yet      at least one check fails (each failure is listed with its number)
    Incomplete   there are no numbers yet (run burn-test first)

The checks:
    1. each unit earns money before fixed costs        (founder/numbers.json)
    2. year 1 makes an operating profit                 (founder/numbers.json)
    3. break-even fits inside capacity, if capacity is given
    4. enough of the buyer panel buys                   (founder/panel/results.json, --min-buy-rate, default 25%)
    5. real demand: at least one MEASURED demand claim  (founder/evidence/claims.csv)

A simulated panel can fail a plan but never pass one. Only a real buyer can.

Labels travel through the math (receipts/rules.md, rule 10). Every money check
carries the weakest label of the inputs it was computed from, so a margin worked
out from a price the simulated panel picked is SIMULATED, not a fact. A money
check that passes on a SIMULATED input can still fail the plan, but it cannot
pass it: the verdict is at best Unproven until that input is real.

    python3 compile.py                      # reads ./founder, writes ./founder/business-plan.md
    python3 compile.py --dir path/to/founder --min-buy-rate 0.3
    python3 compile.py --check              # print the verdict and exit 0 (Profitable) or 1
"""

import argparse
import importlib.util
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SECTIONS = [  # (file in founder/, heading, which skill writes it)
    ("summary.md", "Summary", "kill-or-build"),
    ("evidence/claims.md", "What is real and what is a guess", "receipts"),
    ("board.md", "What the board said", "shark-board"),
    ("competitors.md", "The competition", "ground-truth"),
    ("panel/results.md", "The buyer panel", "truth-serum"),
    ("pricing.md", "Pricing", "litmus"),
    ("offer.md", "The offer", "dealbreaker"),
    ("cfo.md", "The numbers", "burn-test"),
    ("marketing.md", "Marketing", "signal"),
    ("brand.md", "Brand", "straight-talk"),
    ("ops.md", "Operations", "reality-check"),
    ("launch.md", "Launch plan", "prove-it"),
]


def _load(folder, name):
    path = os.path.join(HERE, "..", folder, name + ".py")
    spec = importlib.util.spec_from_file_location("founder_" + name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _load_unit_economics():
    return _load("burn-test", "unit_economics")


def _read(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return fh.read().strip()
    except FileNotFoundError:
        return None


def _strip_h1(text):
    lines = text.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
    # demote headings one level so they nest under the section heading
    return "\n".join(("#" + l) if l.startswith("#") else l for l in lines).strip()


def verdict(d, min_buy_rate=0.25):
    """Return (verdict, checks, numbers, panel, evidence). checks = [(ok, text)]."""
    checks = []
    numbers = panel = None
    ledger = _load("receipts", "ledger")
    evidence = ledger.summarise(ledger.load(d))
    simulated_passes = []  # money checks that pass only on a simulated input
    raw = _read(os.path.join(d, "numbers.json"))
    if raw:
        ue = _load_unit_economics()
        numbers = ue.analyse(json.loads(raw), ledger={r["id"]: r for r in ledger.load(d)})

        def money(ok, text, result):
            lab = numbers["labels"][result]
            checks.append((ok, "%s [%s]" % (text, ue.label_of(numbers, result))))
            if ok and lab["status"] == "SIMULATED":
                simulated_passes.append("%s rests on %s" % (ue.RESULT_NAMES[result], "; ".join(lab["weakest"])))

        u = numbers["unit"]
        c = numbers["contribution"]
        money(c > 0, "Each %s earns $%.2f before fixed costs (%.0f%% contribution)." % (u, c, numbers["contribution_pct"] * 100)
              if c > 0 else "Each %s LOSES $%.2f before fixed costs." % (u, -c), "contribution")
        y = numbers["year1_profit"]
        money(y > 0, "Year 1 operating profit: $%s." % "{:,.0f}".format(y) if y > 0
              else "Year 1 operating LOSS: $%s." % "{:,.0f}".format(-y), "year1_profit")
        be, cap = numbers["breakeven_per_day"], numbers["capacity_per_day"]
        if cap is not None:
            fits = not math.isinf(be) and be <= float(cap)
            money(fits, "Break-even is %s %ss a day against a capacity of %s." % (
                "never reached" if math.isinf(be) else "{:,.0f}".format(math.ceil(be)), u, cap), "fits_capacity")
        if numbers["acquisition_cost"] is not None:
            money(numbers["acquisition_fits"], "Winning a customer costs $%.2f against the $%.2f one is worth in year 1." % (
                numbers["acquisition_cost"], numbers["allowable_acquisition_cost"]), "acquisition_fits")
    raw = _read(os.path.join(d, "panel", "results.json"))
    if raw:
        panel = json.loads(raw)
        r = panel["buy_rate"]
        checks.append((r >= min_buy_rate, "%d of %d simulated buyers buy (%.0f%%, the bar is %.0f%%). Simulated:"
                       " an upper bound, never proof." % (panel["buys"], panel["answered"], r * 100, min_buy_rate * 100)))
    real = evidence["demand_measured"]
    demand_text = ("%d real commitment%s from buyers (paid, signed or booked)." % (real, "" if real == 1 else "s")
                   if real else "No real buyer has paid, signed or booked yet. Log the first with /receipts.")
    if numbers is None:
        v = "Incomplete"
    elif not all(ok for ok, _ in checks):
        v = "Not yet"
    elif not real or simulated_passes:
        v = "Unproven"
    else:
        v = "Profitable"
    checks.append((real > 0, demand_text))
    if numbers is not None:
        numbers["simulated_passes"] = simulated_passes
        numbers["stale_handoff"] = stale_handoff(d, numbers)
    return v, checks, numbers, panel, evidence


def stale_handoff(d, numbers):
    """Results whose label in handoff/06_burn-test.json no longer matches what the inputs give now.

    The verdict always uses the labels worked out now. A stale file means a source changed after /burn-test
    ran (a price claim relabelled, a quote added), so the CFO's report a person reads is out of date.
    """
    raw = _read(os.path.join(d, "handoff", "06_burn-test.json"))
    if not raw:
        return []
    stored = json.loads(raw).get("results", {})
    return ["%s: %s in the handoff, %s now" % (k, v.get("status"), numbers["labels"][k]["status"])
            for k, v in sorted(stored.items())
            if k in numbers["labels"] and v.get("status") != numbers["labels"][k]["status"]]


def compile_plan(d, min_buy_rate=0.25):
    idea = _read(os.path.join(d, "idea.md"))
    name = None
    if idea:
        first = idea.splitlines()[0]
        name = first[2:].strip() if first.startswith("# ") else None
    v, checks, numbers, panel, evidence = verdict(d, min_buy_rate)
    title = name or (numbers["business"] if numbers and numbers.get("business") else "Your business")
    L = ["# %s · Business plan" % title, ""]
    L.append("**Verdict: %s**" % v)
    L.append("")
    for ok, text in checks:
        L.append("- %s %s" % ("✓" if ok else "✗", text))
    if v == "Incomplete":
        L.append("- No numbers yet. Run /burn-test, then compile again.")
    sim = (numbers or {}).get("simulated_passes") or []
    if v == "Unproven" and sim:
        L += ["", "The math passes only on simulated inputs: %s. A number takes the weakest label of anything it"
              " was computed from, so these passes are SIMULATED and cannot make the plan Profitable. Replace each"
              " simulated input with a real one (a buyer paying the price, a supplier quote), point numbers.json"
              " at that claim, and compile again." % "; ".join(sim)]
    if v == "Unproven" and not evidence["demand_measured"]:
        L += ["", "The math works on paper. Nothing about demand is real yet: the numbers rest on estimates and"
              " simulated buyers. Run the real test in /prove-it, or get one pilot yes with /handshake,"
              " and log it with /receipts."]
    leaks = [e for e in _load("receipts", "ledger").check(d)[0] if "label leak" in e or "computed from" in e]
    if leaks:
        L += ["", "**Label leaks in the ledger** (a computed claim says more than its sources; fix with /receipts):"]
        L += ["- %s" % e for e in leaks]
    stale = (numbers or {}).get("stale_handoff") or []
    if stale:
        L += ["", "**Stale handoff** (a source changed after /burn-test ran, so `cfo.md` is out of date; the verdict"
              " above uses the labels as they stand now). Run /burn-test again:"]
        L += ["- %s" % s for s in stale]
    L.append("")
    if numbers:
        be = numbers["breakeven_per_day"]
        lab = lambda k: numbers["labels"][k]["status"]
        inp = lambda k: numbers["inputs"][k]["status"]
        L += ["| key number | | how we know |", "| --- | ---: | --- |",
              "| Price | $%.2f a %s | %s |" % (numbers["price"], numbers["unit"], inp("price")),
              "| Profit margin at plan | %.0f%% per %s | %s |" % (numbers["margin_at_plan"] * 100, numbers["unit"], lab("margin_at_plan")),
              "| Break-even | %s %ss a day | %s |" % ("never" if math.isinf(be) else "{:,.0f}".format(math.ceil(be)), numbers["unit"],
                                                 lab("breakeven_per_day")),
              "| Year 1 operating profit | $%s | %s |" % ("{:,.0f}".format(numbers["year1_profit"]), lab("year1_profit")),
              "| Startup spend | $%s | %s |" % ("{:,.0f}".format(numbers["startup"]), inp("startup")),
              "| Cash needed before it pays for itself | $%s | %s |" % ("{:,.0f}".format(numbers["cash_needed"]), lab("cash_needed")),
              "| Startup money earned back | %s | %s |" % ("month %d" % numbers["payback_month"] if numbers["payback_month"]
                                                          else "not in year 1", lab("payback_month"))]
        if panel:
            L.append("| Buyer panel (simulated) | %d buy · %d pass | SIMULATED |" % (panel["buys"], panel["passes"]))
        b = evidence["by_status"]
        L.append("| Real buyer commitments | %d | MEASURED |" % evidence["demand_measured"])
        L.append("| Claims in the ledger | %d measured · %d they said it · %d planned · %d simulated | |" % (
            b["MEASURED"], b["THEY SAID IT"], b["PLANNED"], b["SIMULATED"]))
        if evidence["cost_measured"] or evidence["cost_planned"]:
            L.append("| Costs backed by a quote or invoice | %d of %d | |" % (
                evidence["cost_measured"], evidence["cost_measured"] + evidence["cost_planned"]))
        L += ["", "_How we know: each result takes the weakest label of anything it was computed from. The full"
              " table is in the numbers section._"]
        L.append("")
    if idea:
        L += ["## The idea", "", _strip_h1(idea), ""]
    missing = []
    for fname, heading, skill in SECTIONS:
        text = _read(os.path.join(d, fname))
        if text:
            L += ["## %s" % heading, "", _strip_h1(text), ""]
        else:
            missing.append((heading, skill))
    if missing:
        L += ["## Not done yet", ""]
        for heading, skill in missing:
            L.append("- %s: run /%s" % (heading, skill))
        L.append("")
    L.append("_The panel and the board are simulated, and the numbers are projections from your inputs. Only the"
             " MEASURED and THEY SAID IT claims come from real people. Confirm demand with real customers and costs with"
             " real quotes before you spend. Not financial, legal or tax advice._")
    return v, "\n".join(L) + "\n"


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default="founder")
    ap.add_argument("--min-buy-rate", type=float, default=0.25)
    ap.add_argument("--check", action="store_true", help="print the verdict only; exit 0 if Profitable")
    ap.add_argument("--out", help="default: <dir>/business-plan.md")
    a = ap.parse_args(argv)
    if not os.path.isdir(a.dir):
        print("error: no %s/ folder here. Run the other Shark Tank Proof skills first." % a.dir, file=sys.stderr)
        return 2
    v, text = compile_plan(a.dir, a.min_buy_rate)
    if a.check:
        _, checks, numbers, _, _ = verdict(a.dir, a.min_buy_rate)
        print("Verdict: %s" % v)
        for ok, t in checks:
            print("  %s %s" % ("✓" if ok else "✗", t))
        for why in (numbers or {}).get("simulated_passes") or []:
            print("  ✗ Passes only on a simulated input, so it cannot make the plan Profitable: %s." % why)
        return 0 if v == "Profitable" else 1
    out = a.out or os.path.join(a.dir, "business-plan.md")
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(text)
    print("Verdict: %s. Wrote %s" % (v, out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
