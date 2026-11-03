---
name: dealbreaker
description: >-
  Builds an offer too good to refuse. Lists every problem the buyer hits on the way
  to the result they want, turns each into a solution, trims to what is cheap to
  deliver and valuable to the buyer, and stacks it with honest bonuses, a guarantee
  the CFO can afford, real urgency and a clear name. Scores it on the value
  equation (outcome, likelihood, time, effort) and re-tests it on a quick buyer
  panel. Use when the user says "make my offer better", "why won't people buy",
  "what should I include", "guarantee", "bonuses", "grand slam offer", or after the
  panel shows people passing.
argument-hint: "[what you sell]"
---

# dealbreaker

Most businesses sell a product. Good ones sell an offer: the product plus
everything that makes buying it an easy yes. This skill builds that, using the
Offers lens in `${CLAUDE_SKILL_DIR}/../shark-board/lenses.md` as the method (a
summary of the framework in Alex Hormozi's *$100M Offers*; never present it as
his words).

Read `${CLAUDE_SKILL_DIR}/../receipts/rules.md` first. An offer is a
set of promises. Every promise is `PLANNED` until it has been delivered and
measured, and the offer must say it that way.

## Step 1: read what is already known

- `founder/idea.md` and `founder/pitch.md`: what is sold today.
- `founder/panel/results.md`: why buyers pass, in their words. This is the raw
  material: every top objection should be answered by something in the offer.
- `founder/numbers.json`: what each extra costs, so the stack stays profitable.
- `founder/board.md`: the board's conditions.

## Step 1b: the first yes

Before the full offer, design the first one: the smallest real commitment a
stranger would make with no references. For a shop, a launch-day price or a
founding-member card. For a business sold to businesses, a time-boxed pilot on
their own numbers (two to eight weeks, one workflow, a success line written in
advance, a clear end: roll into the standard price or remove it and owe
nothing). Use the pilot offer shape in
`${CLAUDE_SKILL_DIR}/../handshake/receivers.md`. The full offer below is
what the pilot rolls into.

## Step 2: the problem list

Write every obstacle between the buyer and the result they want, in the buyer's
words: before buying (doubt, price, effort to switch), during (waiting, learning,
inconvenience), after (does it last, what if it fails). Aim for 15 to 30. Pull
from the panel objections and the competitor complaints first.

## Step 3: solutions, trimmed and stacked

Turn each problem into a solution (a feature, a service, a guarantee, a format).
Score each on value to the buyer (1 to 5) and cost to deliver (1 to 5, from the
CFO's numbers). Keep high value, low cost. Stack what is left into:

- **The core**: the thing itself, described by the outcome, not the ingredients.
- **Bonuses**: two or three, each killing one specific objection.
- **The guarantee**: what happens if it does not deliver. Model what it costs at a
  realistic claim rate with the CFO's tool before promising it.
- **Urgency and scarcity**: only if they are true (a launch week, a limited first
  batch). Never fake a countdown or a "only 3 left".
- **The name**: a clear, specific name for the offer, not the company.
- **The next sale** (no dead ends, Ready, Fire, Aim, rule 11 in `rules.md`): what a
  buyer of this offer is most likely to want next (a refill, an upgrade, a
  membership, the next service), and the easiest way to keep buying (a
  subscription they can cancel any time, a standing order). Put its expected
  value in `founder/numbers.json` as `backend_per_customer` (`PLANNED` until
  someone buys it), so `/burn-test` can work out what a customer is worth.

## Step 4: score it

On the value equation, before and after, 1 to 10 each: dream outcome, perceived
likelihood of getting it, time to the result, effort and sacrifice. Say which
element of the stack moves which score.

Say why the buyer buys: to feel good, or to solve a problem. For a problem,
put the result in money or time saved ("each one saves you 30 minutes a week"),
from a real or planned number with its label.

Be strict on likelihood: with no `MEASURED` results, a buyer has only the
founder's word. Likelihood is low until there is a case, a quote or a demo on
the buyer's kind of data, and a stack of bonuses does not change that.

## Step 5: re-test it

Write the new offer into `founder/pitch.md` (keep the old one as
`founder/pitch-v1.md`) and run `/truth-serum --quick` with the same seed.
Report the buy rate before and after and which objections dropped. If nothing
moved, say so: the problem may be the market or the price, not the offer. If
it moved, say that too, and that it is still simulated: the real re-test is
the first-yes offer put to real buyers.

Log every promise the offer makes ("results in 5 days", "3x faster", "zero
data leaves the building") with `ledger.py add` as `PLANNED`, kind `product`,
unless it is already `MEASURED` with evidence.

## Rules

- Every promise must be deliverable and affordable; check costs with the CFO.
- A promise that has not been measured is written as a goal or a commitment
  ("we will measure", "if we miss it, you pay nothing"), never as a fact.
- No fake reviews, testimonials, scarcity, discounts or "as seen on".
- Follow the advertising and consumer-protection rules of the user's market for
  guarantees and claims (health claims especially). Not legal advice.

## Output

`founder/offer.md` (the hard truth first: the weakest part of the offer; then
the first-yes offer, the problem list, the stack, costs, the value-equation
scores, the re-test result) and the updated `founder/pitch.md`. Next:
`/burn-test` to re-run the numbers with the stack, then `/signal`,
or `/handshake` to send the first-yes offer to a real buyer.
