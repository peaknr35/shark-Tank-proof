#!/usr/bin/env python3
"""Unit economics for burn-test. Standard library only, no network.

Takes one JSON file describing the business and prints the numbers a CFO would
check before a single dollar is spent: what one unit earns, the real margin at
the volume you plan, how many units a day you need to break even, what year 1
looks like month by month, and how long it takes to earn the startup money back.

    python3 unit_economics.py founder/numbers.json
    python3 unit_economics.py founder/numbers.json --out founder/cfo.md
    python3 unit_economics.py founder/numbers.json --json
    python3 unit_economics.py founder/numbers.json --price 7.00 --volume 0.8
    python3 unit_economics.py founder/numbers.json --ledger founder   # where claims.csv lives

The input (see example.json in this folder):

    business          name, for the report
    unit              what you sell one of: "cup", "order", "client-month"
    price             price per unit, before tax
    variable          [{label, cost}]  cost of ONE unit: ingredients, packaging,
                      shipping, card fees, a per-unit commission
    fixed_monthly     [{label, cost}]  costs you pay every month whatever you sell:
                      rent, salaries, software, insurance
    startup           [{label, cost}]  one-off spend before you open
    days_per_month    selling days in a month (default 30)
    capacity_per_day  the most units a day you can physically sell (optional)
    plan_per_day      the volume you plan for once you are up and running
    ramp_per_day      12 numbers: units a day in each month of year 1
                      (optional; default = plan_per_day every month)
    sources           where each top-level number came from, so its label can
                      travel: {"price": "c07", "ramp_per_day": "PLANNED"}. A value
                      is a ledger claim id, a status, or a list of either (the
                      weakest wins). Items in variable / fixed_monthly / startup
                      carry their own "claim" or "status".

How we know each result (rules.md, rule 10): every result takes the WEAKEST
label of the inputs it was computed from. A margin worked out from a price the
simulated buyer panel picked is SIMULATED, however clean the arithmetic. An
input with no source is PLANNED (rule 6). A claim id that is not in the ledger
cannot vouch for anything, so it counts as SIMULATED.

Every number in the report comes from that file. Nothing is looked up or
guessed. If a field is missing the tool says so instead of filling it in.

--price and --volume run a what-if without editing the file: --price replaces
the price, --volume scales every volume (0.8 = 20 percent fewer sales).
"""

import argparse
import csv
import json
import math
import os
import re
import sys

# Strongest first; the same order as receipts/ledger.py.
STRENGTH = {"MEASURED": 3, "THEY SAID IT": 2, "PLANNED": 1, "SIMULATED": 0}
# Which inputs each result is computed from.
# Break-even is fixed / contribution units a month: price and costs only. Selling days just restate it per
# day, so they do not lower its label; with a quoted price and every cost quoted, break-even is MEASURED.
# Comparing it with a daily capacity does use the days, so fits_capacity keeps them.
DEPENDS = {
    "contribution": ["price", "variable"],
    "breakeven_per_day": ["price", "variable", "fixed_monthly"],
    "margin_at_plan": ["price", "variable", "fixed_monthly", "days_per_month", "plan_per_day"],
    "year1_profit": ["price", "variable", "fixed_monthly", "days_per_month", "ramp_per_day"],
    "cash_needed": ["price", "variable", "fixed_monthly", "days_per_month", "ramp_per_day", "startup"],
    "payback_month": ["price", "variable", "fixed_monthly", "days_per_month", "ramp_per_day", "startup"],
    "fits_capacity": ["price", "variable", "fixed_monthly", "days_per_month", "capacity_per_day"],
}
RESULT_NAMES = {
    "contribution": "Contribution per unit", "breakeven_per_day": "Break-even a day",
    "margin_at_plan": "Profit margin at plan", "year1_profit": "Year 1 operating profit",
    "cash_needed": "Cash needed", "payback_month": "Startup money earned back",
    "fits_capacity": "Break-even inside capacity",
}


class NumbersError(Exception):
    pass


def _money(v):
    sign = "-" if v < 0 else ""
    return "%s$%s" % (sign, "{:,.2f}".format(abs(v)))


def _whole(v):
    sign = "-" if v < 0 else ""
    return "%s$%s" % (sign, "{:,.0f}".format(abs(round(v))))


def _sum(items, field):
    total = 0.0
    for i, it in enumerate(items or []):
        if not isinstance(it, dict) or "cost" not in it:
            raise NumbersError("%s[%d] needs a 'cost'" % (field, i))
        try:
            total += float(it["cost"])
        except (TypeError, ValueError):
            raise NumbersError("%s[%d].cost is not a number: %r" % (field, i, it["cost"]))
    return total


def load_ledger(d):
    """Claim rows by id from <d>/evidence/claims.csv, or {} when there is no ledger."""
    path = os.path.join(d, "evidence", "claims.csv") if d else ""
    if not path or not os.path.exists(path):
        return {}
    with open(path, encoding="utf-8", newline="") as fh:
        return {(r.get("id") or "").strip(): r for r in csv.DictReader(fh)}


def _weakest(pairs):
    """pairs = [(status, why)]. Return (status, [why of every pair at that status])."""
    floor = min((p[0] for p in pairs), key=lambda st: STRENGTH[st])
    return floor, [p[1] for p in pairs if p[0] == floor]


def _resolve(value, ledger, name, warnings):
    """One source value (claim id, status, or a list of either) -> [(status, why)]."""
    values = value if isinstance(value, list) else [value]
    out = []
    for v in values:
        v = str(v).strip()
        if re.match(r"^c\d+$", v):
            row = ledger.get(v)
            if row is None or (row.get("status") or "").strip() not in STRENGTH:
                warnings.append("%s cites %s, which is not in the ledger: counted as SIMULATED" % (name, v))
                out.append(("SIMULATED", "%s [%s, not in the ledger]" % (name, v)))
            else:
                out.append((row["status"].strip(), "%s [%s]" % (name, v)))
        elif v.upper() in STRENGTH:
            out.append((v.upper(), name))
        else:
            warnings.append("%s has source %r, which is neither a claim id nor a status: counted as SIMULATED" % (name, v))
            out.append(("SIMULATED", name))
    return out or [("PLANNED", "%s (no source)" % name)]


def input_labels(spec, ledger=None, what_if=None):
    """How we know each input: {input: (status, [why])}, plus warnings.

    what_if names inputs a what-if replaced or scaled: those are capped at PLANNED.
    """
    ledger = ledger or {}
    sources = spec.get("sources") or {}
    warnings, labels = [], {}
    for name in ("variable", "fixed_monthly", "startup"):
        pairs = []
        for i, it in enumerate(spec.get(name) or []):
            if not isinstance(it, dict):
                continue
            tag = "%s: %s" % (name, it.get("label", "item %d" % (i + 1)))
            vals = [x for x in (it.get("claim"), it.get("status")) if x]
            pairs += _resolve(vals, ledger, tag, warnings) if vals else [("PLANNED", "%s (no source)" % tag)]
        if name in sources:
            pairs += _resolve(sources[name], ledger, name, warnings)
        labels[name] = _weakest(pairs or [("PLANNED", "%s (no source)" % name)])
    for name in ("price", "days_per_month", "plan_per_day", "ramp_per_day", "capacity_per_day"):
        if name in sources:
            labels[name] = _weakest(_resolve(sources[name], ledger, name, warnings))
        elif name == "ramp_per_day" and "ramp_per_day" not in spec and "plan_per_day" in labels:
            labels[name] = labels["plan_per_day"]  # no ramp: every month is the plan volume
        else:
            labels[name] = ("PLANNED", ["%s (no source)" % name])
    if "plan_per_day" not in spec and "plan_per_day" not in sources:
        labels["plan_per_day"] = labels["ramp_per_day"]  # no plan: the last ramp month stands in
    for name in what_if or []:
        st, why = labels[name]
        if STRENGTH[st] > STRENGTH["PLANNED"]:
            labels[name] = ("PLANNED", ["%s (what-if)" % name])
    return labels, warnings


def result_labels(inputs):
    """Every result takes the weakest label of the inputs it was computed from."""
    out = {}
    for result, deps in DEPENDS.items():
        pairs = [(inputs[d][0], w) for d in deps for w in inputs[d][1]]
        st, why = _weakest(pairs)
        out[result] = {"status": st, "weakest": why}
    return out


def load(path):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        raise NumbersError("no such file: %s" % path)
    except json.JSONDecodeError as e:
        raise NumbersError("%s is not valid JSON: %s" % (path, e))


def analyse(spec, price=None, volume=1.0, ledger=None, what_if=None):
    """Return a dict of every number in the report, each with its label. Pure function, easy to test.

    ledger is {claim id: row} (load_ledger), used to look up the label of every cited input.
    """
    what_if = list(what_if or [])
    if price is not None:
        what_if.append("price")
    if volume != 1.0:
        what_if += ["plan_per_day", "ramp_per_day"]
    if "price" not in spec and price is None:
        raise NumbersError("'price' is missing")
    p = float(price if price is not None else spec["price"])
    if p <= 0:
        raise NumbersError("price must be above zero")
    days = float(spec.get("days_per_month", 30))
    var = _sum(spec.get("variable"), "variable")
    fixed = _sum(spec.get("fixed_monthly"), "fixed_monthly")
    startup = _sum(spec.get("startup"), "startup")

    if "plan_per_day" not in spec and "ramp_per_day" not in spec:
        raise NumbersError("give 'plan_per_day' or 'ramp_per_day' (12 numbers)")
    plan = float(spec.get("plan_per_day", 0)) * volume
    ramp = spec.get("ramp_per_day")
    if ramp is None:
        ramp = [plan] * 12
    else:
        if len(ramp) != 12:
            raise NumbersError("'ramp_per_day' needs 12 numbers, one per month (got %d)" % len(ramp))
        ramp = [float(v) * volume for v in ramp]
    if not plan:
        plan = ramp[-1]

    contribution = p - var
    contribution_pct = contribution / p
    breakeven_day = math.inf if contribution <= 0 else fixed / (contribution * days)
    plan_units_month = plan * days
    margin_at_plan = (contribution - (fixed / plan_units_month if plan_units_month else math.inf)) / p

    months = []
    cumulative = -startup
    payback_month = None
    for m, per_day in enumerate(ramp, start=1):
        units = per_day * days
        revenue = units * p
        variable_cost = units * var
        profit = revenue - variable_cost - fixed
        cumulative += profit
        if payback_month is None and cumulative >= 0:
            payback_month = m
        months.append({"month": m, "per_day": per_day, "units": units, "revenue": revenue,
                       "variable": variable_cost, "fixed": fixed, "profit": profit,
                       "cumulative": cumulative})
    year_profit = sum(m["profit"] for m in months)
    year_revenue = sum(m["revenue"] for m in months)
    # the cash you need: startup plus the deepest hole the monthly losses dig
    lowest = min([-startup] + [m["cumulative"] for m in months])
    cash_needed = -lowest

    capacity = spec.get("capacity_per_day")
    flags = []
    if contribution <= 0:
        flags.append("Each unit loses money before rent and salaries: the price is below the variable cost.")
    if capacity is not None and breakeven_day > float(capacity):
        flags.append("Break-even needs %.0f %ss a day but capacity is %s." % (breakeven_day, spec.get("unit", "unit"), capacity))
    if capacity is not None and plan > float(capacity):
        flags.append("The plan (%.0f a day) is above capacity (%s)." % (plan, capacity))
    if year_profit < 0:
        flags.append("Year 1 loses money on operations (%s)." % _whole(year_profit))
    if payback_month is None:
        flags.append("The startup spend is not earned back within year 1.")

    inputs, label_warnings = input_labels(spec, ledger, what_if)
    return {
        "labels": result_labels(inputs), "inputs": {k: {"status": v[0], "why": v[1]} for k, v in inputs.items()},
        "label_warnings": label_warnings,
        "business": spec.get("business", ""), "unit": spec.get("unit", "unit"),
        "price": p, "variable_per_unit": var, "contribution": contribution,
        "contribution_pct": contribution_pct, "fixed_monthly": fixed, "startup": startup,
        "plan_per_day": plan, "margin_at_plan": margin_at_plan, "breakeven_per_day": breakeven_day,
        "capacity_per_day": capacity, "year1_revenue": year_revenue, "year1_profit": year_profit,
        "year1_after_startup": year_profit - startup, "payback_month": payback_month,
        "cash_needed": cash_needed, "months": months, "flags": flags,
        "variable_items": spec.get("variable", []), "fixed_items": spec.get("fixed_monthly", []),
        "startup_items": spec.get("startup", []),
    }


def sensitivity(spec, ledger=None):
    """The three what-ifs every plan should survive. A what-if is at best PLANNED."""
    base = analyse(spec, ledger=ledger)
    rows = [("Base plan", base)]
    rows.append(("Price -10%", analyse(spec, price=base["price"] * 0.9, ledger=ledger)))
    rows.append(("Volume -20%", analyse(spec, volume=0.8, ledger=ledger)))
    worse = json.loads(json.dumps(spec))
    for it in worse.get("variable", []):
        it["cost"] = float(it["cost"]) * 1.15
    rows.append(("Unit costs +15%", analyse(worse, ledger=ledger, what_if=["variable"])))
    return rows


def label_of(a, result):
    """'SIMULATED: price [c07]' for a result in an analyse() output."""
    lab = a["labels"][result]
    return "%s: %s" % (lab["status"], "; ".join(lab["weakest"][:3]) + (" and more" if len(lab["weakest"]) > 3 else ""))


def report(spec, a, ledger=None):
    u = a["unit"]
    lab = lambda k: a["labels"][k]["status"]
    L = []
    L.append("# Unit economics: %s" % (a["business"] or "your business"))
    L.append("")
    L.append("Every number below comes from the input file. Nothing is looked up or guessed.")
    L.append("")
    L.append("## How we know each number")
    L.append("")
    L.append("Each result takes the weakest label of anything it was computed from (rules.md, rule 10), so a"
             " number that came out of a calculation is never stronger than its weakest input.")
    L.append("")
    L.append("| result | label | set by |")
    L.append("| --- | --- | --- |")
    for k in DEPENDS:
        if k == "fits_capacity" and a["capacity_per_day"] is None:
            continue
        L.append("| %s | %s | %s |" % (RESULT_NAMES[k], lab(k), "; ".join(a["labels"][k]["weakest"][:3])
                                       + (" and more" if len(a["labels"][k]["weakest"]) > 3 else "")))
    L.append("")
    if any(a["labels"][k]["status"] == "SIMULATED" for k in DEPENDS):
        L.append("**Simulated inputs sit under these results.** They can show a plan failing, never passing."
                 " Replace each simulated input with a real quote or a real sale, then run this again.")
        L.append("")
    for w in a["label_warnings"]:
        L.append("- Warning: %s" % w)
    if a["label_warnings"]:
        L.append("")
    L.append("## One %s" % u)
    L.append("")
    L.append("| line | per %s |" % u)
    L.append("| --- | ---: |")
    L.append("| Price | %s |" % _money(a["price"]))
    for it in a["variable_items"]:
        L.append("| %s | -%s |" % (it.get("label", "cost"), _money(float(it["cost"]))))
    L.append("| **Contribution** (what each %s leaves to pay the fixed costs) | **%s** (%.0f%%) [%s] |"
             % (u, _money(a["contribution"]), a["contribution_pct"] * 100, lab("contribution")))
    L.append("")
    L.append("## The margin that matters")
    L.append("")
    L.append("Fixed costs: %s a month (%s)." % (_whole(a["fixed_monthly"]), ", ".join(
        "%s %s" % (it.get("label", "cost"), _whole(float(it["cost"]))) for it in a["fixed_items"]) or "none given"))
    L.append("")
    be = a["breakeven_per_day"]
    L.append("- **Break-even: %s %ss a day.** Below that you lose money every month. [%s]" % (
        "never (each unit loses money)" if math.isinf(be) else "{:,.0f}".format(math.ceil(be)), u,
        lab("breakeven_per_day")))
    L.append("- **Profit margin at your plan** (%s a day): **%.0f%%** of every sale, after every cost. [%s]" % (
        "{:,.0f}".format(a["plan_per_day"]), a["margin_at_plan"] * 100, lab("margin_at_plan")))
    if a["capacity_per_day"] is not None:
        L.append("- Capacity: %s a day." % a["capacity_per_day"])
    L.append("")
    L.append("## Year 1, month by month")
    L.append("")
    L.append("| month | %ss a day | revenue | profit | cumulative (after %s startup) |" % (u, _whole(a["startup"])))
    L.append("| ---: | ---: | ---: | ---: | ---: |")
    for m in a["months"]:
        L.append("| %d | %s | %s | %s | %s |" % (m["month"], "{:,.0f}".format(m["per_day"]), _whole(m["revenue"]),
                                             _whole(m["profit"]), _whole(m["cumulative"])))
    L.append("")
    L.append("- **Year 1 operating profit: %s** on %s of revenue. [%s]" % (
        _whole(a["year1_profit"]), _whole(a["year1_revenue"]), lab("year1_profit")))
    L.append("- After the %s startup spend: %s." % (_whole(a["startup"]), _whole(a["year1_after_startup"])))
    L.append("- Startup money earned back: %s." % ("month %d" % a["payback_month"] if a["payback_month"] else "not within year 1"))
    L.append("- Cash you need before it pays for itself: **%s**. [%s]" % (_whole(a["cash_needed"]), lab("cash_needed")))
    L.append("")
    L.append("## What if")
    L.append("")
    L.append("| scenario | margin at plan | break-even a day | year 1 profit | label |")
    L.append("| --- | ---: | ---: | ---: | --- |")
    for name, s in sensitivity(spec, ledger):
        be = s["breakeven_per_day"]
        L.append("| %s | %.0f%% | %s | %s | %s |" % (name, s["margin_at_plan"] * 100,
                                                   "never" if math.isinf(be) else "{:,.0f}".format(math.ceil(be)),
                                                   _whole(s["year1_profit"]), s["labels"]["year1_profit"]["status"]))
    L.append("")
    if a["flags"]:
        L.append("## Red flags")
        L.append("")
        for f in a["flags"]:
            L.append("- %s" % f)
    else:
        L.append("No red flags in these numbers. They are only as good as the inputs: check every cost against a real quote.")
    return "\n".join(L) + "\n"


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("numbers", help="the business's numbers.json")
    ap.add_argument("--out", help="write the report here (markdown)")
    ap.add_argument("--json", action="store_true", help="print the numbers as JSON")
    ap.add_argument("--price", type=float, help="what-if price")
    ap.add_argument("--volume", type=float, default=1.0, help="what-if volume multiplier")
    ap.add_argument("--ledger", help="the folder with evidence/claims.csv (default: the numbers file's folder)")
    args = ap.parse_args(argv)
    try:
        spec = load(args.numbers)
        ledger = load_ledger(args.ledger or os.path.dirname(os.path.abspath(args.numbers)))
        what_if = []
        if args.price is not None:
            spec = dict(spec, price=args.price)
            what_if.append("price")
        if args.volume != 1.0:
            spec = dict(spec)
            if "plan_per_day" in spec:
                spec["plan_per_day"] = float(spec["plan_per_day"]) * args.volume
            if "ramp_per_day" in spec:
                spec["ramp_per_day"] = [float(v) * args.volume for v in spec["ramp_per_day"]]
            what_if += ["plan_per_day", "ramp_per_day"]
        if what_if:  # the what-if values are plans now: cap their labels in the file's own sources
            sources = dict(spec.get("sources") or {})
            for k in what_if:
                sources[k] = ([sources[k]] if k in sources and not isinstance(sources[k], list)
                              else list(sources.get(k, []))) + ["PLANNED"]
            spec = dict(spec, sources=sources)
        a = analyse(spec, ledger=ledger)
    except NumbersError as e:
        print("error: %s" % e, file=sys.stderr)
        return 2
    if args.json:
        out = {k: v for k, v in a.items() if not k.endswith("_items")}
        out["breakeven_per_day"] = None if math.isinf(out["breakeven_per_day"]) else out["breakeven_per_day"]
        print(json.dumps(out, indent=1))
        return 0
    text = report(spec, a, ledger)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as fh:
            fh.write(text)
        print("wrote %s" % args.out)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
