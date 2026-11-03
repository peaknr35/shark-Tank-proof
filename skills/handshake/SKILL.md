---
name: handshake
description: >-
  Turns the founder folder into the thing that gets one real person to say yes
  to the next step: a one-page pilot offer for a customer, an NSF Project Pitch
  or grant answer for a funder, an investor or lender one-pager, a business case
  for a boss, or an invite for the people who will use it. Always writes the
  one-sentence, three-sentence and three-minute versions first. Builds only from
  claims in the evidence ledger that the audience may see, never from simulated
  buyers, and checks the finished pitch with the ledger before it goes out. Use
  when the user says "pitch this", "write a pilot offer", "one-pager", "grant
  pitch", "NSF pitch", "deck for", "email this customer", "business case", or
  "what do I send them".
argument-hint: "<who it is for, and the yes you want>"
---

# handshake

A plan is for the founder. A pitch is for one person and one yes. This skill
writes it from what is actually known, so the founder can send it without
having to defend a number they cannot back.

What the user typed after `/handshake`: `$ARGUMENTS`

Read `${CLAUDE_SKILL_DIR}/../receipts/rules.md` first. The ledger tool:

```bash
python3 "${CLAUDE_SKILL_DIR}/../receipts/ledger.py" <gate | scan | summary>
```

Below, `LEDGER` means exactly that.

## Step 1: who, and what yes

Ask who it is for and the yes the founder wants, if not given. Name the
receiver: a customer, a funder, an investor, a lender, someone inside their
business, or the people who will use it. Read
`${CLAUDE_SKILL_DIR}/receivers.md` for what that receiver needs to see.

If there is a document from them (an RFP, a grant call, an email, a job post),
read it first, pull out exactly what they ask for, and save it as
`founder/opportunities/<name>.md` (shape:
`${CLAUDE_SKILL_DIR}/../first-dollar/opportunity.md`).

Push the ask down to the smallest real yes (rule 7). If the founder wants to
ask a stranger for a big upfront fee, say plainly that a time-boxed pilot on
the receiver's own numbers is more likely to get a yes, and offer both.

## Step 2: what the folder can support

```bash
LEDGER check
LEDGER gate --audience <public | anonymised | permission>
```

Pick the audience from how the pitch will travel: `public` for anything that
could be forwarded, `anonymised` for a private send, `permission` only if
every `ASK FIRST` claim's person said yes in `founder/evidence/people.md`.

Build only from what `gate` prints. If the receiver needs something the folder
cannot support, do not write around it: list it under **Gaps** at the end of
the output, with how to get it (`/receipts` job 4 goes deeper). Never
fill a gap with a guess, a panel quote or a board opinion.

If nothing about demand is `MEASURED`, the pitch says so honestly through its
wording: "we are looking for three firms to run a pilot", not "firms are
lining up".

## Step 3: write it

1. The one sentence, the three sentences, the three-minute outline.
2. The receiver's format from `receivers.md`. Answer in the receiver's own
   headings when they gave you a call or RFP. Respect their limits (count
   characters for the NSF sections and say the count).
3. Cite every fact with its claim id, like `[c04]`, in the working draft.
   Write `PLANNED` claims as goals ("we expect", "the pilot will test"), never
   as results.
4. A short **What could go wrong** section in plain words. Receivers trust it.
4b. Check the pitch stands on four legs (Ready, Fire, Aim, rule 11 in `rules.md`):
   one big idea, the big benefit to this receiver (about them, not you), one
   big promise joining the two, and proof. The proof leg comes only from the
   claims `gate` printed; with no `MEASURED` proof, the promise is the pilot's
   terms ("if it does not hit the line we set together, you owe nothing").
5. **Gaps**: what this pitch would need to be stronger, and the cheapest way to
   get each.

Save it as `founder/outputs/<YYYY-MM-DD>-<receiver>.md`.

## Step 4: check it before it goes

```bash
LEDGER scan founder/outputs/<file>.md --audience <the same audience>
```

`scan` refuses any cited claim the audience may not see (a `SIMULATED` or
`PRIVATE` one, an `ASK FIRST` without permission) and flags proof words
("validated", "proven", "strong demand") when no real buyer has paid or signed.
Fix every problem it prints and run it again until it is clean. Then make a
send-ready copy without the `[c..]` ids if the founder wants one, and keep the
cited draft.

## Rules

- No simulated buyer, board member or model output is ever quoted, counted or
  described as a customer, a user, an advisor or market research from real
  people.
- No invented advisors, partners, logos, client names or numbers. "Advisors in
  accounting" needs a real advisor in `people.md` who agreed to be listed.
- No market size without a source; otherwise write it as an estimate with the
  method.
- Sending is the founder's job. Draft the email or message; do not send it.

## Output

`founder/outputs/<date>-<receiver>.md` (plus a clean copy if asked), and
`founder/opportunities/<name>.md` if there was a call or RFP. End with the one
sentence, the gaps, and the next action: who to send it to this week, and what
to log with `/receipts` when they answer.
