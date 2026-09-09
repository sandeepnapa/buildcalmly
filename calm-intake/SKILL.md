---
name: calm-intake
description: Sort an inbound request into needs, asks, and mechanisms, confirm every ruling with the person, then order the confirmed work easiest to hardest and get the first item picked. Stages 0 and 1 of the build calmly loop, normally entered through the buildcalmly skill rather than directly. Use directly only to sort or sequence a backlog that already exists, with no loop around it.
license: MIT
compatibility: Needs a filesystem to write the intake and sequence records, and Python 3 to run `scripts/say.py`, which prints the opening and the progress marker. No network calls, no application programming interface (API) key. Needs a session that can take a reply, because every stage ends at a human answer.
metadata:
  version: 0.8.0
---

# calm-intake

Stages 0 and 1 of the build calmly loop, defined in `../workflow.md`. Read that file for the gates,
the file layout, and the section "How to talk to the person", which governs every word the person
sees here. This skill covers how to run the two stages it owns.

## The one rule

Never rule on an item for the person. The agent classifies, argues its case once, then records what
the person decided.

## The second rule

The test identifiers live in the record on disk. The person hears the finding in plain words. See
"How to talk to the person" in `../workflow.md`.

## The briefs

| File | Read it when |
|---|---|
| `reference/classify.md` | Classifying any item: the eight tests, the record format, the exemptions, the near misses |
| `reference/questions.md` | Opening a session, and asking anything: what `scripts/say.py` prints, then the option sets for every stage 0 and stage 1 question |
| `reference/reframing-bank.md` | An ask names a mechanism and the problem behind it is not obvious |
| `reference/worked-example.md` | First time through, or when a request carries several items at once |

## The script

`scripts/say.py` prints the two things this skill says that an agent otherwise skips:
the opening, and the progress marker. Run it and paste the output verbatim. It is the source of
truth for both strings, and the copies in `reference/questions.md` and `../workflow.md` follow it.

```
python3 scripts/say.py opening                 the opening, ending in the invitation
python3 scripts/say.py opening --request TEXT  the same, ending in a reflection of their words
python3 scripts/say.py gate N                  the marker for gate N, 0 to 2
```

Run it from this skill's root. Never retype either string by hand, and never paraphrase what it
prints. A paraphrase is the failure this script exists to make impossible.

---

## Stage 0: intake

**Entry:** a person describes what they want, in any form.

1. **Open with the route.** Run `python3 scripts/say.py opening` and paste its output as your
   first message, before anything else. Pass `--request "<their verbatim words>"` when the request
   arrived with the invocation, which is the common case. Once per engagement, before anything is
   classified. A person who does not know a spec is coming reads the spec interview as an
   interrogation, and the opening also says where the loop ends, so nobody waits for a prototype
   that is not coming.
2. **Capture verbatim.** Write the request down before interpreting it. The original wording is
   evidence, and paraphrase destroys it. When the request arrived with the invocation, reflect it
   back rather than asking for it again.
3. **Split into items.** One sentence often carries three requests. Split on the verbs, then
   confirm the split (Q0.1) before ruling on anything.
4. **Classify each item** as a need, an ask, or a mechanism, using the eight tests in
   `reference/classify.md`. Tests AN-1 through AN-5 decide whether a need has been found. AN-6
   through AN-8 size it. Record which tests passed and which failed, per item, in
   `build/00 intake.md`. Say the result to the person as one sentence about their problem: what
   makes this real, what is thin, and what you propose anyway.
5. **For every mechanism, write the problem it appears to solve**, marked plainly as an inference,
   and confirm it (Q0.3). A mechanism the person says is the requirement takes an exemption (Q0.4)
   and travels with the needs.
6. **Gather missing evidence** with the ladder in `reference/classify.md`, through Q0.5. Never fill
   a field the person did not supply.
7. **Get every ruling confirmed** (Q0.2). Batch the obvious ones, take the contested ones one at a
   time. Lead with the class you would defend and give the one plain sentence that decides it.

**Writes:** `build/00 intake.md`, one block per item in the record format `reference/classify.md`
gives.

**GATE 0.** Every item carries a ruling the person made. No inference is left standing.
Marker: run `python3 scripts/say.py gate 0` and put its line at the top of the gate question. It
carries the gloss on the word "gate", which shows here and nowhere else.

---

## Stage 1: sequencing

**Entry:** gate 0 is green.

1. **Take the confirmed needs and the exempt mechanisms.** Record what was dropped and why, in the
   same file.
2. **Order easiest to hardest.** Easiest means fewest unknowns, fewest dependencies, smallest blast
   radius when it is wrong. Effort is the weakest of the three signals; uncertainty is the
   strongest.
3. **State every dependency edge.** An item that unblocks three others may move ahead of its
   difficulty rank. Say when you have done that and why (Q1.2).
4. **Name any date against the order** (Q1.3). The loop does not estimate, so the person decides
   whether a date outranks difficulty, and the override is recorded as theirs.
5. **Present the order** (Q1.1): the sequence you recommend first, then one or two defensible
   alternatives, each labeled with what it optimizes for.

**Writes:** `build/01 sequence.md`. Every feature starts at status `queued`. This file is the
loop's resume point, so it carries status for the whole engagement.

**GATE 1.** The person has named the feature to specify first (Q1.4).
Marker: run `python3 scripts/say.py gate 1` and put its line at the top of the gate question.

---

## Handing off

Say what is starting, in the person's own terms, then invoke `calm-spec` on it. Name the feature
and what the next stretch of questions is for. Skip the skill name, the stage number, and the file
paths. Do not draft any part of the spec here. Intake answers what and why; the spec answers how
well, and it has its own interview.

> Starting on the reply notification. Next is ten questions on what it has to do and how you
> would know it worked.

`calm-spec` also closes the loop. When its gate goes green it offers the next feature in the
sequence, so a second pass through stage 1 is never needed. Read `../workflow.md` under GATE 2 for
what that gate carries.

## What this skill does not do

- It does not estimate. No dates, no points, no effort in hours.
- It does not decide the work is worth doing. It sorts what was asked for.
- It does not build. Nothing in stages 0 and 1 touches code, and version 1 of the loop stops at a
  spec, so nothing downstream touches code either.
