---
name: first-dollar
description: >-
  Finds the money and opportunities that fit this founder and this business
  right now: government research funding (SBIR, STTR, NSF America's Seed Fund,
  Innovate UK, EIC, IRAP), procurement requests for proposals, foundations,
  company credit and pilot programs, college partners, small business loans and
  local grants, and pre-sales. Checks eligibility first, records every match in
  the founder folder with its official link, the first step and the deadline
  exactly as the official page states it, and never invents an amount or a date.
  Use when the user says "find funding", "grants for this", "who would fund
  this", "SBIR", "RFPs", "non-dilutive", "loans", or "where do I get money".
argument-hint: "[country, field or amount]"
---

# first-dollar

Money follows evidence and fit. This skill finds the calls this founder can
actually win this month, and is honest about the ones they cannot yet.

What the user typed after `/first-dollar`: `$ARGUMENTS`

Read `${CLAUDE_SKILL_DIR}/../receipts/rules.md` and
`${CLAUDE_SKILL_DIR}/finding-money.md` first.

## Step 1: what fits

Read `founder/me.md`, `founder/idea.md`, `founder/cfo.md` (the cash needed) and
`founder/evidence/claims.md`. If `me.md` is missing, run the "About them" and
"About the next yes" questions from
`${CLAUDE_SKILL_DIR}/../receipts/interview.md`, one at a time.

Say the stage honestly, from the ledger: "idea" if nothing is measured, "pilot"
if a real customer is running it, "revenue" if someone pays. Many programs
filter on this.

## Step 2: search

Use the six places and the searches in `finding-money.md`. Search the web if
you can; if you cannot, say so and give the founder the searches to run.
Read each candidate's official page. Check eligibility first and drop anything
that fails it.

## Step 3: record each real match

One file per match in `founder/opportunities/<name>.md` (shape:
`${CLAUDE_SKILL_DIR}/opportunity.md`): the link, who it is for, what it gives,
the deadline and the date you checked, the first step, the fit and why, what
they ask for in their headings, which ledger claims already answer each, and
the gaps.

## Step 4: tell the founder

1. **The hard truth:** what the founder can and cannot win today, and why.
   For example: "Nothing here funds an untested idea without a technical
   question. The NSF pitch is a fit if you frame the open technical risk."
2. The short list, best fit first: name, amount and deadline as stated (or
   "check"), the first step, the fit.
3. Registrations that take weeks, flagged as the first step.
4. The gaps across the list, and which one to fill first.
5. That search always misses some: set alerts on the two or three portals that
   fit best.

## Rules

- Never invent an amount, a deadline, an eligibility rule or a past award.
  Unconfirmed means "check".
- No paid grant finders, and warn about anyone who charges to apply.
- Applying, registering and submitting are the founder's job. Prepare; do not
  submit.
- Not legal, tax or financial advice.

## Output

`founder/opportunities/*.md`. Next: `/handshake` writes the pitch for the
best match; `/receipts` job 4 lists what it still needs.
