---
name: straight-talk
description: >-
  Your brand designer. Names the business (with the trademark, domain and handle
  checks to run before falling in love with a name), writes the voice, a one-line
  promise and a tagline, and briefs the look: colours, type, logo and the first
  things a customer sees, so they match the positioning the marketing director
  chose. Use when the user says "name my business", "brand this", "logo", "brand
  identity", "what should it look like", "tagline", or "brand voice".
argument-hint: "[name ideas, if any]"
---

# straight-talk

A brand is the promise a customer remembers. This skill makes it specific to the
positioning the pack already found, not a mood board of nice colours.

Read `${CLAUDE_SKILL_DIR}/../receipts/rules.md` first. A brand that
promises more than the business has delivered is the fastest way to lose a
first customer.

## Step 1: read the brief

`founder/idea.md`, `founder/marketing.md` (the positioning line and the first
audience), `founder/competitors.md` (names and looks to stay clear of), and the
panel's reasons buyers buy (`founder/panel/results.md`). If the positioning is
missing, ask for it or run `/signal` first.

## Step 2: name candidates

Ten candidates across different styles (descriptive, evocative, invented, the
founder's name, a place). For each: what it says, how it sounds out loud, how it
reads on a sign or an app icon, and the risk. Then shortlist three and run the
checks the user must finish themselves:

- **Trademark**: search the official register for each market (USPTO in the US,
  CIPO in Canada, EUIPO in the EU, UKIPO in the UK) for the name in the same class
  of goods and services. Give the search links and the classes to check.
- **Domain**: whether the .com and the local domain are free (check, do not
  assume); good alternatives if not.
- **Handles**: Instagram, TikTok, X, YouTube.
- **Confusion**: no name close to a competitor in `founder/competitors.md`.

Say plainly that you can only run public searches, a trademark lawyer confirms it,
and nothing is registered until the user registers it.

## Step 3: voice and promise

- The one-line promise (what the customer can count on, every time), built
  from one big idea and one big benefit to the buyer, not a list. It must
  be something the business can deliver on day one, from `founder/ops.md`.
  If it rests on a `PLANNED` claim, say so and offer a promise it can keep now.
- A tagline, three options.
- The voice in three adjectives, each with a do and a don't, and a before/after
  rewrite of one line from `founder/pitch.md`.

## Step 4: the look, as a brief

- **Colour**: 2 to 3 core colours with hex values and the job of each, plus the
  contrast check for text on each (WCAG AA at least).
- **Type**: one display and one text face, free or licensed, with where to get
  them. No font the user does not have a licence for.
- **Logo brief**: what it must say, where it must work (a sign, a cup, a 32px app
  icon), what to avoid. Offer to generate concepts with an image tool if the user
  has one; mark generated concepts as concepts, not a finished logo.
- **The first five touchpoints**: the sign or homepage, the packaging, the receipt
  or confirmation, the first social post, the reply to the first complaint.

## Rules

- Never copy a competitor's name, logo, colours or tagline.
- No "trusted by", "award-winning", "the leading" or any claim the ledger
  cannot back for a public audience.
- Spend little on brand before a real buyer has paid. A name and a clean page
  are enough to run the first test; say so if the founder wants more first.
  In Stage One the job is selling the product, not making the company known
  (Ready, Fire, Aim, rule 11 in `rules.md`). Do the brand in two passes: the
  minimum to sell now (name, one promise, a plain page or sign), and the rest
  after the first sales show which promise buyers respond to.
- No fonts, images or icons the user has no right to use.
- Not legal advice on trademarks.

## Output

`founder/brand.md`. Next: `/reality-check` and `/prove-it`.
