---
name: prove-it
description: >-
  Your launch lead. Builds a dated, step-by-step launch plan: a cheap real-world
  test first (a waitlist, a pre-sale or a pop-up with a real price, so real buyers
  confirm what the simulated panel said), then the countdown to opening day with
  owners and deadlines, the launch-day run sheet, and the first 30 days of what to
  measure and what to change. Use when the user says "how do I launch", "launch
  plan", "when can I open", "launch checklist", "go live", or "soft open".
argument-hint: "[target launch date]"
---

# prove-it

Launching is a project with a date. This skill turns everything else in the pack
into a dated plan, and starts with the cheapest way to find out if real people
will pay before the big money goes out. This test is where the pack's guesses
meet reality, so it comes first and it is never skipped.

Read `${CLAUDE_SKILL_DIR}/../receipts/rules.md` first.

## Step 0: ready (the seven questions)

Ready, Fire, Aim (rule 11 in `rules.md`): get it ready fast, test it for real, then
perfect what works. Before the test, answer in writing, a line or two each:

1. Is it a good idea? (what the board, competitors and real calls say, with labels)
2. Does it feel like one? (the founder's own gut, stated honestly)
3. Is it economically feasible? (from `founder/cfo.md`)
4. Can I afford to test it? (the test's cost against the cash available)
5. Do I know what has to be done? (the critical tasks)
6. Do I have the people? (one named owner who will push it every day)
7. What is Plan B? (what you do if it fails, and the kill line below)

Then write the plan in four pages at most, the same day if you can: rough
numbers, the critical tasks with dates, the owner, and Plan B. A plan that
takes weeks to write is a way of not starting.

## Step 1: test before you spend

Test the riskiest assumption first, and on its own. If an idea has two
unknowns (will they want it, and can we make it well enough), find out the
first with the cheapest test before paying to solve the second.

Pick the cheapest real test that fits the business, and run it before signing the
big costs in `founder/numbers.json`:

| business | the test |
| --- | --- |
| physical shop or café | a pop-up, a market stall or a pre-order list with a price and a date |
| online product | a landing page with the price and a "pre-order" or "join the waitlist" button |
| service or agency | three paid pilot clients at the planned price |
| software or service sold to businesses | five to ten people who have the problem, then a time-boxed pilot offer (from `/handshake`) to the ones who feel it most |
| subscription | a founding-member offer, paid up front |
| any product not built yet | a pre-sale with a delivery date and a full refund if it slips, or a similar product someone else makes, sold with your angle, to learn what sells before you build |

Write two lines before running it, and log both as `PLANNED` with `ledger.py
add` so they cannot be moved afterwards:

- **The success line**: for example, 50 pre-orders in two weeks at $6.50, or 2
  of 5 firms agree to a pilot.
- **The kill line**: the result that means stop or change course, for example
  under 15 pre-orders, or 0 of 10 firms after a real ask.

When the test ends, log the result as `MEASURED`, kind `demand`, with the
evidence (the order export, the signed page, the emails), even if it is zero.
Compare it with the panel's buy rate. Real buyers win every time: if they fall
short of the panel, go back to `/dealbreaker` or `/litmus`; if they
hit the kill line, say so plainly and do not move the line.

Do not book the big costs in `founder/numbers.json` (a lease, equipment, hires)
until the success line is met.

## Step 2: the countdown

From today to launch day, with real dates (ask for the target date; default to the
earliest realistic one given lead times in `founder/ops.md`). Weekly blocks, each
task with an owner and a deadline:

- Legal and money: registration, bank account, permits from `founder/ops.md`.
- Build: fit-out or website, suppliers ordered by their lead times.
- Brand: sign, packaging, profiles from `founder/brand.md`.
- Marketing: the calendar in `founder/marketing.md` from launch minus 14 days.
- Team: hiring and training on the SOPs.
- A soft open or friends-and-family day before the public launch.

Mark the critical path: the tasks that move the launch date if they slip.

## Step 3: launch day

An hour-by-hour run sheet: who is where, what goes out on which channel, the
opening offer, what to do if something breaks (from the risk register).

## Step 4: the first 30 days (aim)

Only now, with real buyers, fix and improve: first what they complained about,
then what stopped others buying. Keep a short list of improvements and ship
one at a time on a schedule, telling customers what changed. Do not rebuild
what is selling; make it a little better each round.

The weekly numbers to track (from the CFO: units a day against break-even; from
marketing: the channel numbers), the level that triggers a change, and a review on
days 7, 14 and 30 with the questions to answer.

## Output

`founder/launch.md` with the hard truth first (the most likely way the test
fails), then the test with its success and kill lines, the countdown, the run
sheet and the 30-day review. Next: run the test, log it with
`/receipts`, then `/kill-or-build` compiles everything into the
business plan.
