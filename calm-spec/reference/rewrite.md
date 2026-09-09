# The rewrite brief

Use this when someone asks for their spec rewritten rather than reported on. You do the rewrite
yourself, in this session, reading the whole document first. No script, no network call, no
application programming interface (API) key. Whole-document context is the point: it finds a real
constraint buried in a list of nice-to-haves, and it finds a document so over-constrained that
nothing is left to optimize.

Write the result to `<input>.rewritten.md` beside the source unless told otherwise. Never
overwrite the source file.

## The three kinds of statement

Every load-bearing line becomes exactly one of these. A line you cannot classify is a line the
reader cannot classify either; rewrite it until you can.

- **Constraint (C)**: a hard rule. Boolean, checkable, non-overridable. Every C carries a
  falsifiable check: a test, an assertion, a type, a lint rule, a gate, a query. A MUST with no
  check behind it is a wish wearing a MUST. The one-question test: can I write a check that fails
  when this is violated?
- **Default (D)**: an overridable starting point, the concrete value the system uses when the
  input does not specify otherwise. State the default and state what overrides it.
- **Aspiration (A)**: a direction to optimize toward. It ranks better against worse rather than
  allowed against forbidden. Every A carries a metric and a direction, or an honest "this is
  taste."

## What to catch

1. **A wish wearing a MUST**: an aspiration written as a hard rule with no check. Either promote
   it to a real C with a check, or demote it to an A with a metric and a direction.
2. **A buried constraint**: a genuine hard rule hidden in a list of nice-to-haves, at risk of
   being traded away under pressure. Lift it into Constraints with a check.
3. **Over-constraining**: so many hard rules that nothing is left to optimize. Relax the ones
   that are really preferences down to Defaults or Aspirations.

## Output shape

One Markdown document, these sections, this order. Omit a section only when the source genuinely
has nothing for it, and say so briefly rather than inventing content.

```
# <Spec title>

## Goals
## Non-Goals
## Constraints (C)      C1, C2, ... each with *Check: <the falsifiable test>.*
## Defaults (D)         D1, D2, ... each with its override
## Aspirations (A)      A1, A2, ... each with metric and direction, or "taste, not a gate"
## Precedence           when guidance conflicts, C over D over A, plus any spec-specific order
## Notes on the rewrite
```

The notes are a short bulleted audit: which lines were reclassified and why, which MUSTs had no
check, anything that could not be classified (flag it, never silently drop it), and every place
intent had to be guessed.

## Rules for how to work

- **Never invent a number.** A threshold or metric the source does not supply is written as
  `<define threshold>` and listed in the notes. A fabricated number reads as rigor and behaves as
  a lie.
- **Preserve the author's wording** wherever it already sorts cleanly into C, D, or A. Preserve
  domain specifics everywhere.
- Keep every check concrete enough that someone could implement it.
- When the source carries sections this shape has no slot for (trust boundary, action classes,
  budgets, feedback gates), keep them: place them after Precedence, before the notes.

## Then lint it

Run `python3 scripts/spec_lint.py <output>.md` on your own rewrite. Fix what the gate reports and
re-run until the gate is green. Hand back the rewrite, the gate result, the audit, and anything
still marked `<define ...>`.
