---
name: buildcalmly
description: Run the build calmly loop end to end: sort a request into needs and asks, order the work easiest to hardest, and write a spec for each feature that passes a 39-rule grader, stopping for a human answer three times along the way. Use when someone describes something they want built, when a project is starting from a sentence or a paragraph, or when a paused loop needs picking up from where it stopped.
license: MIT
compatibility: Needs a filesystem to read and write the build record, and a session that can take a reply, because every stage ends at a human answer. Invokes two other skills, which must be installed alongside it and which carry Python 3 scripts of their own. No scripts at this level, no network calls, no application programming interface (API) key.
metadata:
  version: 0.3.0
---

# buildcalmly

The single entry point to the build calmly loop. Three stages, three hard gates, defined in
`workflow.md`. This file routes. That file governs.

Version 1 of the loop runs from a request to a spec and stops there. Design, the prototype, and
the feedback round are deferred, so never offer them.

## The one rule

**Never restate a gate, a stage step, a file path, or the progress marker here.** `workflow.md`
owns all four. A copy in this file becomes a second version that drifts from the first, and the
precedence rule in `workflow.md` beats it silently. Read `workflow.md` before doing anything below.

## What this skill does

Four things, all of them routing:

1. Finds where the person already is, if anywhere.
2. Names the stage that runs next.
3. Invokes the skill that owns it.
4. Honours a stop at any moment, and writes the note that makes the stop resumable.

Everything else belongs to the two stage skills.

## Entry: find the resume point

Look for `build/01 sequence.md` **in the working directory only.** Never walk up the tree to find
one. `build/` sits beside the work it belongs to, so a sequence file in a parent directory belongs
to a different engagement, and offering to continue it names the wrong feature with full confidence.

**No sequence file.** Start at stage 0. Say the loop is starting fresh.

**A sequence file exists.** Read it, then open with a gate. State in plain words what it records:
the feature, the stage, and the answer that was being waited on. Offer three ways forward through
AskUserQuestion: continue from there, pick a different feature already in the sequence, or add
something new at stage 0. Always ask. The file records where a session stopped and carries no
information about whether the person still wants that.

**A `Paused` block is present.** It carries what was in flight when the stop landed. Read it out
before offering to continue, so the person knows what state the work is in.

## Routing

| Stage | Owner |
|---|---|
| 0, 1 | `calm-intake` |
| 2 | `calm-spec` |

Stage 2 is also where the loop closes. Gate 2 offers the next feature in the sequence or the end
of the engagement, and `workflow.md` holds what it has to carry.

Invoke the owning skill with the Skill tool and follow it. Tell it which stage it is entering, and
the feature slug where there is one. When a stage closes green and the next stage has a different
owner, invoke that owner the same way.

**The handoff is advisory.** What holds the order is the entry condition each stage declares in
`workflow.md`, checked on arrival. A skill that finds its entry condition unmet stops and says
which one, whatever invoked it.

## Stopping

The stop contract lives in `workflow.md`, under "Stopping the loop". Follow it there. This skill
adds one case to it: a stop arriving during a routing decision, between two stages, is honoured
exactly like one arriving inside a stage, and writes the same resume note.

## What this skill does not do

- **It does not gate.** Every gate belongs to the stage skill that owns it.
- **It does not talk about machinery.** "How to talk to the person" in `workflow.md` governs every
  word, including the resume offer above. Stage numbers, skill names, and file paths stay backstage.
- **It is not required.** Each of the two skills runs on its own. `calm-spec` in particular is
  built to grade a spec that arrived with no loop around it.
