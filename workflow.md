# workflow.md: the build calmly loop

The procedure two skills follow to take a request from a sentence to a spec a builder can work
from. It is written for the agent to execute. A person reading it should be able to tell, at any
moment, which stage is running and what is being waited on.

## What version 1 covers

Three stages: sorting the request, ordering the work, and specifying one feature at a time. The
loop delivers a spec and stops there. Design, the prototype, and the feedback round are deferred,
and nothing in this file promises them.

## The one rule

**No stage begins until the person has said yes to the stage before it.** Every gate in this
document is hard. When a gate is red, the agent stops, states what is missing, and waits. Proceeding
on an assumption is a failure of the loop even when the assumption turns out to be correct.

## Precedence

When two of these documents disagree, this order settles it: the person's instruction in the
session, then this file, then a `SKILL.md`, then a `reference/` brief. A `SKILL.md` that contradicts
a stage or a gate defined here is a defect in the `SKILL.md`. Two things this file does not
override, both belonging to a script: the linter's computed gate at stage 2, and the exact wording
of the opening and the progress marker, which `calm-intake/scripts/say.py` prints.

## The two skills

| Skill        | Stages | What it owns                                     |
| ------------ | ------ | ------------------------------------------------ |
| `calm-intake` | 0, 1   | Sorting asks from needs, then ordering the work  |
| `calm-spec`   | 2      | The spec, and the gate that says it is buildable |

Stages 0 and 1 run once per engagement. Stage 2 runs once per feature, in a loop, until the
sequence is empty or the person calls the engagement finished.

## Skills and subagents

A skill loads into the running session. It shares this conversation, so it can use the
AskUserQuestion tool, hold a gate, and wait for a reply. Where that tool is absent, ask the same
question in prose and hold the gate the same way.

A subagent runs in a separate context window and cannot reach the person at all. It receives one
prompt and returns one report.

**Never put a gate inside a subagent.** A subagent that needs an answer will invent one. Subagents
are allowed in exactly one place: **research during stage 0**, meaning prior art, a codebase
survey, or an application programming interface (API) shape. The report comes back and the session
presents it at the gate.

Everything else runs in the session where the person can see it. The interview and the drafting at
stage 2 stay in the session, because both turn on answers only the person has.

## Files on disk

The loop writes into a `build/` folder next to the work:

```
build/
  00 intake.md              stage 0: every request, classified, with the person's ruling
  01 sequence.md            stage 1: the ordered backlog, and the status of every feature
  features/
    01-<slug>/
      intake.md             the ten spec questions, answered
      spec.md               the deliverable, gate green
```

`01 sequence.md` is the resume point. It carries the status of every feature, so a session that
ends mid-loop can be picked up by reading one file. Update it at the close of every stage, before
reporting the stage done.

The three statuses are `queued`, written at stage 1; `spec-green`, written when the linter's gate
goes green; and `done`, written when the person says yes at gate 2.

## The progress marker

Every gate carries one line saying how far the loop has come. It counts gates passed, which is a
fact about what has finished. It says nothing about how long the rest takes, because this loop does
not estimate.

**The scale.** Three stages, three gates, one gate per stage. Passing a gate advances the count by
one. `scripts/say.py gate <n>` in `calm-intake` prints the line, and it is the source of truth for the
string. The table below is the scale the script computes. Each figure is printed inside a fuller
sentence, and the last one appears only inside the gate 2 line, since there is no gate 3. Never
recompute a figure, and never retype the line by hand:

| Gates passed | Figure |
|---|---|
| 0 | `0 of 3 (0%)` |
| 1 | `1 of 3 (33%)` |
| 2 | `2 of 3 (67%)` |
| 3 | `3 of 3 (100%)` |

**Where it shows.** Every gate, and nowhere else, pasted from `say.py gate <n>`. The opening
does not carry it, because a greeting is the wrong place for `0 of 3 (0%)`, the one value on
the scale that tells the person nothing. A marker on every message would run through the
ten-question spec interview as noise.

**The word "gate" gets a gloss on first use**, at gate 0, where the marker also first appears,
because a person arriving here has no reason to know the word: a gate is a point where the loop
stops and waits for their answer.

**The second feature and after.** Gates 0 and 1 belong to the engagement and stay green once
passed. A feature that starts after the first opens at `2 of 3 (67%)` and runs to `3 of 3`.

**Going backwards.** A spec the person reopens after gate 2 went green returns to stage 2, and gate
2 goes unpassed with it. The marker drops, and the drop is always reported with its reason:

> `Gates passed: 2 of 3 (67%)`, down from `3 of 3`. Reopening the spec puts this feature back where
> it was. Rework here is the loop working correctly.

**What the marker cannot carry.** The scale runs one feature at a time, so a sequence of four
features reaches 100% four times. State the sequence position in words beside it at gate 2, for
instance "feature 2 of 4 specified, 2 queued". A new feature added at gate 2 lengthens the sequence
and leaves the marker alone.

## How to talk to the person

Assume the person has never read this file and never will. They came to solve their problem, and
everything here that is machinery stays backstage: stage numbers, gate numbers, skill names, rule
identifiers, scores, profiles, file paths, and the `<define ...>` marker. Three things are staged
on purpose, because each one orients the person: the opening, the progress marker, and the file
list at the close of an engagement.

**Say what it means for them.** A rule that fires gets reported as the thing it caught, out in the
world, in their words. A check that passes gets reported as the thing holding up. The identifier
that found it stays out of the sentence.

| Backstage | What the person hears |
|---|---|
| "AN-3 fails, the evidence is a prediction" | "This has not actually bitten you yet, so I am guessing at how often it matters" |
| "GATE PASS, 48 of 56, warnings SL-03.2 and SL-05.3" | "The spec holds up. Two things are still soft: what happens when the two sources disagree, and how you would measure success" |
| "SL-06.4 wants an eval rubric, likely a false positive on this profile" | "One check wants a scoring rubric. Those are for systems that guess, and yours is a yes or no lookup, so I am letting it go" |
| "D1 is still `<define primary data source>`" | "One thing is open on purpose: where the scores come from" |
| "Status moved to `done`, marker 3 of 3" | "This one is settled and written up. Three left in the queue" |

**The grading is available on request, never volunteered.** Offer it once, at the gate where it is
computed, in one line: *say "show me the grading" any time*. Print the verdict line, the per-case
table, and the rule identifiers when the person asks, and only then.

**Write in the second person.** The person reads every question and every option in it. "So you can
redeem the coupon" is right. Naming them in the third person describes them to somebody who is not
in the room. This holds inside the spec lines they will read back.

**Name a question by what it asks.** The headings in these briefs are internal labels. The person
sees the plain question: the cheap kill asks "tried anything yet?", the expiry asks "when does this
go stale?", the escape hatch asks "what happens when it cannot tell?", the tie-breaker asks "when
these two collide, which wins?".

**Housekeeping happens offstage.** Index files, line caps, naming conventions, style checks, and
this loop's own bookkeeping never interrupt a stage. Anything needing the person's decision waits
until the stage closes and gets one plain sentence there.

**Say what the spec is for, once, at gate 2.** The loop hands over a document rather than working
code, so the person is told plainly what to do with it: give it to whoever builds, or bring it back
here when it is time to build. Say it in one sentence, and only at the gate that produces it.

**Every stop says how to restart.** A declined gate, and the end of any session, closes with the
words that resume it: *say "continue the <thing>" and I will pick up at <the next question, in
plain words>*.

## Stopping the loop

The loop stops whenever the person wants it to. Two ways in, one way out.

**At a gate.** Every gate already asks a question, so declining is an exit. A gate answered with a
stop closes the loop rather than reopening the stage.

**Mid-stage.** "Stop", "pause", "exit", and "let us leave it there" end the loop wherever they
land, including halfway through a stage. Whichever skill holds the floor honours this. A skill that
hears a stop and treats it as feedback on the stage in progress has failed this rule.

**A stop is not always instant.** Stage 0 may have research out with a subagent, and a subagent in
flight cannot be interrupted. The stop takes effect at the next point the session has the floor.
Say so when it applies, and name what is still running, so a person who asked to stop and watched
the work carry on knows the loop heard them.

**Every stop writes the resume note first**, before a word goes to the person. Add or replace a
`Paused` block at the top of `build/01 sequence.md`:

```markdown
## Paused
Stopped: <date>, stage <n>, feature <slug, or "none yet">
Pending: <the answer that was being waited on, in plain words>
In flight: <what was half done, or "nothing">
```

The statuses `queued`, `spec-green` and `done` are written at the close of a stage, so none of them
can describe a stop in the middle of one. That is the gap this block fills. Clear the block once
the loop resumes past the point it records.

**Then say how to restart**, in the words that do it, per "Every stop says how to restart" above.

---

---

## Stage 0: intake

**Skill:** `calm-intake`. **Entry:** a person describes what they want.

1. Open by running `python3 scripts/say.py opening` from the `calm-intake` skill root and pasting
   its output, before anything else. Pass `--request "<their verbatim words>"` when the request arrived with the
   invocation. The script names the two passes the loop runs in, because a person arriving here
   has no use for a stage number, and it is a script because prose instructions to say something
   get skipped. Once per engagement, before anything is interpreted.
2. Capture the request verbatim before interpreting it. The original wording is evidence. A
   request that arrived with the invocation is reflected back, never asked for a second time.
3. Split it into discrete items. One sentence often carries three requests.
4. Classify each item as a **need** (a problem with evidence behind it), an **ask** (a request with
   no evidence yet), or a **mechanism** (a named solution standing in for an unstated problem).
5. For every mechanism, write the problem it appears to be solving, marked as an inference.
6. Present the classification through AskUserQuestion, one item at a time where the ruling is
   contested, batched where it is obvious. Lead with the classification you would defend and say
   why in the option description.

Never reclassify an item on the person's behalf. A ruling you disagree with gets one sentence of
argument, then it stands.

**Writes:** `build/00 intake.md`.

**GATE 0.** The person has ruled on every item. Nothing is left marked as an inference.
**Marker:** run `python3 scripts/say.py gate 0` from the `calm-intake` skill root and put
its line at the top of the gate question. Never retype it. The figures are `0 of 3 (0%)`
going in and `1 of 3 (33%)` once green.
**Red looks like:** an item still classified by the agent alone, or a mechanism whose underlying
problem was never confirmed.

---

## Stage 1: sequencing

**Skill:** `calm-intake`. **Entry:** gate 0 is green.

1. Take the confirmed needs. Asks and mechanisms that survived stage 0 as needs come along; the
   rest are recorded and dropped.
2. Order them easiest to hardest to build. Easiest means: fewest unknowns, fewest dependencies,
   smallest blast radius if it is wrong. Cost of building is a weaker signal than uncertainty.
3. State the dependency edges explicitly. An item that unblocks three others earns a place ahead of
   its difficulty rank, and that reordering is named out loud.
4. Present the order through AskUserQuestion. Offer the sequence you recommend first, then the one
   or two defensible alternatives, each with what it optimizes for.

**Writes:** `build/01 sequence.md`, with every feature at status `queued`.

**GATE 1.** The person has picked the feature to specify first.
**Marker:** run `python3 scripts/say.py gate 1` from the `calm-intake` skill root and put
its line at the top of the gate question. Never retype it. The figures are `1 of 3 (33%)`
going in and `2 of 3 (67%)` once green.
**Red looks like:** an agreed order with no first item named. Ordering is not selection.

---

## Stage 2: spec

**Skill:** `calm-spec`. **Entry:** gate 1 is green, and a feature is named.

Run the skill's own three phases against the chosen feature:

1. **Interview.** Ten questions, one at a time, through AskUserQuestion. Four answers block a draft:
   intent, result, tie-breaker, check. Missing any one, say which and stop.
2. **Draft.** Fill the template. Never invent a number: an unsupplied threshold is written as
   `<define threshold>` and listed at the end.
3. **Lint.** Run the linter over `build/features/<slug>/spec.md`. The command is
   `python3 scripts/spec_lint.py <spec>`, run from the `calm-spec` skill root, with the path to the
   spec written from there; `calm-spec/SKILL.md` gives the exact invocation and the profile flags.
   Fix what the gate reports, re-run, repeat until the gate is green. Add the judgment findings,
   each with its quoted line.

The linter's gate is computed by the script. Your reading produces advisories. Never promote an
advisory to a gate failure, and never suppress a rule to make a gate pass.

**Writes:** `build/features/<slug>/intake.md`, then `spec.md`. Status moves to `spec-green`, then
to `done` once gate 2 goes green.

**GATE 2.** Two conditions, both required. The script reports a green gate, and the person has said
yes to the spec as it stands. This is the closing gate of the loop, so it carries three things the
earlier gates do not:

- **Every unresolved `<define ...>` marker, read out.** The person decides whether one blocks.
- **What happens next, offered through AskUserQuestion.** Two routes: specify the next feature in
  the sequence, which is the one to lead with while the sequence still has items in it, or call the
  engagement finished. A person who wants a third thing says so, and that stands.
- **The file list, when the engagement is finished.** Every file the loop wrote, each named in
  plain words for what it holds: the record of the request as it arrived, the ordered list of
  features, and, for each feature, the answers behind its spec and the spec itself. Say in one
  sentence what the spec is for, per "Say what the spec is for" above.

**Marker:** run `python3 scripts/say.py gate 2` from the `calm-intake` skill root and put
its line at the top of the gate question. Never retype it. The figures are `2 of 3 (67%)`
going in and `3 of 3 (100%)` once green. Say the sequence position in words alongside it.
**Red looks like:** rolling into the next feature's interview because the sequence made it obvious.
The sequence is a plan, and the person still picks.

---

## Non-goals

- **This is not a project management tool.** It tracks one sequence in one file. Estimates, dates,
  and assignees live somewhere else.
- **It does not design or build.** Version 1 stops at a spec. Turning that spec into options, a
  prototype, and a feedback round is deferred work, and offering it here would promise something
  the loop cannot do.
- **It does not run without a person.** Every stage ends at a human answer. In a session that
  cannot take a reply, the loop stops at stage 0 and reports where it stopped.
- **It does not decide whether the work is worth doing.** Stage 0 sorts what was asked for. Whether
  the sequence deserves to be built is the person's judgment and is never the agent's.
- **It does not ship.** Publishing, pushing, and deploying sit outside this loop and need their own
  go-ahead.

## Known tensions

- **Hard gates cost time.** Three stops per feature is slow by design. The person who wants speed
  can ask for a stage to be skipped, and that request is recorded in the feature folder rather than
  quietly honoured as a new default.
- **Easiest-first ordering can specify the wrong thing first.** The cheap feature is not always the
  one that teaches the most. Stage 1 names this when it applies and lets the person override.
- **A green spec is not a built feature.** The linter grades the document. Whether the thing
  described can be built at a sensible cost is settled by building it, which happens outside this
  loop. Gate 2 says the spec is clear, and it says nothing else.
- **The sequence outlives the engagement.** A person can leave with four specs and build none of
  them. The loop has no way to tell, and it does not follow up.

## Escape hatch

The agent may stop the loop at any stage and say the loop is the wrong instrument: the request is
one line of work, the problem is not a build problem, or the spec cannot be written because the
person does not yet know what they want. Say so once, name what would be better, then do what the
person decides.
