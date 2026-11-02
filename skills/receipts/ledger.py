#!/usr/bin/env python3
"""The evidence ledger for receipts. Standard library only, no network.

Every skill in the pack writes what it found as a claim with two labels kept
apart: how we know it (status) and who may see it (use). Pitches and the plan
read only from here, so a guess can never turn into a fact on the way out.

    status   MEASURED       counted, timed, paid, signed (needs an evidence id)
             THEY SAID IT   a real person said it in writing or on a recording (needs an evidence id)
             PLANNED        an estimate, a projection, a goal
             SIMULATED      a buyer panel, a board memo, any model output. Never proof.
    use      PUBLIC, ANONYMISED, ASK FIRST, PRIVATE
    kind     demand, price, cost, product, market, team, other

Files, all under <dir>/evidence/:
    claims.csv        the ledger (id,claim,number,kind,status,use,evidence,checked,by)
    evidence-log.md   one table row per original: | e01 | what | where from | date | use |
    claims.md         written by `summary`, grouped by status
    summary.json      written by `summary`, read by kill-or-build

    python3 ledger.py init                           # make founder/evidence, opportunities, outputs
    python3 ledger.py add --claim "3 firms paid a deposit" --kind demand --status MEASURED --use ANONYMISED --evidence e04
    python3 ledger.py check                          # exit 1 if any claim breaks a rule
    python3 ledger.py summary                        # claims.md + summary.json
    python3 ledger.py gate --audience public         # what a pitch to this audience may use
    python3 ledger.py scan founder/outputs/2026-11-02-acme.md --audience public
"""

import argparse
import csv
import datetime
import json
import os
import re
import sys

STATUSES = ["MEASURED", "THEY SAID IT", "PLANNED", "SIMULATED"]
USES = ["PUBLIC", "ANONYMISED", "ASK FIRST", "PRIVATE"]
KINDS = ["demand", "price", "cost", "product", "market", "team", "other"]
FIELDS = ["id", "claim", "number", "kind", "status", "use", "evidence", "checked", "by"]
NEEDS_EVIDENCE = ("MEASURED", "THEY SAID IT")
AUDIENCES = {  # which use labels each audience may see
    "public": ["PUBLIC"],
    "anonymised": ["PUBLIC", "ANONYMISED"],
    "permission": ["PUBLIC", "ANONYMISED", "ASK FIRST"],  # only once the person said yes, in people.md
}
STALE_DAYS = 90
# Words that claim proof. Fine when a MEASURED demand claim backs them, a red flag when none does.
HYPE = ["validated", "proven", "guaranteed", "traction", "customers love", "strong demand",
        "high demand", "everyone wants", "market wants", "will pay", "can't lose", "no-brainer"]

EVIDENCE_LOG = """# Evidence log

One row per original (a screenshot, an email, a receipt, a recording, a signed page).
The file itself lives in this folder; claims in claims.csv point here by id.

| Id | What it is | Where it came from | Date | Use |
|---|---|---|---|---|
<!-- Example: | e01 | Screenshot of the before and after timings | My own test run | 2026-10-24 | PUBLIC | -->
<!-- Example: | e02 | Client email saying it saved them a day | Email from the client | 2026-10-20 | ASK FIRST | -->
"""

PEOPLE = """# People

Real people only. A simulated buyer never goes here.

| Name | Who they are | What we did together | What they said | Can I name them? |
|---|---|---|---|---|
<!-- Example: | J. Doe | Client / partner / cohort member / mentor | Ran the build on a week of their orders | "It saved me Monday mornings" | Asked 24 Oct, yes | -->

Peers count. Someone in your cohort or network who runs your build on their own
work and tells you what happened is a real case study.
"""


class LedgerError(Exception):
    pass


def _ev_dir(d):
    return os.path.join(d, "evidence")


def _claims_path(d):
    return os.path.join(_ev_dir(d), "claims.csv")


def init(d):
    made = []
    for sub in ("evidence", os.path.join("evidence", "calls"), "work", "opportunities", "outputs"):
        p = os.path.join(d, sub)
        if not os.path.isdir(p):
            os.makedirs(p)
            made.append(p)
    for path, body in ((_claims_path(d), ",".join(FIELDS) + "\n"),
                       (os.path.join(_ev_dir(d), "evidence-log.md"), EVIDENCE_LOG),
                       (os.path.join(_ev_dir(d), "people.md"), PEOPLE)):
        if not os.path.exists(path):
            with open(path, "w", encoding="utf-8", newline="") as fh:
                fh.write(body)
            made.append(path)
    return made


def load(d):
    path = _claims_path(d)
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    return [{k: (r.get(k) or "").strip() for k in FIELDS} for r in rows]


def evidence_ids(d):
    path = os.path.join(_ev_dir(d), "evidence-log.md")
    if not os.path.exists(path):
        return set()
    ids = set()
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\|\s*(e\d+)\s*\|", line.strip())
            if m:
                ids.add(m.group(1))
    return ids


def _next_id(rows):
    nums = [int(r["id"][1:]) for r in rows if re.match(r"^c\d+$", r["id"])]
    return "c%02d" % (max(nums) + 1 if nums else 1)


def add(d, claim, kind, status, use, number="", evidence="", checked=None, by=""):
    row = {"id": "", "claim": claim, "number": number, "kind": kind, "status": status, "use": use,
           "evidence": evidence, "checked": checked or datetime.date.today().isoformat(), "by": by}
    problems = problems_for(row, evidence_ids(d))
    if problems:
        raise LedgerError("; ".join(problems))
    rows = load(d)
    row["id"] = _next_id(rows)
    if not os.path.exists(_claims_path(d)):
        init(d)
    with open(_claims_path(d), "a", encoding="utf-8", newline="") as fh:
        csv.DictWriter(fh, fieldnames=FIELDS).writerow(row)
    return row


def problems_for(r, ev_ids, today=None):
    out = []
    if not r["claim"]:
        out.append("no claim text")
    if r["status"] not in STATUSES:
        out.append("status %r is not one of %s" % (r["status"], ", ".join(STATUSES)))
    if r["use"] not in USES:
        out.append("use %r is not one of %s" % (r["use"], ", ".join(USES)))
    if r["kind"] not in KINDS:
        out.append("kind %r is not one of %s" % (r["kind"], ", ".join(KINDS)))
    if r["status"] in NEEDS_EVIDENCE:
        if not r["evidence"]:
            out.append("%s needs an evidence id from evidence-log.md" % r["status"])
        else:
            for e in re.split(r"[ ;,]+", r["evidence"]):
                if e and e not in ev_ids:
                    out.append("evidence %s is not in evidence-log.md" % e)
    try:
        datetime.date.fromisoformat(r["checked"])
    except ValueError:
        out.append("checked %r is not a YYYY-MM-DD date" % r["checked"])
    return out


def check(d, today=None):
    """Return (errors, warnings), each a list of strings."""
    today = today or datetime.date.today()
    rows, ev = load(d), evidence_ids(d)
    errors, warnings, seen = [], [], set()
    for r in rows:
        tag = r["id"] or "(no id)"
        if r["id"] in seen:
            errors.append("%s: duplicate id" % tag)
        seen.add(r["id"])
        errors += ["%s: %s" % (tag, p) for p in problems_for(r, ev)]
        try:
            age = (today - datetime.date.fromisoformat(r["checked"])).days
            if age > STALE_DAYS and r["status"] != "SIMULATED":
                warnings.append("%s: last checked %d days ago, check it again before you pitch it" % (tag, age))
        except ValueError:
            pass
    return errors, warnings


def is_commitment(r):
    """A MEASURED demand claim that counts as a real yes. A logged no ("0", "0 of 10", "none") does not."""
    if r["kind"] != "demand" or r["status"] != "MEASURED":
        return False
    return not re.match(r"^\s*(0+(\.0+)?|none|no)(\s|$|\b)", r["number"].lower())


def summarise(rows):
    count = {s: 0 for s in STATUSES}
    by_kind = {}
    for r in rows:
        if r["status"] in count:
            count[r["status"]] += 1
        k = by_kind.setdefault(r["kind"], {s: 0 for s in STATUSES})
        if r["status"] in k:
            k[r["status"]] += 1
    real = count["MEASURED"] + count["THEY SAID IT"]
    demand = by_kind.get("demand", {s: 0 for s in STATUSES})
    return {
        "claims": len(rows),
        "by_status": count,
        "by_kind": by_kind,
        "real_share": (real / float(len(rows))) if rows else 0.0,
        "demand_measured": sum(1 for r in rows if is_commitment(r)),
        "demand_refusals": demand["MEASURED"] - sum(1 for r in rows if is_commitment(r)),
        "demand_said": demand["THEY SAID IT"],
        "demand_simulated": demand["SIMULATED"],
        "cost_measured": by_kind.get("cost", {}).get("MEASURED", 0),
        "cost_planned": by_kind.get("cost", {}).get("PLANNED", 0),
    }


def write_summary(d):
    rows = load(d)
    s = summarise(rows)
    L = ["# The evidence", ""]
    b = s["by_status"]
    L.append("**%d claims: %d measured · %d they said it · %d planned · %d simulated.**"
             % (s["claims"], b["MEASURED"], b["THEY SAID IT"], b["PLANNED"], b["SIMULATED"]))
    L.append("")
    if s["demand_measured"]:
        L.append("Real demand: %d measured (money, a signature or a booking)." % s["demand_measured"])
    else:
        L.append("**No real buyer has paid, signed or booked yet.** Everything about demand is a guess or a"
                 " simulation until one does.")
    L.append("")
    for status in STATUSES:
        group = [r for r in rows if r["status"] == status]
        if not group:
            continue
        L += ["## %s" % status.capitalize(), "", "| Id | Claim | Number | Kind | Use | Evidence | Checked |",
              "|---|---|---|---|---|---|---|"]
        for r in group:
            L.append("| %s | %s | %s | %s | %s | %s | %s |" % (
                r["id"], r["claim"].replace("|", "/"), r["number"].replace("|", "/"), r["kind"], r["use"],
                r["evidence"] or "", r["checked"]))
        L.append("")
    L.append("_MEASURED and THEY SAID IT come from real people and real files. PLANNED is a goal. SIMULATED is a"
             " model's opinion and never appears in a pitch as proof._")
    with open(os.path.join(_ev_dir(d), "claims.md"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    with open(os.path.join(_ev_dir(d), "summary.json"), "w", encoding="utf-8") as fh:
        json.dump(s, fh, indent=2)
    return s


def gate(rows, audience):
    """Claims a pitch to this audience may use. SIMULATED and PRIVATE never pass."""
    allowed = AUDIENCES[audience]
    return [r for r in rows if r["status"] != "SIMULATED" and r["use"] in allowed]


def scan(d, path, audience):
    """Check a pitch file: every [c01] it cites must pass the gate; hype needs measured demand behind it."""
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    rows = {r["id"]: r for r in load(d)}
    ok_ids = {r["id"] for r in gate(rows.values(), audience)}
    problems = []
    cited = set()
    for group in re.findall(r"\[(c\d+(?:\s*[,;-]\s*c\d+)*)\]", text):  # [c01], [c01, c04], [c01-c03]
        for a, b in re.findall(r"c(\d+)\s*-\s*c(\d+)", group):
            cited.update("c%02d" % n for n in range(int(a), int(b) + 1))
        cited.update(re.findall(r"c\d+", group))
    cited = sorted(cited)
    for cid in cited:
        r = rows.get(cid)
        if r is None:
            problems.append("[%s] is cited but not in the ledger" % cid)
        elif cid not in ok_ids:
            problems.append("[%s] is %s / %s and may not go to a %s audience" % (cid, r["status"], r["use"], audience))
        elif r["status"] == "PLANNED":
            problems.append("[%s] is PLANNED: make sure the pitch says it as a goal, not a result (info)" % cid)
    if not summarise(list(rows.values()))["demand_measured"]:
        low = text.lower()
        for w in HYPE:
            if w in low:
                problems.append("says %r but no real buyer has paid or signed yet" % w)
    if not cited:
        problems.append("cites no claims; every fact in a pitch should carry its [c..] id")
    return problems


def main(argv=None):
    if hasattr(sys.stdout, "reconfigure"):  # Windows consoles default to cp1252
        sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dir", default="founder")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("init")
    a_add = sub.add_parser("add")
    a_add.add_argument("--claim", required=True)
    a_add.add_argument("--kind", required=True, choices=KINDS)
    a_add.add_argument("--status", required=True, choices=STATUSES)
    a_add.add_argument("--use", required=True, choices=USES)
    a_add.add_argument("--number", default="")
    a_add.add_argument("--evidence", default="")
    a_add.add_argument("--checked")
    a_add.add_argument("--by", default="")
    sub.add_parser("check")
    sub.add_parser("summary")
    a_gate = sub.add_parser("gate")
    a_gate.add_argument("--audience", required=True, choices=sorted(AUDIENCES))
    a_scan = sub.add_parser("scan")
    a_scan.add_argument("file")
    a_scan.add_argument("--audience", required=True, choices=sorted(AUDIENCES))
    a = ap.parse_args(argv)

    if a.cmd == "init":
        made = init(a.dir)
        print("Made %s" % ", ".join(made) if made else "Already there, nothing changed.")
        return 0
    if a.cmd == "add":
        try:
            r = add(a.dir, a.claim, a.kind, a.status, a.use, a.number, a.evidence, a.checked, a.by)
        except LedgerError as e:
            print("refused: %s" % e, file=sys.stderr)
            return 1
        print("%s %s / %s: %s" % (r["id"], r["status"], r["use"], r["claim"]))
        return 0
    if a.cmd == "check":
        errors, warnings = check(a.dir)
        for e in errors:
            print("error: %s" % e)
        for w in warnings:
            print("warning: %s" % w)
        if not errors:
            print("%d claims, no errors." % len(load(a.dir)))
        return 1 if errors else 0
    if a.cmd == "summary":
        s = write_summary(a.dir)
        b = s["by_status"]
        print("%d claims: %d measured, %d they said it, %d planned, %d simulated. Real demand: %d."
              % (s["claims"], b["MEASURED"], b["THEY SAID IT"], b["PLANNED"], b["SIMULATED"], s["demand_measured"]))
        return 0
    if a.cmd == "gate":
        for r in gate(load(a.dir), a.audience):
            print("[%s] %s | %s | %s%s" % (r["id"], r["status"], r["use"], r["claim"],
                                           (" (" + r["number"] + ")") if r["number"] else ""))
        return 0
    if a.cmd == "scan":
        problems = scan(a.dir, a.file, a.audience)
        hard = [p for p in problems if not p.endswith("(info)")]
        for p in problems:
            print("- %s" % p)
        if not problems:
            print("Clean: every cited claim may go to a %s audience." % a.audience)
        return 1 if hard else 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
