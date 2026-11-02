---
name: kill-or-build
description: >-
  Your business planner. Compiles everything the other Shark Tank Proof skills wrote (the
  board's verdict, the competitors, the buyer panel, pricing, the offer, the CFO's
  numbers, marketing, brand, operations, the launch plan and the evidence ledger)
  into one business plan with a verdict at the top that is computed, never
  written by hand: Profitable (the numbers pass and a real buyer has paid, signed
  or booked), Unproven (works on paper, no real buyer yet), Not yet (with the
  failing numbers) or Incomplete. A simulated panel can fail a plan but never
  pass one. Adds an executive summary and a one-page version. Use
  when the user says "write my business plan", "put it all together", "is it
  profitable", "give me the plan", or at the end of the Shark Tank Proof pack.
argument-hint: "[--min-buy-rate 0.25]"
---

# kill-or-build

The last step. One document a founder can act on, built only from what the
pack found, and honest about which parts are real.

Read `${CLAUDE_SKILL_DIR}/../receipts/rules.md` first.

Tool in this folder:

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir founder
```

## Step 1: see what is there

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir founder --check
```

prints the verdict and each check. The checks, all computed:

1. Each unit earns money before fixed costs (`founder/numbers.json`).
2. Year 1 makes an operating profit.
3. The break-even fits inside capacity, if a capacity was given.
4. Enough simulated buyers buy (`founder/panel/results.json`; default bar 25%,
   change it with `--min-buy-rate` and say why). A low panel fails the plan; a
   high panel proves nothing.
5. Real demand: at least one `MEASURED` demand claim in
   `founder/evidence/claims.csv` (a payment, a deposit, a signed pilot, a
   booking).

The verdicts:

| verdict | means |
| --- | --- |
| Incomplete | no numbers yet: offer `/burn-test` |
| Not yet | a check fails; each failure is listed with its number |
| Unproven | the math works on paper, but no real buyer has committed |
| Profitable | the math works and at least one real buyer committed |

Run `ledger.py summary` first so the evidence section is current:

```bash
python3 "${CLAUDE_SKILL_DIR}/../receipts/ledger.py" summary
```

If there are no numbers, the verdict is Incomplete: offer to run `/burn-test`.
List the other missing sections with the skill that fills each. Do not fill a
missing section yourself from guesses.

## Step 2: the summary

Write `founder/summary.md`, half a page, plain words, opening with **The hard
truth:** the single most likely reason this fails.

- What the business is and who it is for, in two sentences.
- The verdict and the three numbers behind it (margin, break-even, year 1).
- What is real: the count of `MEASURED` and `THEY SAID IT` claims, and what
  they are. Then what is still a guess.
- What the simulated panel and board agreed on, and where they disagreed,
  labelled as simulated.
- The biggest risk and what will be done about it.
- What the founder needs to start (cash from the CFO, the first test from launch).
- The one thing to do this week.

If the verdict is Not yet, the summary leads with what has to change and which skill
changes it. If it is Unproven, it leads with the one real-world test that would
prove or kill it this month. Never soften a failing check, and never write an
Unproven plan as if it were a validated one.

## Step 3: compile

```bash
python3 "${CLAUDE_SKILL_DIR}/compile.py" --dir founder
```

writes `founder/business-plan.md`: title, the verdict and its checks, the key numbers
table, the idea, then every section the pack produced (summary, board, competition,
panel, pricing, offer, numbers, marketing, brand, operations, launch), and what is
not done yet.

## Step 4: the one-pager

Write `founder/one-pager.md` for the founder and close partners: the problem,
the customer, the offer and price, the numbers table, the real evidence (and
the panel, labelled simulated), what the money is for, and the ask. Same
numbers as the plan, word for word.

For anyone outside (a customer, a funder, a lender), do not send the plan or
this page: run `/handshake`, which builds only from claims that audience
may see and checks the result.

## Rules

- The verdict comes from `compile.py`. Never write Profitable by hand, never
  round a failing number into a passing one, and never call Unproven "almost
  there".
- Say once, clearly: the panel and board are simulated and the numbers are
  projections; only real customers and real quotes confirm them. Not financial,
  legal or tax advice.
- If the user wants a PDF or a deck, offer to export the plan, but keep the
  markdown as the source of truth.

## Output

`founder/summary.md`, `founder/business-plan.md`, `founder/one-pager.md`. Then give
the user the verdict in one line, the hard truth, and the one real-world thing
to do this week. Next: `/handshake` for the receiver who has to say yes.
