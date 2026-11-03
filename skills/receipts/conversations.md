# Talking to real buyers

The simulated panel tells you what to ask. Real people tell you the answer.
This is how to run a short call that produces evidence instead of
compliments, and how to log it. The method is a summary, in our words, of the
customer-conversation approach in Rob Fitzpatrick's *The Mom Test* (2013) and
Steve Blank's customer development. Not their words, and not endorsed by them.

## Before the call

- Pick the one thing you most need to learn (from the board's kill list or the
  biggest `PLANNED` claim in the ledger).
- Write down the commitment you will ask for at the end: a second meeting, a
  pilot, a deposit, an introduction. No ask means no evidence.
- Do not pitch for the first two thirds of the call.

## Questions that work

About their life, not your idea. About the past, not the future. Specifics,
not opinions.

1. Walk me through the last time this happened. What did you do?
2. What does it cost you today, in hours, money or mistakes? How do you know?
3. What have you already tried? What did you pay for it? Why did you stop?
4. Who else is involved when this goes wrong? Who signs off on spending?
5. If this were solved, what would you do with the time or money?

## Questions that lie to you

- "Would you buy this?" and "How much would you pay?" (people are polite about
  the future)
- "Do you think this is a good idea?" (you will hear yes)
- Anything that starts with your solution

## The ask

End with one real commitment, sized to where you are: "Can I show you this
running on one of your real cases next Tuesday?", "Would you run a three-week
pilot on Schedule C reviews?", "Would you put down a $200 deposit to hold a
founding spot?" A yes is `MEASURED` demand. A "maybe later" is a no for now.
Write down which.

## Logging the call

1. Save your notes as `founder/evidence/calls/<date>-<who>.md`: who, role,
   date, their words on the problem, their numbers, what they tried, the ask
   and the answer.
2. Add a row to `founder/evidence/evidence-log.md` (`e07 | Call notes, J. Doe,
   managing partner | call | 2026-11-04 | ASK FIRST`).
3. Add the claims with `ledger.py add`, one per fact. Their past numbers are
   `THEY SAID IT`. A yes to the ask is `MEASURED`, kind `demand`, with
   `--commitment` naming what they did (paid, deposit, signed, booked, intro). Praise is
   `THEY SAID IT`, kind `other`.
4. Add the person to `founder/evidence/people.md` with whether you may name
   them.

Five honest calls beat a hundred simulated buyers. Ten calls where nobody takes
the ask is the clearest result the pack can give you.
