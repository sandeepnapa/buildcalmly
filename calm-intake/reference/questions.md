# The stage 0 and stage 1 questions

The option sets for every AskUserQuestion call this skill makes, so the wording is consistent
across sessions. Where the tool is absent, ask the same question in prose. Where the session cannot
take a reply at all, stop at stage 0 and report where the loop stopped, per `../../workflow.md`.

**Batching.** Up to four questions per call. Batch rulings the person will find obvious. Take a
contested ruling on its own, with the argument in the option description. Lead every option list
with the choice you would defend and mark it "(Recommended)".

**Voice.** Every string below reaches the person, so it obeys "How to talk to the person" in
`../../workflow.md`. Second person throughout. No test identifier, no class name, no file path, and
no stage number inside a question, a label, or a description. The three class names are recorded on
disk under the labels mapped in Q0.2.

---

## Stage 0

### The opening

The first thing said in any session, before Q0.1 and before anything is classified. It names the
route so the person knows what they have walked into. Say it once per engagement.

**Do not type it. Run it.**

```
python3 scripts/say.py opening
python3 scripts/say.py opening --request "<their verbatim words>"
```

Run from the `calm-intake` skill root and paste the output as the first message. The script owns
these words; everything below is what it prints, kept here so a reader can review the wording
without running anything. When the two disagree, the script is right and this copy is a defect.

Prose instructing an agent to say something is skippable, and an agent that skips it opens cold at
Q0.1 and shows no marker at any gate. Script output pasted verbatim cannot be skipped.

*Hello! My goal is to help you get a real problem written down clearly enough to build from, yours
or your users'. We'll do it in two passes.*

*First, we figure out what's needed. You tell me what you want, I sort the underlying needs from
the asks, and we put them in an order.*

*Then we pin down what the first one has to do. I ask you ten questions, write it up, and check it
against the ways a spec usually goes wrong. What you get is a spec a builder can work from without
coming back to ask you what you meant.*

*At each stage I'll pause and ask for your feedback. We can stop whenever you like and pick up
later from wherever we left off.*

*Whenever you're ready, tell me in your own words, or your users' words, what you'd like to build
or fix. Rough is fine, and messy is genuinely useful. Something like: "People keep asking me for
the same dashboard and I keep rebuilding it by hand."*

*If it helps to have a starting point: what breaks today, who it happens to, and what you do
instead right now. For that same one: "It broke again on Monday. It's mostly the ops team, and
right now I copy last month's file and edit it for an hour."*

**Two passes, three gates.** The opening groups the three stages into two plain passes, because a
person arriving here has no use for a stage number. The gates are unchanged. The first pass covers
intake and sequencing, the second covers the spec.

**The third paragraph says where the loop ends**, in the words "a spec a builder can work from".
Version 1 stops at a document. A person who walked in expecting working code needs to hear that in
the greeting rather than at the last gate.

**No progress marker here.** The count first appears at gate 0, carrying the gloss on the word
"gate" with it. A greeting is the wrong place for `0 of 3 (0%)`, the one value on the scale that
tells the person nothing.

**When the request already arrived** with the invocation, which is the common case, pass
`--request` with their exact words. The script keeps the opening through the pause paragraph and
ends on a reflection instead of the invitation:

*You've already described it: "<their exact words>". I'm taking that as our starting point, so you
don't have to type it twice. Add anything you left out, or just say go and I'll start sorting it
into pieces.*

Never make a person retype what they just wrote. The verbatim capture uses the wording they
already gave.

**Keep the opening to these paragraphs.** The non-goals, the file layout, the gates, and the escape
hatch are all real, and each one lands better at the stage that needs it.

### Q0.1 The split

*I read this request as <n> items: <one line each>. Is that the right split?*

- **Yes, <n> items (Recommended)**: proceed to rulings on this list.
- **Merge two of them**: name which, in Other. One item, one ruling.
- **Split one further**: name which, in Other. A sentence with two verbs is usually two items.

Ask once, before any ruling. A wrong split makes every later ruling wrong.

### Q0.2 The ruling

*You said: "<quoted wording>". I read that as <the proposal, in one plain sentence>. Does that
match?*

- **A real problem worth solving**: something is worse today because it is unfixed, and you can
  point at when it last bit you.
- **Worth doing, though nothing has gone wrong yet**: no one has said what breaks if it is skipped.
- **A solution you already want**: a named solution standing in for a problem still unsaid. Q0.4
  asks what makes it fixed.

Those three labels record as `need`, `ask`, and `mechanism`. The person sees the labels; the record
in `build/00 intake.md` carries the class.

Put the proposal first with "(Recommended)". In the description of the option you argue against,
say what is missing in plain words, for instance "nothing has actually gone wrong yet, so the only
evidence is what might happen". Keep the test identifier in the record, out of the question.

### Q0.3 The problem behind a mechanism

*Behind "<mechanism>", I infer the problem is <inference>. Is that the problem?*

- **Yes, that is the problem (Recommended when the ladder supports it)**: record the need statement
  and rule on it with Q0.2.
- **The problem is different**: state it in Other. Rewrite the need statement and re-run AN-1.
- **The mechanism is the requirement**: go to Q0.4 for the exemption.
- **There is no problem behind it**: rule it an ask. It is recorded and dropped at stage 1.

### Q0.4 The exemption

*Which exemption makes "<mechanism>" the requirement?*

- **Regulatory or contractual**: the mechanism is written into the obligation. Name the document.
- **Competitive parity in a live deal**: the line item is losing the deal now. Name the deal.
- **Cheap and reversible**: days of work against weeks of interviews, and shipping produces
  better evidence.
- **Expert user, or decided above you**: the requester has done the design work, or the decision
  is made and recorded as such.

"None of the above" goes in Other and sends the item back to Q0.3.

### Q0.5 Missing evidence

*Item <n> has no dated occurrence behind it. What do you want to do?*

- **I can supply one now (Recommended)**: answer the ladder. When did it last happen, what did you
  do instead, what did it cost, what happens if it stays?
- **Park it and investigate**: recorded as an ask with a note of who to interview.
- **Drop it**: recorded as an ask, dropped at stage 1.
- **Treat it as a real problem anyway**: recorded as your call, with a note that the evidence is
  still missing.

### Q0.6 Who feels the pain

*"<quoted wording>" arrived through <proxy role>. Who actually does the work this is about?*

Offer the roles the request itself names, then Other. AN-7 holds gate 0 red until this field is
filled for every relayed item.

### Q0.7 Closing gate 0

*That is everything settled: <n> to work on, <n> written down and parked. Ready to put them in
order?*

- **Yes, order them (Recommended)**: write `build/00 intake.md` and start stage 1.
- **Go back to one first**: name which, in Other.

A single item makes the ordering trivial, so say so and fold it into this question rather than
asking twice.

**Marker:** run `python3 scripts/say.py gate 0` and put its line at the top of this question. It
carries the gloss on the word "gate", which shows here and nowhere else.

---

## Stage 1

### Q1.1 The order

*Here is the order I recommend, easiest to hardest, and two alternatives. Which one?*

- **<order A> (Recommended)**: optimizes for fewest unknowns and smallest blast radius.
- **<order B>**: optimizes for unblocking, when one item unblocks others.
- **<order C>**: optimizes for what teaches the most, when the cheapest item teaches the least.

Each option lists the sequence in one line and names what it trades away.

### Q1.2 A dependency override

*<Item> unblocks <items>, so I moved it ahead of its difficulty rank. Keep it there?*

- **Keep it ahead (Recommended)**: the dependency edge is recorded in `01 sequence.md`.
- **Put it back**: rank by difficulty alone, and record the edge as a known tension.

Ask only when a reordering happened. Every reordering is named out loud.

### Q1.3 A deadline against the order

*<Item> carries a date, <date>, and sits at position <n> in the recommended order. Which wins?*

- **Keep the order (Recommended when the date is soft)**: the date is recorded as a known tension.
- **Move it first**: the sequence records that the person overrode difficulty for the date.

Ask only when an item carries a date. The loop does not estimate, so it cannot say whether the
order reaches the date in time.

### Q1.4 Closing gate 1

*Which feature starts?*

Offer the first three items of the agreed sequence, recommended one first. Gate 1 is green when
one is named. An agreed order with no first item named holds the gate red.

**Marker:** run `python3 scripts/say.py gate 1` and put its line at the top of this question.
