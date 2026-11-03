# Where do I go? (the stage map)

This folder is an ICM workspace (Interpretable Context Methodology): each skill
is one numbered stage with one job. Stages talk only through files in this
folder. A person can open, read and edit any of them before the next stage
runs, and the next stage reads whatever is there.

Two kinds of file:

- **Reference** (the same every run, read as rules): the pack's
  `receipts/rules.md`, `me.md`, `idea.md`, `customer.json`.
- **Working** (changes each run, read as input): everything a stage writes
  below, plus the ledger in `evidence/`.

## The handoff

A number that moves from one stage to the next carries its label with it
(`rules.md`, rule 10): **a number takes the weakest label of anything it was
computed from.** MEASURED > THEY SAID IT > PLANNED > SIMULATED.

- In the ledger: a computed claim lists its sources in the `from` column.
  `ledger.py trace c09` shows the chain down to the originals.
- In `handoff/`: a stage that works numbers out writes one file
  (`handoff/04_litmus.json`, `handoff/06_burn-test.json`) with every result,
  its label and the inputs that set it. `/kill-or-build` flags a file whose
  labels have gone stale.

## Stages

| stage | skill | reads (working) | writes | hands on |
| --- | --- | --- | --- | --- |
| 00 | `/receipts` | anything a real person did | `evidence/` | ledger claims `c01`... (every stage cites these) |
| 01 | `/shark-board` | `idea.md`, `evidence/` | `board.md` | |
| 02 | `/ground-truth` | `idea.md` | `competitors.md`, `competitors.csv` | competitor prices as claims (MEASURED, with a link) |
| 03 | `/truth-serum` | `customer.json`, `pitch.md` | `panel/` | `panel/results.json`, `panel/answers/` (always SIMULATED) |
| 04 | `/litmus` | `panel/answers/`, `competitors.md`, `numbers.json` | `pricing.md`, `pricing-curve.md` | `handoff/04_litmus.json`; the price claim `--from` the range; `numbers.json` `sources.price` |
| 05 | `/dealbreaker` | `pricing.md`, `panel/results.md`, `board.md` | `offer.md` | |
| 06 | `/burn-test` | `numbers.json`, `evidence/claims.csv` | `cfo.md`, `cfo-sources.md` | `handoff/06_burn-test.json` |
| 07 | `/signal` | `offer.md`, the ledger gate `public` | `marketing.md` | |
| 08 | `/straight-talk` | `idea.md`, `offer.md` | `brand.md` | |
| 09 | `/reality-check` | `numbers.json`, `offer.md` | `ops.md` | real quotes as claims |
| 10 | `/prove-it` | `board.md`, `offer.md`, `evidence/` | `launch.md` | success and kill lines as claims |
| 11 | `/kill-or-build` | every file above, `handoff/` | `summary.md`, `business-plan.md`, `one-pager.md` | the verdict |
| 12 | `/handshake` | the ledger gate for the audience | `outputs/` | |
| 13 | `/first-dollar` | `business-plan.md`, `me.md` | `opportunities/` | |

The order is a default, not a rule: any stage runs on its own. If you edit a
file a stage wrote, run that stage's next stage again so it picks up the edit.
