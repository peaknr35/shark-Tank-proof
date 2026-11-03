# Shark Tank Proof

**A board that bites before investors do.**

Fourteen Claude skills that test a business before you launch it, then get you
to the first real yes. Free, MIT, no signup, no API key, nothing to connect.

`skills/receipts` `skills/shark-board` `skills/ground-truth`
`skills/truth-serum` `skills/litmus` `skills/dealbreaker` `skills/burn-test`
`skills/signal` `skills/straight-talk` `skills/reality-check`
`skills/prove-it` `skills/kill-or-build` `skills/handshake`
`skills/first-dollar`

## Why this exists

Most startup tools are yes men. A board of model opinions, a panel of model
buyers and numbers built from guesses can make almost any idea look good, and
none of it has met a real customer.

Shark Tank Proof keeps every claim in one ledger with two labels: how we know
it (`MEASURED`, `THEY SAID IT`, `PLANNED`, `SIMULATED`) and who may see it
(`PUBLIC`, `ANONYMISED`, `ASK FIRST`, `PRIVATE`). A guess becomes a fact only
when a real person does something: pays, signs, books, or says no.

- **Profitable needs a real buyer.** If the math works but nobody has paid,
  signed or booked, the verdict is **Unproven**. A simulated panel can fail a
  plan but never pass one.
- **Profitable needs real inputs too.** The price has to be one a real buyer
  paid, and every cost needs a quote or an invoice. A `PLANNED` price or cost
  holds the plan at Unproven. Only the volumes (the ramp, the plan, selling
  days) may stay forecasts. Break-even is `MEASURED` once the price is real
  and every cost is quoted.
- **Every report opens with the hard truth:** the most likely reason it fails.
- **The board has five members**, and the Evidence lens never votes to fund
  without real proof.
- **Sell first, test fast, perfect later** (after *Ready, Fire, Aim*). Every
  skill knows the business's stage, aims at the first profitable sale, and
  tests the riskiest assumption first, with a Plan B and a stop line set
  before the test.
- **A number takes the weakest label of anything it was computed from.** A
  margin worked out from a price the simulated panel picked is `SIMULATED`,
  however clean the arithmetic, so it cannot pass the plan by the time
  `/kill-or-build` adds it all up.
- **Promises are goals.** "3x faster" is logged as planned until it is measured.
- **The first ask is small:** a time-boxed pilot on the buyer's own numbers.
- **Pitches are checked** against the ledger before they go out.

## The fourteen

| command | job | what it does |
| --- | --- | --- |
| `/receipts` | Evidence keeper | The ledger every skill writes to. Logs real calls, deposits, pilots and refusals, audits what is real versus guessed, and lists the gaps. Keeps one story file per project: the problem before, who did what, where it broke. No receipt, no claim. |
| `/shark-board` | Board of directors | Five members, each a sub-agent applying one published framework (Offers, Monopoly, Product, Selling, Evidence), find what would kill the idea, the cheapest test for each, and vote. |
| `/ground-truth` | Competitor scout | Direct competitors, indirect ones and substitutes from public sources, with prices and what their customers complain about, every fact linked. |
| `/truth-serum` | Consumer panel | A swarm of simulated buyers (100 by default) told not to be polite. Surfaces objections and turns them into questions for real calls. Simulated, never proof. |
| `/litmus` | Pricing | A price range from the panel's answers, set against competitors and the margin, plus the real test that settles it. |
| `/dealbreaker` | Offer | Finds every dealbreaker on the way to yes, designs the first yes (often a pilot) and the full offer, every promise logged as planned until delivered. |
| `/burn-test` | CFO | Unit economics, break-even, year 1, cash burn, the bad case, and how many inputs are real quotes. |
| `/signal` | Marketing | Positioning, channels, a 30-day campaign and hooks, using only claims the ledger allows in public. |
| `/straight-talk` | Brand | Names with the checks to run, a voice, a promise the business can keep on day one, and a brief for the look. |
| `/reality-check` | Operations | Suppliers, staffing, routines, tools, permits and a risk register, with real quotes logged. |
| `/prove-it` | Launch | The real-world test first, with a success line and a kill line logged before it runs, then the countdown. |
| `/kill-or-build` | Business plan | The plan with a computed verdict: Incomplete, Not yet, Unproven or Profitable. |
| `/handshake` | Pitch | The thing one real person needs to say yes: a pilot offer, a grant pitch, a one-pager. Checked against the ledger before it goes. |
| `/first-dollar` | Funding | Grants, RFPs, loans and programs that fit, with official links and the first step. Starts from a built-in list of 42 places to look in the US, UK, EU and beyond. |

## How to use it

Everything lives in a `founder/` folder in your project. Each skill reads what
the others wrote.

```
founder/
  START-HERE.md     the map
  me.md             who is behind it
  idea.md ...       what the other skills write (board, panel, pricing, offer, cfo, plan)
  work/             one story file per project, pilot or client
  evidence/         the ledger (claims.csv), the evidence log, real people, call notes, originals
  opportunities/    one file per customer, funder or internal ask
  outputs/          every pitch, dated
```

One home per fact: a number lives once in the ledger, and every other file
points to it by its claim id.

```
receipts -> shark-board -> ground-truth -> truth-serum -> litmus -> dealbreaker -> burn-test -> signal -> straight-talk -> reality-check -> prove-it -> kill-or-build -> handshake -> first-dollar
```

Run `/receipts` first to set up the folder, and again every time a real person
does something. Any skill also runs on its own, and you can just ask in plain
words: "is any of this real?" runs `/receipts`, "write a pilot offer for a CPA
firm" runs `/handshake`.

What a run looks like, honestly:

1. `/shark-board` opens with the hard truth and a kill list: the three
   real-world tests to run first, and the result that means stop.
2. `/truth-serum --quick` finds the objections in a few minutes and ends with
   the questions to take to real people.
3. `/burn-test` builds the numbers and says how many inputs are real quotes.
4. `/kill-or-build` says **Unproven** if the math works but nobody has paid,
   signed or booked. That is the honest answer for most new ideas.
5. `/handshake` writes a one-page pilot offer for five real buyers.
6. One says yes. `/receipts` logs it, and the plan can say Profitable for the
   first time.

## What's new

- **Ready, Fire, Aim across the pack.** Rule 11: know the stage, sell first,
  find the optimum selling strategy (where the customers are, what they buy
  first, at what price, with what words), answer seven questions before a
  test, keep the plan to four pages, fire when it is good rather than perfect,
  and improve only what sells. The board gains a Selling lens. `/burn-test`
  works out what one customer is worth (first order plus the back end) and so
  the most you can spend to win one, and `/kill-or-build` checks the real cost
  against it. `/ground-truth` maps how competitors sell, `/signal` builds the
  main ad on four legs (big idea, big benefit, big promise, proof from the
  ledger), and `/prove-it` opens with the seven questions.

- **Labels travel through the math.** The break used to be at the handoff
  between skills: `/litmus` set a price from the simulated buyers, `/burn-test`
  worked out the margin from it, and the margin reached the verdict looking
  like a fact. Now every handoff file carries its labels (the method is
  Interpretable Context Methodology: stages are folders and files a person can
  open between steps). `ledger.py add --from c07,c08` gives a computed claim the
  weakest label of its sources and refuses a stronger one. `numbers.json`
  points each input at its claim, `unit_economics.py` prints the label of every
  result and the input that set it, and `compile.py` will not say Profitable
  while a money check passes only on a simulated input. Rule 10 in
  `skills/receipts/rules.md`.
- **The folder is an ICM workspace.** `ledger.py init` writes
  `founder/CONTEXT.md`, the stage map: each skill as a numbered stage, what it
  reads, what it writes and what it hands on. `/litmus` and `/burn-test` write
  their results, labels and the inputs that set them to
  `founder/handoff/04_litmus.json` and `06_burn-test.json`, files you can open
  between stages. `ledger.py trace c09` shows where a computed claim came from,
  down to the originals, and `/kill-or-build` flags a handoff whose labels went
  stale after a source changed.
- **A funding list.** `/first-dollar` starts from 42 grants, procurement
  portals and programs (NSF Seed Fund, SBIR.gov, SAM.gov, Innovate UK, EIC,
  IRAP, startup credits and more), each with its link, who it is for, how to
  start and the date it was checked. Confirm amounts and deadlines on the
  official page before you use them.
- **Project story files.** `founder/work/` holds one file per project, pilot or
  client: the problem before, who did what, where it broke, what is still
  unproven, and one sentence to reuse in pitches.
- **A better interview.** `/receipts` now asks about each project, and asks
  whether you may use a person's words and name before anyone is quoted.
- **Folder rules.** One home per fact, originals stay original, small files,
  private stays private.
- **Peers count.** Someone in your cohort or network who runs your build on
  their own work is a real case study, and the people template says so.

## Install

Copy the skill folders into your Claude Code skills folder. Keep all fourteen
together: they share `rules.md` and `ledger.py` in `receipts`.

```bash
cp -r "shark Tank proof/skills/"* ~/.claude/skills/
```

Or as a plugin, inside Claude Code, from the folder that holds this one:

```
/plugin marketplace add "./shark Tank proof"
/plugin install shark-tank-proof@shark-tank-proof
```

As a plugin the commands get a prefix, like `/shark-tank-proof:shark-board`.
Start a new session after installing. If the older Founder skills are
installed, move them out first so there are not two packs answering the same
questions.

The tools need Python 3.8 or newer. Nothing to pip install.

## The tools

All standard-library Python. None touch the network.

```bash
python3 skills/receipts/ledger.py init
python3 skills/receipts/ledger.py add --claim "2 of 5 firms agreed to a pilot" --kind demand --status MEASURED --use ANONYMISED --number "2 of 5" --evidence e04
python3 skills/receipts/ledger.py add --claim "Recommended price" --kind price --use PRIVATE --number "$6.50" --from c07
python3 skills/receipts/ledger.py summary
python3 skills/receipts/ledger.py scan founder/outputs/2026-11-02-acme.md --audience public
python3 skills/burn-test/unit_economics.py founder/numbers.json --out founder/cfo.md --handoff founder
python3 skills/truth-serum/panel.py init --customer founder/customer.json --pitch founder/pitch.md
python3 skills/litmus/van_westendorp.py founder/panel/answers --price 6.50 --handoff founder
python3 skills/kill-or-build/compile.py --dir founder
```

**`ledger.py`** keeps the claims. `add` refuses a `MEASURED` or `THEY SAID IT`
claim with no evidence file behind it, and a logged no ("0 of 5") never counts
as a buyer. A claim added `--from` other claims takes the weakest of their
labels, and `check` flags one that says more than its sources. `gate` lists what a pitch to an audience may use (never
`SIMULATED`, never `PRIVATE`). `scan` checks a finished pitch: every cited
claim must pass the gate, and proof words like "validated" are flagged when no
real buyer has paid.

```bash
python3 -m unittest discover -s tests -v
```

## Fine print

**Not affiliated with Shark Tank, Dragons' Den or their producers.** The name
is a description of what the board does. If you publish or sell this pack,
check the name with a trademark lawyer first.

**The board applies published frameworks. It is not those people.** The five
lenses are short summaries, in our words, of ideas from *$100M Offers* by Alex
Hormozi, *Zero to One* by Peter Thiel with Blake Masters, Walter Isaacson's
biography of Steve Jobs, *Ready, Fire, Aim* by Michael Masterson, and *The Mom
Test* by Rob Fitzpatrick. The board never speaks as them, quotes them or claims
they endorse anything. Rule 11 and the selling advice across the pack are
likewise our own summary of ideas from *Ready, Fire, Aim*.

**The consumer panel is simulated buyers, not customers.** It finds objections
and questions. It never counts as demand and never appears in a pitch as proof.

**The numbers are only as good as the inputs.** Check costs with suppliers and
the structure, payroll and tax with an accountant.

**Research uses public sources, with links.** No invented competitors, prices,
reviews, quotes, advisors, grant amounts or deadlines.

**Not financial, legal or tax advice.**

## Credit

Built on the Founder skill by Jake Schincariol
([opusjake.ai](https://opusjake.ai), MIT) and the Next Yes evidence-folder
method. The original copyright notice is kept in `LICENSE`.

## License

MIT. Take it, change it, ship it.
