---
name: receipts
description: >-
  The evidence keeper and the pack's honesty check. Keeps one ledger of every
  claim the Shark Tank Proof pack makes, each labelled with how we know it (MEASURED,
  THEY SAID IT, PLANNED, SIMULATED) and who may see it (PUBLIC, ANONYMISED, ASK
  FIRST, PRIVATE), files the originals, logs real customer calls, audits what is
  real versus guessed or simulated, and lists the gaps to go and fill. Use when
  the user says "what do I actually know", "is any of this real", "audit my
  claims", "log this call", "I got a pilot", "add evidence", "what am I
  missing", "reality check", or at the start of the pack and after any real
  customer contact.
argument-hint: "[audit | log <file or call notes> | gaps <receiver>]"
---

# receipts

The rest of the pack makes guesses: a board of model opinions, a panel of
model buyers, numbers from estimates. That is useful research. It is not proof,
and without this skill it starts to look like proof. This skill keeps the line
between the two, and it is the only place a guess can become a fact: when a
real person does something.

What the user typed after `/receipts`: `$ARGUMENTS`

Read `${CLAUDE_SKILL_DIR}/rules.md` first, every time. Every other Shark Tank Proof skill
follows it too.

Tool in this folder (if the path is not expanded, use the base directory Claude
Code printed for this skill):

```bash
python3 "${CLAUDE_SKILL_DIR}/ledger.py" <init | add | check | summary | gate | scan>
```

Below, `LEDGER` means exactly that. State lives in `founder/evidence/`.

## The folder

```
founder/
  START-HERE.md        the map (copy templates/START-HERE.md)
  CONTEXT.md           the stage map: which skill reads, writes and hands on what (made by init)
  me.md                who is behind it (copy templates/me.md)
  idea.md ...          what the other skills write
  work/                one file per project, pilot or client (copy templates/work-record.md)
  evidence/
    claims.csv         the ledger; claims.md and summary.json are written from it
    evidence-log.md    one row per original file
    people.md          real people only: who, what they said, may we name them
    calls/             notes from real conversations
    <originals>        screenshots, emails, receipts, recordings, signed pages
  opportunities/       one file per customer, funder or internal ask
  outputs/             every pitch, dated, written by /handshake
  handoff/             labelled results passed between stages: 04_litmus.json, 06_burn-test.json
```

## Four jobs

Ask which one if it is not clear. Do one at a time.

### 1. Start or update the folder

- `LEDGER init`, then copy `templates/START-HERE.md` and `templates/me.md` into
  `founder/` if missing. Say what you made.
- Interview the founder with `${CLAUDE_SKILL_DIR}/interview.md`. One question
  at a time.
- Read any files they give you. File the originals in `founder/evidence/`, add
  one row each to `evidence-log.md`, then add one claim per fact with `LEDGER
  add`. Keep their words.
- For each project, pilot or client they describe, write one
  `founder/work/<name>.md` from `templates/work-record.md`: the problem before,
  who did what, where it broke, what is still unproven, and one suggested
  sentence for pitches. It lists ledger ids; the facts stay in the ledger.
- If other Shark Tank Proof skills already ran, sweep their outputs and log what they
  found with the right status: the panel's buy rate and board scores are
  `SIMULATED`; the CFO's margin and ramp are `PLANNED`; a supplier quote or a
  public price page is `MEASURED` with the link as its evidence.

### 2. Log real contact

Anything a real person did: a call, an email, a deposit, a signed pilot, a
refusal. Follow "Logging the call" in `${CLAUDE_SKILL_DIR}/conversations.md`.
A yes is `MEASURED`, kind `demand`, with `--commitment` naming what they did
(`paid`, `deposit`, `signed`, `booked`, `intro`) and the count as the number;
the ledger refuses a buyer with no commitment, no count or no evidence. A
signup or a waitlist is not a commitment: log it as kind `other`. A no is
logged too: `MEASURED`, kind `demand`, number `0 of 1`, with the reason in
their words. If the founder has not talked to anyone yet, give them that
file and the five questions, and help them pick the first five people.

### 3. Audit

```bash
LEDGER check      # broken labels, missing evidence ids, stale claims
LEDGER summary    # writes founder/evidence/claims.md and summary.json
```

Then tell the user, in this order:

1. **The hard truth:** how much of the pack rests on real evidence. For
   example: "31 claims. 2 measured, 0 from real buyers. Nothing about demand
   is real yet."
2. Claims that are stated as fact somewhere in `founder/` but are `PLANNED` or
   `SIMULATED` in the ledger (read board.md, offer.md, pitch.md, marketing.md,
   one-pager.md). Name the file and the line, and the honest wording.
3. The three strongest real claims.
4. The three biggest gaps.

### 4. Find the gaps for one receiver

For a chosen customer, funder or internal ask (`founder/opportunities/`),
compare what they need to see (`${CLAUDE_SKILL_DIR}/../handshake/receivers.md`) with what
`LEDGER gate` allows. List each missing piece as something to go and get: a
measured number, a quote with permission, a pilot, a partner, a registration.
For each, the cheapest way to get it this week and who could help.

When you list the gaps (job 3 or 4), put first the gap that blocks the first
sale: where the customers are, what they buy first, at what price, or what
words make them buy (Ready, Fire, Aim, rule 11 in `rules.md`).

## Rules

- Never upgrade a status without a new original in `evidence/`. A claim moves
  from `PLANNED` to `MEASURED` only when the thing was counted, paid or signed.
- Never log a simulated buyer, a board member or your own reasoning as
  `THEY SAID IT`. Only real people say things.
- Say who did what. A workshop is not a contract; a mention is not a client.
- `PRIVATE` stays in the folder. Ask before you log anything about a third
  party as `PUBLIC`.
- Date every claim. Check anything older than 90 days again before it goes in a
  pitch.

## Output

`founder/evidence/` (ledger, log, people, calls, claims.md, summary.json),
`founder/START-HERE.md`, `founder/me.md`. End with: what you changed, the hard
truth in one line, the gaps, and the one real-world action this week that
would add the most `MEASURED` evidence.
