---
name: calm-spec
description: Interview for the inputs a spec needs, draft the spec from them, and grade any spec against 39 rules covering the ways specs lie, returning a reproducible pass or fail, per-case scores, and a concrete fix for every finding. Stage 2 of the build calmly loop, and a standalone tool everywhere else. Use when someone asks to write, review, grade, tighten, or lint a spec, a product requirements document, a system prompt, an agent instruction file, an eval definition, or a scoring rubric, or asks whether a spec is solid enough to build from.
license: MIT
compatibility: Needs a filesystem and python3 to run the bundled linter, which uses the standard library only, makes no network calls, and installs nothing. Works in Claude Code, in claude.ai with code execution enabled, and through the Skills application programming interface (API). No API key is needed anywhere; the rewrite phase runs in the session itself.
metadata:
  version: 0.7.0
  rule_pack: 0.2.0
---

# calm-spec

One test decides everything here: **a checker outside the loop can pass or fail this spec without
asking the author a question.** Every rule in the pack is a way that test fails.

## Where this sits

This is stage 2 of the build calmly loop, defined in `../workflow.md`. `calm-intake` hands you a
feature and its intake record. You produce a spec that passes the gate, and the loop ends there:
version 1 delivers a spec and does not design or build. Run standalone whenever someone brings a
spec with no loop around it.

That file's section "How to talk to the person" governs every word the person sees from this
skill, standalone runs included. The short version: the score, the rule identifiers, the profile
name, and the `<define ...>` marker stay backstage until the person asks for them.

## The division of labor

The script enforces the form. The person supplies the judgment: the actual threshold, the actual
non-goal, whose interest wins, what done means. Hold that line. The gate is computed only by the
script, so the same document always produces the same verdict. Your reading produces advisories
and fixes, and you never promote one to a gate failure on your own.

## Three phases

Pick the phase from what was asked. `lint` is the common entry. The phases chain: a spec drafted
here is linted here before it is handed back.

---

## Phase 1: interview

Use when someone wants a spec written and has no complete input set yet.

Read `reference/interview.md` for the ten questions and the exact wording.

How to ask:

- **One question at a time.** Never present all ten at once.
- Where the AskUserQuestion tool exists, use it, with two to four labeled options per question so
  the person picks rather than composes. Lead with the option you would recommend and say why.
- **Use the person-facing heading each question carries** in `reference/interview.md`. The names in
  that file's own headings are internal labels, and a question headed "Cheap kill" or "Expiry"
  makes a person guess at what is being asked of them.
- **Write every option in the second person.** An option that describes the person to a third party
  is a defect, however accurate it is.
- Where that tool is absent, ask in plain prose, still one at a time.
- Where the session cannot take a reply at all, ask all ten in one pass, answer what the supplied
  material already settles, and list the gaps. Never invent an answer to fill one.

Four answers block the draft: **intent, result, tie-breaker, check.** Missing any one of them, say
which is missing and why it blocks, then stop. Do not draft around a gap.

Write the answers to `intake.md` next to where the spec will live. That record is the spec's
provenance.

---

## Phase 2: draft

Use when a complete intake exists.

Read `reference/spec-template.md` for the output shape, then write the spec into it.

Two rules govern the drafting:

1. **Never invent a number.** A threshold the intake did not supply is written as
   `<define threshold>` and listed in the notes at the end. A fabricated number reads as rigor and
   behaves as a lie. To the person, that marker is described as a thing left open: "one thing is
   open on purpose, which is where the scores come from".
2. **Preserve the author's wording** wherever it already sorts cleanly into a constraint, a
   default, or an aspiration.

Then run phase 3 on your own draft. Fix what the gate reports, re-run, and repeat until the gate
is green. Hand back the spec, the gate result, and anything still marked `<define ...>`.

---

## Phase 3: lint

Run the script first. It is fast, reproducible, and it needs no reading on your part:

```bash
python3 scripts/spec_lint.py <file.md>              # profile inferred
python3 scripts/spec_lint.py <file.md> --profile agent
python3 scripts/spec_lint.py <file.md> --json       # for chaining
```

Profiles: `product` (a product requirements document or feature spec), `agent` (a system prompt or
agent instruction file), `eval` (an eval definition or scoring rubric). The script infers one when
none is given. Confirm the inference with the person if the document sits on a boundary.

Exit code 1 means a hard gate is red.

### Then add the judgment layer

The script prints the rules it cannot decide. Read the document and work through each one. They are
listed with their full check text in `rules/RULES.md`, identified by an `R` suffix:

- `SL-00.1R` is the target stated positively and by example, or only by prohibition
- `SL-00.2R` are there examples, and do they cover the hard cases
- `SL-00.3R` does the spec say what happens when the system is unsure or the input is bad
- `SL-01.2R` is the stated check real, mechanically runnable, and outside the builder's influence
- `SL-02.3R` do any two hard rules silently contradict
- `SL-04.4R` would two readers build the same thing from each requirement
- `SL-05.4R` is any rule faking precision in a domain that needs judgment
- `SL-06.7R` does the acceptance measure the goal or a cheaper proxy
- `SL-09.5R` is the spec self-sufficient

**Quote the line before you judge it.** A judgment finding with no quoted evidence does not ship.
Anything you cannot quote has not been established.

Every rule in `rules/RULES.md` carries a before-and-after pair and one sentence naming the call
that stays with the person. Use the pair when proposing a replacement line. When a finding turns
on a number, a ranking, or a non-goal only the author can supply, name that call and ask for it
rather than inventing one.

### Reporting back

Two audiences read this. The record on disk gets the full grading. The person gets what it means,
under "How to talk to the person" in `../workflow.md`.

**To the person, in this order:**

1. **The verdict in one sentence.** "The spec holds up." Or "the spec has a hole in it, here."
2. **What is still soft**, one line each, each named as a thing in the world. A rule you are
   setting aside gets its reason in the same line, so the person can audit the dismissal without
   the rule pack.
3. **Anything left open on purpose**, with where it gets decided.
4. **The one change that would move the spec furthest**, in a sentence.
5. **The offer**, once: *say "show me the grading" any time.*

**On request, and only then:** the script's verdict verbatim, the gate, the score, the per-case
table, the rule identifiers, and the suppression syntax.

Never open with the score. A reader without the rule pack cannot tell whether 48 of 56 is good,
and a number offered as proof of rigor reads as noise.

**A judgment finding is reported as the case it would break on.** Quote the line, then give the
real situation where two builders would build different things. This one is the model:

> Your words were "the day after every win at the stadium". The spec I drafted says "a home game".
> Those come apart when the league schedules a home game at a neutral site, and a builder reading
> the spec would count that day while you would not. Which one do you mean?

### Closing gate 2, inside the loop

Gate 2 is the last gate, so it closes the feature and it closes the engagement. `../workflow.md`
under GATE 2 is the contract. Four things belong here, in this order:

1. **The progress marker.** Run `python3 ../calm-intake/scripts/say.py gate 2` and put its line at
   the top of the gate question. Never retype it. Say the sequence position in words beside it,
   for instance "feature 2 of 4 specified, 2 queued".
2. **Every unresolved `<define ...>`, read out** as a thing left open, in plain words. The person
   decides whether one blocks.
3. **What happens next, through AskUserQuestion.** Two routes: the next feature in the sequence,
   which leads while the sequence still has items in it, or the engagement finished. A person who
   wants something else says so, and that stands. Never start the next interview because the
   sequence made it obvious.
4. **The file list, when they call it finished**, each file named in plain words for what it holds,
   plus one sentence on what the spec is for: hand it to whoever builds, or bring it back when it
   is time to build.

Standalone, there is no loop, no marker, and none of the four.

**Closing the session** rather than the gate, say what was settled in the person's own terms, then
the words that resume it. File paths and the status word go in one line at the end, or nowhere.

Do not rewrite the person's spec unless they ask. Findings and fixes, not a silent edit.

**When they do ask for the rewrite**, you do it yourself in this session: read
`reference/rewrite.md` and follow it. Out comes the spec restructured into Goals, Non-Goals,
Constraints with checks, Defaults with overrides, Aspirations with metrics, Precedence, and an
audit of every line reclassified. Lint your output before handing it back.

---

## Reference files

Read these only when you need them.

| File | What is in it |
|---|---|
| `rules/RULES.md` | All 39 rules: why each exists, what is checked, the fix, a before-and-after pair, the call that stays with the person, per-profile severity |
| `rules/rules.json` | The registry the script reads. Both layers read this one file |
| `reference/interview.md` | The ten intake questions, the blocking four, and the option sets |
| `reference/spec-template.md` | The output shape the draft phase fills |
| `reference/rewrite.md` | The brief for rewriting an existing spec into Constraint, Default, Aspiration (C/D/A) form, in-session |
| `reference/principles.md` | Where each rule comes from and how to game this linter |
| `corpus/` | Labeled fixtures and the measurement of the rules against them |

## Suppression

A rule that misfires can be silenced in the document itself, on the line above the offending line
or anywhere in the file:

```
<!-- calm-spec: ignore SL-04.1 -->
<!-- calm-spec: ignore-file SL-04.1 SL-03.3 -->
<!-- calm-spec: profile agent -->
```

The prefix `spec-lint:` still parses, for documents written before the rename.

Suggest a suppression when a word-level rule fires on a true positive that the author has good
reason to keep. Never add one yourself to make a gate pass.

Offer the syntax above only to a person who asked for the grading. To anyone else, a misfiring rule
is reported as your call and the reason for it, with no comment string to paste.

## What this tool does not do

It cannot tell you whether the spec was worth writing. A document can satisfy every form rule and
still specify the wrong thing. That residual is taste, it belongs to the person, and naming it is
part of the honest use of this tool.
