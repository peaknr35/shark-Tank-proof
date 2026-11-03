---
name: ground-truth
description: >-
  Maps every competitor and the gap they leave. Finds the direct competitors,
  indirect ones and the substitutes a buyer would use instead, from public
  sources only, and records what each sells, at what price, how they position
  themselves and what their customers complain about in public reviews, every fact
  with a link. Ends with a positioning map and the gap the new business can own.
  Use when the user says "who are my competitors", "is this market crowded", "what
  else is out there", "competitor analysis", "find the gap", or "who am I up
  against".
argument-hint: "[city or market]"
---

# ground-truth

Every buyer already solves this problem somehow. This skill finds out how, what
they pay, and what they hate about it, so the new business starts with a gap
instead of a guess.

Read `${CLAUDE_SKILL_DIR}/../receipts/rules.md` first.

## The rules

- **Public sources only, every fact linked.** Websites, price pages, menus, app
  store and Google Maps listings, review sites, Reddit, news. If a source cannot be
  reached, say so. Never invent a competitor, a price, a rating or a review.
- **Read, do not scrape.** Read pages as a person would. Respect each site's terms.
- **Quotes are verbatim**, short, with the link. They are research, never
  testimonials.

## Step 1: who is there

From `founder/idea.md` (write it first if missing; see `/shark-board` step 0):

| type | what it means | example for a matcha café |
| --- | --- | --- |
| Direct | sells the same thing to the same buyer | other matcha bars within walking distance |
| Indirect | a different product for the same job | the coffee shops on the same street |
| Substitute | how buyers solve it without a business | matcha powder at home, canned drinks |

Aim for 5 to 10 direct and indirect, plus the main substitutes. For a local
business, search the map for the exact area; for online, search how a buyer would
("best <thing> for <who>", "<thing> alternative").

## Step 2: the facts

One row per competitor in `founder/competitors.csv`:

`name,type,url,location_or_channel,price_of_comparable_item,what_it_sells,positioning_line,rating,review_count,source_date`

`positioning_line` is their own headline or tagline, copied. Price is for the item
closest to what the new business sells, with what it includes.

## Step 2b: how they sell

A competitor's selling strategy is the fastest lesson a new business can get
(Ready, Fire, Aim, rule 11 in `rules.md`): copy what works, then be different in
one thing. For the top 3 to 5, from public sources, record in
`founder/competitors.md`:

- **Where** they find customers: the ads, lists, searches, shelves, partners
  and channels they show up in. An ad a competitor keeps running for months is
  probably making money; note how long each has run when you can see it (ad
  libraries, dated posts, archived pages).
- **What** they sell first: their entry product or offer (a sample, a trial, a
  starter kit, a first-visit deal), and what they try to sell next.
- **At what price** they win a first customer, and what it rises to.
- **With what words**: their main promise and the proof they show.

If the founder can, suggest a 15-minute call with someone who markets for a
company in the same field (not a direct rival): how they find customers, what
the first sale is, what a customer is worth. Log what they say as `THEY SAID
IT` with the call note as evidence.

## Step 3: what their customers say

For the top 3 to 5, read their reviews (1 to 3 stars first, then the "love it,
but..." 4 stars). Note recurring complaints as themes with counts and one or two
linked quotes each. Mark a theme thin if it has under three reviews.

## Step 4: the map and the gap

Write `founder/competitors.md`:

0. **The hard truth**: how crowded it is, and whether a buyer has any reason
   to switch.
1. The table (from the CSV), sorted by how directly each competes.
2. Price range: lowest, median, highest for the comparable item.
3. A positioning map in text: two axes that matter to this buyer (price and
   convenience, quality and speed...), where each competitor sits.
4. The complaints, ranked, with links.
5. **The gap**: what nobody does well that this business could, tied to the
   evidence. If there is no gap, say so plainly; that is the most useful result
   this skill can give. A gap is a hypothesis: nobody doing it may mean nobody
   will pay for it. Name the real-buyer question that would tell.
6. The threat: who could copy the new business fastest, and how.
7. **The selling strategy to copy:** the medium, first product, entry price
   and main promise most competitors share (the industry norm), and the one
   element this business could do differently. Mark it `PLANNED` until tested.

## Output

`founder/competitors.csv`, `founder/competitors.md`. Log the evidence: add one
row to `founder/evidence/evidence-log.md` for `competitors.csv` (public pages,
the date), then log the price range and the top complaint themes as
`MEASURED`, kind `market`, citing it, and the gap as `PLANNED`, kind `market`.
Next: `/truth-serum` uses the complaints to write real objections;
`/litmus` uses the price range.
