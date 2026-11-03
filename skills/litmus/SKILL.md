---
name: litmus
description: >-
  Finds the price buyers will actually pay. Reads the consumer panel's four price
  answers per buyer into a Van Westendorp price-sensitivity range (too cheap, a
  bargain, getting expensive, too expensive), sets it against what competitors
  really charge and against the CFO's margin, and recommends a price, a price
  ladder (good / better / best) and an opening offer to test. Use when the user
  says "how much should I charge", "price this", "is $X too expensive", "pricing
  strategy", "what price", or after the consumer panel.
argument-hint: "[current price]"
---

# litmus

Price is the fastest lever on the margin and the one founders guess most. This
skill sets it from three things you can check: what buyers said, what competitors
charge, and what the business needs to earn. Only one thing settles it: a real
buyer paying it.

Read `${CLAUDE_SKILL_DIR}/../receipts/rules.md` first. If the ledger
has real price evidence (a deposit, a paid pilot, a buyer telling you what
they pay today), it outranks every simulated answer below.

Tool in this folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/van_westendorp.py" founder/panel/answers --price 6.50 --out founder/pricing-curve.md
```

## Handoff contract

This skill sits between the panel and the CFO, which is where a simulated
number most easily turns into a "fact". Rule 10 in `rules.md`: a number takes
the weakest label of anything it was computed from.

**Inputs**

| input | label |
| --- | --- |
| `founder/panel/answers/` (from `/truth-serum`) | always `SIMULATED` |
| a CSV of real survey answers | `THEY SAID IT` with an evidence id (pass `--status`), else `SIMULATED` |
| competitor price pages in `founder/competitors.md` | `MEASURED`, each with its claim id |
| the ledger's real price evidence (a deposit, a paid pilot) | `MEASURED`; it outranks everything above |

**Process:** read the range, set it against competitors and the margin, pick a price.

**Outputs**

| output | label |
| --- | --- |
| `founder/pricing-curve.md` | the tool prints it at the top: "How we know this range" |
| the range claim in the ledger | the range's label (`SIMULATED` from the panel) |
| the price claim in the ledger | `--from` the claims it was picked from, so it takes the weakest |
| `founder/numbers.json` `"sources": {"price": "c.."}` | points at the price claim, so `/burn-test` can carry the label on |

## Step 1: what buyers said

If `/truth-serum` ran, every buyer answered four price questions. Run the
tool on `founder/panel/answers` (or a CSV with the columns `too_cheap, cheap,
expensive, too_expensive` from real surveys, which beat simulated answers every
time). It reports:

| point | meaning |
| --- | --- |
| PMC | below this, too many think it is too cheap to be good |
| OPP | the price with the least resistance either way |
| IPP | where as many call it a bargain as call it expensive |
| PME | above this, too many will not buy at all |

PMC to PME is the acceptable range. If the panel has not run, say so and offer to
run `/truth-serum --quick` first. Do not invent a range.

## Step 2: what competitors charge

From `founder/competitors.md` (or look them up now, from their own public price
pages, with links): the price of the nearest substitutes for the same job. Note
what each price includes, so you compare like with like. A matcha latte is
compared with other matcha lattes and with the coffee it replaces, not with a tea
bag.

## Step 3: what the business needs

From `founder/numbers.json`: the variable cost per unit and the break-even. Run the
CFO's tool at two or three candidate prices to see the margin and break-even at
each:

```bash
python3 "${CLAUDE_SKILL_DIR}/../burn-test/unit_economics.py" founder/numbers.json --price 7.00
```

## Step 4: decide

Write `founder/pricing.md`:

0. **The hard truth:** how much of this price rests on real buyers, and its
   label. For example: "This price comes from 20 simulated buyers and two
   competitor pages, so it is SIMULATED, and so is every margin worked out
   from it. No one has paid it yet."
1. **The price**, and why: where it sits in the acceptable range, against the
   competitors, and the margin it gives (from the tool, not a guess).
2. **The ladder**, if the business can have one: a good / better / best (size,
   bundle, subscription, membership) with a reason to step up each rung.
3. **The opening offer**: an intro price or bonus for launch that does not train
   buyers to wait for discounts, with an end date.
4. **What to test with real buyers**: two prices inside the range and how to test
   them (two landing pages, a pre-sale at each, A/B on the menu board). For a
   business sold to businesses, the first price is often a pilot: a small
   deposit credited to the first month, or free for a fixed time in exchange
   for named things (their numbers, staff time, a quote if it works). A large
   setup fee asked of a stranger with no references is the most common reason
   for an early no; say so if the plan has one.
5. The panel's verbatim price objections (top three), so marketing can answer them.

## Rules

- Price answers from simulated buyers pick what to test. They are not proof.
- Log the range first, then the recommended price **computed from it**, so the
  price inherits the weakest label instead of being called `PLANNED`:

  ```bash
  python3 "${CLAUDE_SKILL_DIR}/../receipts/ledger.py" add --claim "Panel acceptable price range" --kind price --status SIMULATED --use PRIVATE --number "$5.80 to $7.40"
  python3 "${CLAUDE_SKILL_DIR}/../receipts/ledger.py" add --claim "Recommended price" --kind price --use PRIVATE --number "$6.50" --from c07,c03
  ```

  The second line has no `--status`: the ledger gives it the weakest label of
  `c07` and `c03` (here `SIMULATED`), and refuses a stronger one. Then write the
  new id into `founder/numbers.json` as `"sources": {"price": "c08"}`.
- A price picked by hand inside a simulated range is still computed from it.
  Rounding it, or calling it "our decision", does not make it `PLANNED`.
- The price becomes `MEASURED` only when a real buyer pays it: log that sale
  as its own claim with an evidence id and point `sources.price` at it.
- Never price below variable cost to "buy" customers without saying so, and how
  long the CFO says the business can afford it.
- No fake anchors: no "was $X" price that was never charged.

## Output

`founder/pricing-curve.md`, `founder/pricing.md`, the range and price claims in
the ledger, and `sources.price` in `founder/numbers.json`. If the price changed,
update `founder/numbers.json` and re-run `/burn-test`. Next: `/dealbreaker`.
