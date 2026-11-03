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

## 9. Keep the folder clean

- **One home per fact.** A number lives in the ledger with its evidence id.
  Pitches and `work/` files point to it by claim id. If it changes, change the
  ledger and rebuild the pitch.
- **Originals stay original.** The real file goes in `evidence/`. Summaries go
  in `work/` or the ledger, never on top of the source.
- **Small files.** One project per `work/` file, one opportunity per
  `opportunities/` file, so a skill reads only what the job needs.
- **Private stays private.** If the folder is shared (a team workspace, a
  repo), keep `PRIVATE` originals out of it.

## 10. A number takes the weakest label of anything it was computed from

The break is at the handoff between skills. `/litmus` picks a price from the
simulated buyers, `/burn-test` works out the margin from that price, and by the
time `/kill-or-build` adds it all up the margin looks like a fact because it
came out of a calculation. Arithmetic does not make a guess stronger.

Strongest to weakest: `MEASURED` > `THEY SAID IT` > `PLANNED` > `SIMULATED`.

- A computed number gets the **weakest** label of every input it used. A margin
  from a simulated price and three quoted costs is `SIMULATED`. A year 1 profit
  from quoted costs and a planned ramp is `PLANNED`. Break-even itself uses only
  the price and the costs, so when the price is a real sale and every cost is
  quoted, break-even is `MEASURED`.
- An input with no source is `PLANNED` (rule 6). A cited claim id that is not
  in the ledger cannot vouch for anything: it counts as `SIMULATED`.
- A what-if (`--price`, `--volume`) is at best `PLANNED`. It can lower a label,
  never raise one.
- Picking a round number inside a simulated range does not launder it. If the
  panel informed the price, the price is computed from the panel.
- A label moves up only when its weakest input does: a real buyer pays the
  price, a supplier sends the quote. Log the new claim, point the handoff file
  at it, and run the stage again.
- A passing check that rests on a `SIMULATED` input can fail a plan but never
  pass one, the same as the panel itself.
- A `PLANNED` price or cost blocks Profitable too. The price and the costs can
  be real before launch (a buyer pays, a supplier quotes), so Profitable needs
  them `MEASURED` or `THEY SAID IT`. Only the volumes (the ramp, the plan,
  selling days, capacity) may stay forecasts, and the plan says they are.

### Every handoff carries its labels

The skills work like the stages of a pipeline (Interpretable Context
Methodology: each stage reads files, does one job, writes files the next stage
reads, and a person can open and edit any of them in between). So the label
travels in the handoff files, next to the number, where a person can see it:

| handoff | file | how the label travels |
| --- | --- | --- |
| `/truth-serum` to `/litmus` | `panel/answers/` | always `SIMULATED` |
| `/litmus` to `/burn-test` | `pricing-curve.md`, the price claim, `numbers.json` `sources.price` | the range prints its label; the price claim is logged `--from` the range claim, so it inherits it |
| `/burn-test` to `/kill-or-build` | `numbers.json` (`sources`, item `claim`), `cfo.md` | `unit_economics.py` prints the label of every result and the input that set it |
| `/kill-or-build` to the reader | `business-plan.md` | every check shows its label; a simulated pass caps the verdict at Unproven |
| anything to the ledger | `claims.csv` `from` column | `ledger.py add --from c07,c08` takes the weakest label; `check` flags a leak; `trace c09` shows the chain |
| `/litmus`, `/burn-test` to the next stage | `handoff/04_litmus.json`, `handoff/06_burn-test.json` | each result with its value, label and the inputs that set it; `/kill-or-build` flags a file whose labels went stale |

The map of every stage, what it reads and what it hands on, is
`founder/CONTEXT.md` (`ledger.py init` writes it).

Each skill that hands a number on writes a short **handoff contract** in its
SKILL.md: what it reads (with labels), what it does, what it writes (with
labels). If a stage cannot say where a number's label came from, the number is
`PLANNED` at best.

## 11. Ready, Fire, Aim: sell first, test fast, perfect later

From Michael Masterson's *Ready, Fire, Aim* (2008), in our words. The pack
tests ideas hard; this rule keeps the testing fast and pointed at the one thing
a new business has to learn first: how to make the first sale profitably.

**Know the stage.** A business under about $1 million a year (Stage One,
"infancy") has one job: sell one product. Its main problem is that the founder
does not yet know what works. Later stages are about many products, then
systems and managers, then acting as an investor. Every report says which stage
the business is in and keeps advice to that stage. Most of this pack is Stage
One work.

**Selling comes first.** In Stage One, most of the founder's time and money go
to finding customers and making sales, not to the logo, the office, the
website polish or the perfect product. Spend nothing on what a customer never
sees until something sells.

**Find the optimum selling strategy (OSS).** Four questions, all four
answered, in this order of importance:

1. **Where** are the customers? (the medium: the list, the street, the search,
   the channel). A weak ad in the right place beats a great ad in the wrong one.
2. **What** do you sell them first? (the front-end product, which buys a
   customer, not a fortune)
3. **What price?** (for the first sale, lean low enough to win customers fast,
   never below what the CFO says one is worth)
4. **What words?** (the copy and the offer that convince them)

Start by copying what works for the competitors who keep buying the same ads,
and be different in one thing only: a medium you can own, a price structure,
or a selling proposition buyers want. Then test away from it.

**The first sale buys a customer; the back end pays.** Know what one customer
is worth (the first order plus what they buy after), and so the most you can
spend to win one (`/burn-test`, "What one customer is worth"). Every first
product has a next product. No dead ends.

**Ready.** Before spending real money on a new product or test, answer seven
questions in writing: Is it a good idea? Does it feel like one? Is it
economically feasible? Can I afford to test it? Do I know what has to be done?
Do I have the people? What is Plan B? Keep the plan to four pages at most:
rough numbers, critical tasks, one named owner, dates, and Plan B. Have it
done in a day, not a month.

**Fire.** Launch when it is good, not when it is perfect. Test the riskiest
single assumption first and on its own, as cheaply as possible: a pre-sale, a
landing page with a price, a similar product sold with your angle, a pilot.
Let a real buyer's action decide, not a survey or a panel.

**Aim.** Improve only what has proven it sells. Then keep improving it on a
schedule, because a product that stops getting better starts getting worse.

**Plan B is a stop-loss.** Set the numbers before the test that mean stop or
change course (`/prove-it`'s kill line). Some ideas will fail; attach your
confidence to the process, not to any one idea.

**Speed never overrides the labels.** Moving fast means testing sooner, not
counting a guess as a result. A test that has not run is `PLANNED`; a panel is
`SIMULATED`; only a real buyer's action is `MEASURED` (rules 1 to 10).
