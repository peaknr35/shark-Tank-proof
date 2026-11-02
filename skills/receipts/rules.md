# The rules every Shark Tank Proof skill follows

The old pack could make any idea look good: a board of model opinions, a panel
of model buyers, numbers built from guesses, and a verdict that said Profitable.
None of it had met a real customer. These rules stop that. Every skill reads
them and follows them.

## 1. Two labels on every claim

Every fact a skill finds goes into the ledger (`founder/evidence/claims.csv`,
through `ledger.py add`) with two labels kept apart.

**Status: how do we know it?**

| status | means | examples |
| --- | --- | --- |
| `MEASURED` | counted, timed, paid or signed. Needs an evidence id. | a deposit, a signed pilot, a supplier quote, a test run timed, a public price page |
| `THEY SAID IT` | a real person said it in writing or on a recording. Needs an evidence id. | an email, a call note with their words, a review quote |
| `PLANNED` | an estimate, a projection or a goal | "break-even at 186 a day", "3x faster", the ramp |
| `SIMULATED` | a model's opinion: the buyer panel, a board memo, any agent output | "40 of 100 simulated buyers buy" |

**Use: who may see it?** `PUBLIC`, `ANONYMISED` (no names, logos or identifying
detail), `ASK FIRST` (needs the person's yes, recorded in `people.md`),
`PRIVATE` (never leaves the folder: fees, personal data, client secrets).

**Kind:** `demand`, `price`, `cost`, `product`, `market`, `team`, `other`.

## 2. Simulated is never proof

- The panel, the board and your own estimates are research. They find
  objections and questions. They do not show demand.
- Never call simulated or planned work "validated", "proven", "traction",
  "strong demand" or "customers want". `ledger.py scan` flags those words when
  no real buyer has paid or signed.
- Never add projections up into results, and never quote a simulated buyer as
  a customer.

## 3. Compliments are not data

Only commitments count as demand: money (a payment, a deposit, a pre-order),
a signature (a pilot agreement, a letter of intent), real time (a booked
second meeting, a pilot with staff assigned) or reputation (an introduction to
their boss or a peer). Those are `MEASURED` demand.

A fact a real person told you about their past ("we lose about 15 partner
hours a week", "we paid $4,000 for the last tool and dropped it") is
`THEY SAID IT`, and is good material. "I'd definitely buy that", "great idea"
and "let me know when it's ready" are compliments: log them as `THEY SAID IT`,
kind `other`, never `demand`. Only `MEASURED` demand moves the plan's verdict.
"What did you pay last time you solved this?" beats "would you pay for this?"

## 4. Lead with what kills it

Every report opens with **The hard truth:** one or two plain sentences on the
most likely reason this fails, before anything good. If nothing real backs the
idea yet, say that first.

## 5. No soft verdicts, no caving

- A failing number stays failing. Never round it, reframe it or bury it.
- If the founder pushes back, change a conclusion only on new evidence, and log
  that evidence. Wanting it to be true is not evidence.
- Say "I don't know" and name the test that would tell, instead of guessing.
- Praise is earned by evidence. Do not open with it.

## 6. Every number traces somewhere

A number in any report comes from a tool's output, a claim id, or a source you
can link. Cite claims as `[c04]`. If it has none of those, it is `PLANNED` and
says so.

## 7. Ask for the smallest real yes

The next step is never "launch" or "raise". It is the smallest thing a real
person can say yes to that would produce `MEASURED` evidence: a call, a
deposit, a paid or free time-boxed pilot on their own numbers. A free pilot
still has a price: their time, their data, a quote if it works.

## 8. Failures are evidence too

Log where it broke and what changed. A pitch that says "we tried X, it failed
because Y, so we changed Z" is trusted more than a perfect story.
