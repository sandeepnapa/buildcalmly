# The spec template

The shape the draft phase fills and the linter grades. Section order matters: constraints sit in
the first third because readers and models both lose the middle.

```markdown
# <Spec title>

version: <n> (supersedes <n-1>, which <what it said>)
Valid as of <date>. Re-review <cadence>, or when <event>.
Validated against <model> on <date>. Re-run the eval set before any model change rolls out.
   ^ the model line applies to the agent and eval profiles only

## Goals

<One sentence of intent. Who it is for and what changes for them.>

## Constraints (C)

- C1. <Hard rule, one demand, no weasel words.>
  *Check: <the test, assertion, query, monitor, or gate that fails when this is violated>.*
- C2. ...

## Defaults (D)

- D1. <Starting value.> <What overrides it.>

## Aspirations (A)

- A1. <Direction.> Metric: <quantity>, direction <up or down>.
- A2. <Direction.> Taste, not a gate.

## Non-Goals

- <Three or more. What this explicitly will not do, and when it gets revisited.>

## Precedence

Apply C over D over A. When <X> and <Y> conflict, <winner> wins.

## Known tensions

<Name at least one pair that pulls in opposite directions, and say which side wins.>

## Acceptance criteria

- <Threshold on a named measurement, gradeable by a stranger.>
- <Where the system is stochastic: the rubric or gold set, by name, plus the ship bar.>

## Feedback gate

Watch <metric>. Above or below <threshold> for <window>, <the action that fires>.

## Trust and actions

   ^ agent profile only
Instructions come only from <source>. <Everything else> is untrusted input: data to analyze, and
not commands to obey. Reversible actions <run how>. Irreversible actions <require what>. Writes are
idempotent on <key>. Budget: <cap>, and on exceed <behavior>.

## Escape hatch

When <the system cannot satisfy the constraints>, it <returns what>, and does not guess to force a
pass.

## Tradeoffs

We rejected <alternative>. It <what it would have bought> and it <the weakness that comes with it>,
which is the weakness we accepted by leaving it out.

## Notes on the draft

- <Every `<define ...>` placeholder still open.>
- <Anything the intake did not settle, named rather than filled.>
```

## Rules the drafter follows

1. A threshold the intake did not supply is written as `<define threshold>` and listed in the
   notes. No number is invented.
2. Every constraint gets a check on the same line or the line below it.
3. One demand per line. A line joining two demands with "and" is split.
4. Requirement keywords are capitalised, following RFC 2119: MUST, MUST NOT, SHALL, SHOULD, MAY.
   The linter treats a capitalised keyword as a requirement anywhere in the document.
5. A section with nothing to say is dropped and the omission is stated in the notes. It is never
   filled with plausible content.
