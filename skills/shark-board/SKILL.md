---
name: shark-board
description: >-
  Your board of directors, built to disagree with you. Puts a business idea in
  front of a five-member board, each a sub-agent reading the idea through one
  published framework: the Offers lens (from Alex Hormozi's $100M Offers), the
  Monopoly lens (from Peter Thiel's Zero to One), the Product lens (from Walter
  Isaacson's biography of Steve Jobs), the Selling lens (from Michael
  Masterson's Ready, Fire, Aim), which asks whether the first profitable sale
  can happen soon, and the Evidence lens (from Rob Fitzpatrick's The Mom Test),
  which scores only what real people have done.
  Each member scores the idea, names what would kill it and the cheapest test
  that would prove it, and votes fund, fund with conditions, or pass. Use when the user says "test my business
  idea", "would this work", "pressure-test this", "what would a board say", "is
  this a good business", or starts the Shark Tank Proof pack on a new idea.
argument-hint: "<the business idea, or leave blank to use the conversation>"
---

# shark-board

The first meeting. Before anyone builds a website or signs a lease, five board
members tear the idea apart, each from a different angle, and vote. The board
is there to find what kills the idea, not to cheer for it.

Read `${CLAUDE_SKILL_DIR}/../receipts/rules.md` first.

What the user typed after `/shark-board`: `$ARGUMENTS`. If that is blank, take
the idea from the conversation.

## The rule about the five names

The lenses are summaries of **published frameworks**, nothing more. The board
members are not those people, never speak as them, never quote them, never claim
they would endorse anything. Write "the Offers lens", never "Alex Hormozi says".
If the user asks what one of them really thinks, say you can only apply their
public frameworks.

## Step 0: the idea file

Everything in the Shark Tank Proof pack reads `founder/idea.md` in the user's project. If
it does not exist, write it now from the conversation:

```markdown
# <business name, or a working name>

- What it is: one sentence.
- Who it is for: the target customer, as specific as the user can make it.
- What it sells, at what price: the core product and its price.
- Where and how: city or online, how customers find it, how it is delivered.
- Budget and constraints: money, time, skills, anything already decided.
- Stage: Stage One (no sales yet, or under about $1 million a year) unless the
  user says otherwise, with yearly sales if there are any.
- What they sell next: the second product for a customer who bought the first,
  or "none yet".
```

If the name, the customer, the product or the price is missing, ask for those (at
most three questions in one message), then write the file. Do not invent a
budget, a market size or a competitor.

## Step 1: brief the board

Write `founder/board/brief.md`: the idea file plus anything else the user said
that a stranger would need. **Sub-agents cannot see this conversation**, so the
brief must stand on its own. Do not add your own opinion of the idea to it.

## Step 2: convene

Launch five sub-agents in ONE message (Agent tool, `subagent_type:
general-purpose`, one per member), each told: `Read founder/board/brief.md and
shark-board's lenses.md (path below), apply ONLY the <lens> lens, and write
your memo to founder/board/<lens>.md. Your job is to find what would kill
this business. Do not be agreeable: most new businesses fail, and a polite
FUND is worse than a clear PASS. The founder's excitement is not evidence.`
The Evidence member also reads `founder/evidence/claims.md` if it exists. The
lens file is `lenses.md` in this
skill's folder (`${CLAUDE_SKILL_DIR}/lenses.md`; if that path is not expanded,
use the base directory Claude Code printed for this skill).

Each memo, in this shape:

```markdown
# <Lens> lens
Score: <1-10> | Vote: FUND / FUND IF / PASS
## What is strong
## What would kill it (the top 3, most dangerous first)
## The cheapest real test for each (what, with whom, by when, what result kills it)
## The first sale: where the first customers are, what they buy first, at what price
## What is real so far, and what is only believed
## The questions I would ask the founder
## If FUND IF: the conditions (each one a real-world test, not "do more research")
```

## Step 3: the chair's summary

Read the five memos (they are short) and write `founder/board.md`:

0. **The hard truth:** the single most likely reason this business dies, in
   one or two plain sentences. This comes first, before the vote.
1. The vote, e.g. "2 fund if, 2 pass", and the average score.
2. The risks more than one member raised: these go first.
3. Every condition, merged, as a checklist. Mark which ones only real buyers
   can tick off (most of them), and which the CFO or the competitor scout can.
   The simulated panel can raise doubts about a condition; it can never tick
   one off.
4. **The kill list:** the three tests to run first in the real world, with the
   result that would mean stop. Put the riskiest assumption first, tested on
   its own, and prefer tests that can run within two weeks (Ready, Fire, Aim,
   rule 11 in `rules.md`).
5. **The stage and the first sale:** which stage the business is in, and the
   board's best answer to the four selling questions (where, what first, what
   price, what words). Mark each answer as a guess until a real buyer acts.
6. One paragraph: the strongest version of this business the board can see.
   It may differ from what the user pitched; say so plainly.

Then log the vote in the ledger as `SIMULATED` (it is model opinion):

```bash
python3 "${CLAUDE_SKILL_DIR}/../receipts/ledger.py" add --kind other --status SIMULATED --use PRIVATE --by shark-board --claim "Board vote: <vote>, average <score>/10"
```

Keep the members' disagreements. A board that agrees on everything was not doing
its job.

## Rules

- Score the business, not the founder.
- No made-up facts. If a lens needs a number nobody has yet (market size, cost of
  acquiring a customer), name it as an open question and say which skill answers
  it (`/ground-truth`, `/truth-serum`, `/burn-test`).
- A PASS is a result, not a failure. Say it plainly.
- If the founder argues with a vote, the board changes it only for new
  evidence, and the chair names that evidence. Arguing harder is not evidence.
- No member treats the panel, another memo or the founder's belief as proof.

## Output

`founder/idea.md`, `founder/board/` (brief and five memos), `founder/board.md`.
Then say the hard truth and the vote, one line each, and suggest the next
step: the first kill-list test with real people (`/receipts` has the
call guide), `/ground-truth` to see who is already there, or
`/truth-serum` to find objections with simulated buyers before the real
calls.

## Where the pack goes next

```
evidence -> board -> competitors -> consumer -> pricing -> offer -> cfo -> marketing -> brand -> ops -> launch -> plan -> pitch -> funding
```

`/receipts` also runs any time a real person does something: a call,
a deposit, a pilot, a no.

Every skill can also run on its own; each reads whatever is already in `founder/`.
