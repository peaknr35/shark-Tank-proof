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
    from     the claim ids a number was computed from. A computed claim takes the
             WEAKEST status of its sources (rules.md, rule 10): a margin worked out
             from a simulated price is SIMULATED, however clean the arithmetic.

Files, all under <dir>/evidence/:
    claims.csv        the ledger (id,claim,number,kind,status,use,evidence,checked,by,from,commitment)
    evidence-log.md   one table row per original: | e01 | what | where from | date | use |
                      a buyer's row must name what backs it: a receipt or invoice (paid, deposit), a signed
                      page (signed), a booking (booked), the email (intro). The file itself is not opened.
    claims.md         written by `summary`, grouped by status
    summary.json      written by `summary`, read by kill-or-build

    python3 ledger.py init                           # make founder/evidence, opportunities, outputs
    python3 ledger.py add --claim "3 firms paid a deposit" --kind demand --status MEASURED --use ANONYMISED --number 3 --commitment deposit --evidence e04
    python3 ledger.py add --claim "Contribution per cup" --kind cost --use PRIVATE --number "$4.76" --from c07,c08
                                                     # no --status: it takes the weakest label of c07 and c08
    python3 ledger.py label c07,c08                  # the label a number computed from these would carry
    python3 ledger.py trace c09                      # where a computed claim came from, down to the originals
    python3 ledger.py check                          # exit 1 if any claim breaks a rule (including a label leak)
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
FIELDS = ["id", "claim", "number", "kind", "status", "use", "evidence", "checked", "by", "from", "commitment"]
# What a real yes is (rules.md, rule 3): money, a signature, real time or reputation. A MEASURED demand claim names
# which one; a signup, a like, a follow or a download is none of them.
COMMITMENTS = ["paid", "deposit", "signed", "booked", "intro"]
# Words that sound like interest, not commitment. A buyer claim that uses one is refused, whatever --commitment says:
# "signed" is a commitment, "signups" is not. Log the signups as their own claim, kind other.
NOT_A_COMMITMENT = re.compile(r"\b(sign[- ]?ups?|waitlist|wait list|subscribers?|followers?|likes?|views?|downloads?|"
                              r"visits?|visitors|clicks?|opt[- ]?ins?|emails? collected|interested|free trials?)\b", re.I)
# What the evidence row for a buyer has to name, by commitment. The commitment is a word the founder types; the row in
# evidence-log.md ("What it is" and "Where it came from") has to say what original backs it: a receipt or invoice for
# money, a signed page for a signature, a calendar invite for a booking, the email or message for an intro.
_MONEY = (r"receipts?|invoices?|payments?|paid|transactions?|bank|statements?|stripe|paypal|square|shopify|"
          r"checkout|(pre-?)?orders?|charges?|transfers?|venmo|wise|deposits?")
PROOF = {
    "paid": _MONEY,
    "deposit": _MONEY,
    "signed": r"signed|signatures?|countersigned|contracts?|agreements?|loi|letters? of intent|docusign|"
              r"purchase orders?|po",
    "booked": r"bookings?|booked|calendar|invites?|invitations?|appointments?|meetings?|scheduled|reservations?",
    "intro": r"intros?|introductions?|introduced|referrals?|referred|emails?|messages?|forwarded",
}
PROOF = {k: re.compile(r"\b(%s)\b" % v, re.I) for k, v in PROOF.items()}
PROOF_NAMES = {
    "paid": "a receipt, invoice, payment or order export",
    "deposit": "a receipt, invoice, payment or order export",
    "signed": "a signed page, contract, agreement, LOI or purchase order",
    "booked": "a booking, calendar invite or appointment",
    "intro": "the introduction email or message",
}
# Most private last. A number computed from others may be shown to no wider an audience than its most private source.
USE_RANK = {"PUBLIC": 0, "ANONYMISED": 1, "ASK FIRST": 2, "PRIVATE": 3}
NEEDS_EVIDENCE = ("MEASURED", "THEY SAID IT")
# Strongest first. A number computed from several others takes the weakest of their labels.
STRENGTH = {"MEASURED": 3, "THEY SAID IT": 2, "PLANNED": 1, "SIMULATED": 0}
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


def weakest(statuses):
    """The weakest label in statuses (rules.md, rule 10). Anything unknown counts as SIMULATED."""
    statuses = list(statuses)
    if not statuses:
        return None
    return min(statuses, key=lambda s: STRENGTH.get(s, -1)) if all(s in STRENGTH for s in statuses) else "SIMULATED"


def split_ids(text):
    return [x for x in re.split(r"[ ;,]+", text or "") if x]


def derived_status(rows_by_id, ids):
    """(status, weakest_ids, missing_ids) for a number computed from these claims.

    A source that is not in the ledger cannot vouch for anything, so it counts as SIMULATED.
    """
    ids = split_ids(ids) if isinstance(ids, str) else list(ids)
    missing = [i for i in ids if i not in rows_by_id]
    labels = {i: (rows_by_id[i]["status"] if i in rows_by_id else "SIMULATED") for i in ids}
    st = weakest(labels.values())
    return st, [i for i in ids if labels[i] == st], missing


def trace(rows_by_id, cid, depth=0, seen=()):
    """Lines showing where a claim came from: its label, then each claim in its from column, down to the originals."""
    pad = "  " * depth
    r = rows_by_id.get(cid)
    if r is None:
        return ["%s[%s] not in the ledger: counts as SIMULATED" % (pad, cid)]
    if cid in seen:
        return ["%s[%s] loops back on itself: counts as SIMULATED" % (pad, cid)]
    sources = split_ids(r.get("from", ""))
    lines = ["%s[%s] %s: %s%s%s" % (pad, cid, r["status"], r["claim"], (" (" + r["number"] + ")") if r["number"] else "",
                                    (" evidence " + r["evidence"]) if r["evidence"] else ("" if sources else " (no source)"))]
    for s in sources:
        lines += trace(rows_by_id, s, depth + 1, seen + (cid,))
    return lines


def count(number):
    """The number of buyers a demand claim records: the first whole number in it, or None if there is none.

    "62", "62 at $6.50" and "2 of 5" give 62, 62 and 2. "0 of 10" gives 0. "", "not yet", "zero", "n/a" give None.
    """
    m = re.search(r"\d[\d,]*", number or "")
    return int(m.group(0).replace(",", "")) if m else None


def most_private(uses):
    uses = [u for u in uses if u in USE_RANK]
    return max(uses, key=USE_RANK.get) if uses else None


def _ev_dir(d):
    return os.path.join(d, "evidence")


def _claims_path(d):
    return os.path.join(_ev_dir(d), "claims.csv")


def init(d):
    made = []
    for sub in ("evidence", os.path.join("evidence", "calls"), "work", "opportunities", "outputs", "handoff"):
        p = os.path.join(d, sub)
        if not os.path.isdir(p):
            os.makedirs(p)
            made.append(p)
    context = os.path.join(d, "CONTEXT.md")  # the stage map: which skill reads, writes and hands on what
    if not os.path.exists(context):
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "templates", "CONTEXT.md"),
                  encoding="utf-8") as fh:
            body = fh.read()
        with open(context, "w", encoding="utf-8") as fh:
            fh.write(body)
        made.append(context)
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
    """{evidence id: "what it is | where it came from"} for every row of evidence-log.md."""
    path = os.path.join(_ev_dir(d), "evidence-log.md")
    if not os.path.exists(path):
        return {}
    ids = {}
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            m = re.match(r"^\|\s*(e\d+)\s*\|", line)
            if m:
                cells = [c.strip() for c in line.strip("|").split("|")]
                ids[m.group(1)] = " | ".join(cells[1:3])
    return ids


def _next_id(rows):
    nums = [int(r["id"][1:]) for r in rows if re.match(r"^c\d+$", r["id"])]
    return "c%02d" % (max(nums) + 1 if nums else 1)


def _header(d):
    path = _claims_path(d)
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", newline="") as fh:
        return next(csv.reader(fh), [])


def add(d, claim, kind, status, use, number="", evidence="", checked=None, by="", derived_from="", commitment=""):
    """Log one claim. With derived_from (claim ids) and no status, the status is the weakest of the sources.

    A status stronger than the weakest source is refused: that is the label leak rule 10 stops.
    """
    rows = load(d)
    by_id = {r["id"]: r for r in rows}
    derived_from = ",".join(split_ids(derived_from))
    if derived_from:
        floor, weak_ids, _ = derived_status(by_id, derived_from)
        if not status:
            status = floor
    row = {"id": "", "claim": claim, "number": number, "kind": kind, "status": status or "", "use": use,
           "evidence": evidence, "checked": checked or datetime.date.today().isoformat(), "by": by,
           "from": derived_from, "commitment": commitment}
    problems = problems_for(row, evidence_ids(d), by_id)
    if problems:
        raise LedgerError("; ".join(problems))
    row["id"] = _next_id(rows)
    if not os.path.exists(_claims_path(d)):
        init(d)
    if _header(d) != FIELDS:  # an older ledger without the "from" column: rewrite it with the new header
        with open(_claims_path(d), "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=FIELDS)
            w.writeheader()
            w.writerows(rows)
    with open(_claims_path(d), "a", encoding="utf-8", newline="") as fh:
        csv.DictWriter(fh, fieldnames=FIELDS).writerow(row)
    return row


def problems_for(r, ev_ids, rows_by_id=None, today=None):
    out = []
    sources = split_ids(r.get("from", ""))
    if not r["claim"]:
        out.append("no claim text")
    if r["status"] not in STATUSES:
        out.append("status %r is not one of %s" % (r["status"], ", ".join(STATUSES)))
    if r["use"] not in USES:
        out.append("use %r is not one of %s" % (r["use"], ", ".join(USES)))
    if r["kind"] not in KINDS:
        out.append("kind %r is not one of %s" % (r["kind"], ", ".join(KINDS)))
    if sources and rows_by_id is not None:
        floor, weak_ids, missing = derived_status(rows_by_id, sources)
        for m in missing:
            out.append("computed from %s, which is not in the ledger" % m)
        if r["status"] in STRENGTH and STRENGTH[r["status"]] > STRENGTH[floor]:
            out.append("label leak: computed from %s (%s), so it can be at most %s, not %s"
                       % (", ".join(weak_ids), floor, floor, r["status"]))
        tightest = most_private(rows_by_id[s]["use"] for s in sources if s in rows_by_id)
        if tightest and r["use"] in USE_RANK and USE_RANK[r["use"]] < USE_RANK[tightest]:
            out.append("use leak: computed from a %s claim, so it may be shown at most as %s, not %s"
                       % (tightest, tightest, r["use"]))
    commitment = (r.get("commitment") or "").strip()
    if commitment and commitment not in COMMITMENTS:
        out.append("commitment %r is not one of %s" % (commitment, ", ".join(COMMITMENTS)))
    if commitment and r["kind"] != "demand":
        out.append("only a demand claim has a commitment")
    if r["kind"] == "demand" and r["status"] == "MEASURED":
        n = count(r["number"])
        if n is None:
            out.append("MEASURED demand needs a number: how many paid, signed or booked (0 for a logged no)")
        elif n > 0 and commitment not in COMMITMENTS:
            out.append("MEASURED demand needs --commitment (%s): a signup, a like or a waitlist is not a commitment"
                       % " / ".join(COMMITMENTS))
        if n and sources and not r["evidence"]:
            out.append("a real buyer needs its own evidence id: a computed claim cannot count as a buyer")
        word = NOT_A_COMMITMENT.search(r["claim"])
        if n and word:
            out.append("%r is interest, not a commitment, whatever --commitment says. Log the %s as their own claim"
                       " (kind other) and the buyers as a claim that says what they did" % (word.group(0), word.group(0)))
        if n and commitment in PROOF and r["evidence"] and isinstance(ev_ids, dict):
            known = [e for e in split_ids(r["evidence"]) if e in ev_ids]
            if known and not any(PROOF[commitment].search(ev_ids[e]) for e in known):
                out.append("a %s buyer needs evidence that names %s: %s in evidence-log.md does not"
                           % (commitment, PROOF_NAMES[commitment], ", ".join(known)))
    if r["status"] in NEEDS_EVIDENCE:
        if not r["evidence"] and sources:
            pass  # a computed claim carries the evidence of the claims it came from
        elif not r["evidence"]:
            out.append("%s needs an evidence id from evidence-log.md" % r["status"])
        else:
            for e in split_ids(r["evidence"]):
                if e and e not in ev_ids:
                    out.append("evidence %s is not in evidence-log.md" % e)
    try:
        datetime.date.fromisoformat(r["checked"])
    except ValueError:
        out.append("checked %r is not a YYYY-MM-DD date" % r["checked"])
    return out


def check(d, today=None):
    """Return (errors, warnings), each a list of strings."""
    errors, warnings, _ = _check_rows(d, today)
    return errors, warnings


def load_checked(d, today=None):
    """The claims every verdict reads: (rows, rejected).

    Each claim that breaks a rule (no evidence, an evidence id that is not in the log, a label or use leak, a
    demand claim with no commitment) counts as SIMULATED until it is fixed, so a hand-edited claims.csv cannot
    make anything look real. rejected lists "c04: why" for each one. load() is the raw file; this is the truth.
    """
    _, _, bad = _check_rows(d, today)
    rows = []
    for r in load(d):
        if r["id"] in bad and r["status"] != "SIMULATED":
            r = dict(r, status="SIMULATED", rejected="; ".join(bad[r["id"]]))
        rows.append(r)
    rejected = ["%s: %s" % (cid, "; ".join(p)) for cid, p in bad.items()]
    return rows, rejected


def _check_rows(d, today=None):
    today = today or datetime.date.today()
    rows, ev = load(d), evidence_ids(d)
    by_id = {r["id"]: r for r in rows}
    errors, warnings, seen, bad = [], [], set(), {}
    for r in rows:
        tag = r["id"] or "(no id)"
        if r["id"] in seen:
            errors.append("%s: duplicate id" % tag)
            bad.setdefault(r["id"], []).append("duplicate id")
        seen.add(r["id"])
        problems = problems_for(r, ev, by_id)
        if problems:
            bad.setdefault(r["id"], []).extend(problems)
        errors += ["%s: %s" % (tag, p) for p in problems]
        try:
            age = (today - datetime.date.fromisoformat(r["checked"])).days
            if age > STALE_DAYS and r["status"] != "SIMULATED":
                warnings.append("%s: last checked %d days ago, check it again before you pitch it" % (tag, age))
        except ValueError:
            pass
    return errors, warnings, bad


def is_commitment(r):
    """A MEASURED demand claim that counts as a real yes: a named commitment (paid, deposit, signed, booked, intro),
    at least one buyer counted in its number, and its own evidence. A logged no ("0 of 10"), a blank or "not yet",
    and a signup with no commitment do not count. Read rows through load_checked so a broken claim is SIMULATED."""
    if r["kind"] != "demand" or r["status"] != "MEASURED":
        return False
    if (r.get("commitment") or "").strip() not in COMMITMENTS or not r.get("evidence"):
        return False
    n = count(r["number"])
    return n is not None and n > 0


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
    rows, rejected = load_checked(d)
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
    if rejected:
        L += ["**Rejected, counted as SIMULATED until fixed:**", ""] + ["- %s" % x for x in rejected] + [""]
    for status in STATUSES:
        group = [r for r in rows if r["status"] == status]
        if not group:
            continue
        L += ["## %s" % status.capitalize(), "", "| Id | Claim | Number | Kind | Use | Evidence | From | Checked |",
              "|---|---|---|---|---|---|---|---|"]
        for r in group:
            L.append("| %s | %s | %s | %s | %s | %s | %s | %s |" % (
                r["id"], r["claim"].replace("|", "/"), r["number"].replace("|", "/"), r["kind"], r["use"],
                r["evidence"] or "", r["from"] or "", r["checked"]))
        L.append("")
    L.append("_MEASURED and THEY SAID IT come from real people and real files. PLANNED is a goal. SIMULATED is a"
             " model's opinion and never appears in a pitch as proof. A claim with a From column was computed from"
             " those claims and carries the weakest of their labels._")
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
    rows = {r["id"]: r for r in load_checked(d)[0]}
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
    a_add.add_argument("--status", choices=STATUSES, help="leave out with --from to take the weakest source label")
    a_add.add_argument("--use", required=True, choices=USES)
    a_add.add_argument("--number", default="")
    a_add.add_argument("--evidence", default="")
    a_add.add_argument("--checked")
    a_add.add_argument("--by", default="")
    a_add.add_argument("--from", dest="derived_from", default="", help="claim ids this number was computed from")
    a_add.add_argument("--commitment", default="", choices=[""] + COMMITMENTS,
                       help="for MEASURED demand: what the buyer did (paid, deposit, signed, booked, intro)")
    a_label = sub.add_parser("label")
    a_label.add_argument("ids", help="claim ids, like c07,c08")
    sub.add_parser("trace").add_argument("id", help="a claim id, like c09")
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
            if not a.status and not a.derived_from:
                raise LedgerError("give --status, or --from with the claim ids it was computed from")
            r = add(a.dir, a.claim, a.kind, a.status, a.use, a.number, a.evidence, a.checked, a.by, a.derived_from,
                    a.commitment)
        except LedgerError as e:
            print("refused: %s" % e, file=sys.stderr)
            return 1
        print("%s %s / %s: %s%s" % (r["id"], r["status"], r["use"], r["claim"],
                                    (" (from %s)" % r["from"]) if r["from"] else ""))
        return 0
    if a.cmd == "label":
        st, weak_ids, missing = derived_status({r["id"]: r for r in load(a.dir)}, a.ids)
        print("%s, set by %s%s" % (st, ", ".join(weak_ids),
                                   ("; not in the ledger: %s" % ", ".join(missing)) if missing else ""))
        return 0
    if a.cmd == "trace":
        print("\n".join(trace({r["id"]: r for r in load(a.dir)}, a.id)))
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
        for r in gate(load_checked(a.dir)[0], a.audience):
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
