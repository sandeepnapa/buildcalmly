# Classify: the eight tests behind a stage 0 ruling

The rubric the agent runs on every item at stage 0 of the loop in `../../workflow.md`. The same bar
as the rest of the loop applies: a checker outside the loop can pass or fail the classification
without asking the author a question.

## Vocabulary

`workflow.md` rules an item as one of three **classes**, and the class is always the person's call:

| Class | What it is | The test |
|---|---|---|
| Need | A problem with evidence behind it | Something observable is worse because this is unfixed |
| Ask | A request with no evidence yet | Nobody has said what breaks if it is skipped |
| Mechanism | A named solution standing in for an unstated problem | It names a tool, a screen, or a technique instead of an outcome |

The eight tests below produce a **verdict**, which is the evidence the agent offers for the class
it proposes. Three verdicts exist:

- **Need found.** Tests 1 through 5 pass. Propose class `need`.
- **Ask only.** One or more of tests 1 through 5 fail and no exemption applies. Propose class `ask`,
  or `mechanism` when the item names a solution.
- **Ask is the requirement.** The item names a mechanism and one exemption applies. Propose class
  `mechanism`, marked exempt. At stage 1 an exempt mechanism travels with the needs, because the
  exemption is its evidence.

Tests 6 through 8 size an item and never block a ruling on their own.

## The record

One block per item in `build/00 intake.md`:

```markdown
### Item <n>: <short label>

- Quoted: "<verbatim wording>" (<requester role>, <date>)
- Feels the pain: <the person doing the work, when the requester is a proxy>
- Need statement: When <situation>, I want to <motivation>, so I can <outcome>.
- Mechanisms: <three, one of them "build nothing">
- Evidence: <dated occurrence, what they did, what it cost>
- Workaround: <what they do today, or "abandon the task">
- Convergence: <n> sources: "<wording A>", "<wording B>"
- Cost of leaving it: <hours, money, or a named deal>
- Tests: AN-1 pass, AN-2 pass, AN-3 fail (prediction in evidence), ...
- Verdict: need found | ask only | ask is the requirement (<exemption>)
- Proposed class: need | ask | mechanism
- Ruling: <class>, by <person>, <date>
```

An item whose Ruling line is empty holds gate 0 red. An item whose Ruling disagrees with the
Proposed class stands as ruled, with the agent's one sentence of argument recorded above it.

## What the person hears

This record is the audit trail, and it is written for the file. The person hears three sentences:
what makes this real, what is thin, what you propose anyway. The Tests line never appears in a
reply, a question, or an option description. Neither does the word Verdict.

> Backstage: `Tests: AN-1 pass, AN-2 pass, AN-3 fail (recurring, no dated instance), AN-6 fail
> (single source). Verdict: need found.`
>
> Said out loud: "This one is real. It costs you a cheap lunch each time, and it keeps happening.
> The thin part is that you have not pinned a date on any single occasion, and it is only you
> asking. I would still treat it as worth solving."

Say once, at the gate, that the full working is available: *say "show me the grading" any time*.
Print the Tests line only when they ask.

## The tests

HARD gates are binary. SOFT gates are graded and the person's judgment arbitrates, with the
reasoning written down.

### AN-1. The need statement passes the no-product-noun test

- **Artifact:** one sentence: `When [situation], I want to [motivation], so I can [expected outcome]`.
- **Gate (HARD):** no product name, no interface noun (button, dashboard, page, export, toggle,
  filter, report, integration), and no verb that exists only inside the product.
- **Check:** delete every clause after "so I can" and confirm the sentence still names a job the
  person had before the product existed. Then confirm the outcome is something they could report
  achieving without mentioning software.

### AN-2. Three materially different mechanisms satisfy it

- **Artifact:** a list of three, one of which is "remove the obstacle elsewhere and build nothing".
- **Gate (HARD):** three or more, differing in kind rather than in styling.
- **Check:** each can be told apart from the others in one line. Fewer than three means the
  statement is still a solution in need clothing, so return to AN-1.

### AN-3. The evidence is past behaviour

- **Artifact:** at least one recounted instance, with a date or an approximate date, what the
  person did, and what it cost them.
- **Gate (HARD):** the evidence block contains no predicted behaviour.
- **Check:** `grep -nEi '\b(would|will|if we|might|plan to|expect to)\b'` over the evidence block.
  Every hit is a prediction. Rewrite it as something observed, or cut it.

### AN-4. The workaround is named, or its absence is stated

- **Artifact:** what the person does today, including "nothing, they abandon the task".
- **Gate (HARD):** the field is filled.
- **Why:** the workaround supplies frequency and cost, the two inputs to sizing. A request with no
  workaround and no abandonment describes a preference, which belongs in a backlog.

### AN-5. The words are quoted, once, verbatim

- **Gate (HARD):** at least one direct quotation from the requester, attributed and dated.
- **Why:** a paraphrase carries the agent's interpretation already baked in, so the person cannot
  audit the ladder that was climbed.

### AN-6. Convergence is counted

- **Artifact:** the count of distinct sources whose differently worded asks ladder to this same
  need statement, each listed with its original wording.
- **Gate (SOFT):** one source is a hypothesis. Three or more independent sources arriving from
  different asks is the strongest buy signal available without shipping something.
- **Check:** the original wordings differ. Three sources repeating one phrase usually trace to one
  internal briefing, so count that as one.

### AN-7. The requester's role is recorded

- **Artifact:** user, buyer, internal proxy, or executive.
- **Gate (HARD):** the field is filled, and a request arriving through a proxy names the person
  who actually feels the pain.
- **Why:** a request relayed by a salesperson or a founder carries the messenger's need until it is
  traced to the person doing the work.

### AN-8. The cost of leaving it broken is stated

- **Artifact:** the answer to "what happens if this stays as it is", in hours, money, or a named
  deal.
- **Gate (SOFT):** the answer is concrete. A shrug marks a preference, and that is a valid finding
  to write down.

## Gathering the evidence

When an item arrives without the fields AN-3, AN-4 and AN-8 need, ask the ladder, in this order,
about the last real occurrence rather than the future:

1. "When did this last happen? Walk me through what you did."
2. "What did you do instead?"
3. "What did that cost you?"
4. "What happens if it stays this way?"

Then ladder upward with up to three *why* questions, stopping when the answer stops naming the
product. A statement broad enough to justify half the backlog sits one rung too high; drop back
down. `questions.md` gives the option sets for asking these through AskUserQuestion.

## Exemptions: when the ask is the requirement

Discovery costs time, so skip it when the cost of investigating exceeds the cost of building.
Record which exemption applies in the Verdict line. "None of the above" sends the item back to the
tests.

| Exemption | What qualifies |
|---|---|
| Regulatory or contractual | The mechanism is written into the obligation |
| Competitive parity in a live deal | The line item is losing the deal now |
| Cheap and reversible | Days of work against weeks of interviews, and shipping produces better evidence |
| Expert users inside the solution space | Developers specifying an application programming interface (API) shape have usually done the design work |
| Decision already made above | Recorded as such, with the tests marked skipped |

## How a verdict becomes a spec line

`calm-spec` types every load-bearing line as a Constraint, a Default, or an Aspiration, per rules
`SL-01.1` through `SL-01.4` in `../../calm-spec/rules/RULES.md`.

- **Need found** with a falsifiable check becomes a Constraint. With a metric and a direction it
  becomes an Aspiration.
- **Ask is the requirement** becomes a Constraint whose check is the presence of the named
  mechanism.
- **Ask only** produces no line of any type.

## Near misses

These read like need statements and fail:

- *"When I need to export data, I want a bulk export, so I can analyse it."* Interface noun in the
  motivation, and "analyse it" names an activity where the outcome belongs. Fails AN-1.
- *"When I use the dashboard, I want it to be faster, so I can save time."* Product noun in the
  situation, and the outcome sits one rung too high. Fails AN-1.
- *"When onboarding a user, I want a smoother onboarding flow, so onboarding is easier."*
  Situation, motivation, and outcome are the same word three times, so there is nothing to
  falsify. Fails AN-1 and AN-2.

## Traps

- **The solution in disguise.** "Users need a dashboard" is a mechanism with the word *need* in
  front of it. AN-1 catches it.
- **The loudest account.** Volume from a single source is a sample of one. AN-6 is the
  counterweight.
- **Discovery as a delay tactic.** Investigation costing more than the build is waste. The
  exemptions exist for this.
- **Dismissing the requester.** Return the outcome in their own words before proposing any other
  mechanism: "You asked for X so that Y by Friday. Did I get Y right?"
