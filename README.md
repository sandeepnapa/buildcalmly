# buildcalmly

Three Agent Skills and the loop that runs them, taking a request from a sentence to a spec a
builder can work from, with a human answer at every stage. One skill is the way in; two own the
stages.

Each skill resolves everything it needs from inside this folder, so the folder installs as a unit.

These are Agent Skills for Claude Code: folders of instructions a model loads on demand. Link
them under `~/.claude/skills/` and invoke `buildcalmly` in a session.

## What is here

| Path | What it is |
|---|---|
| `workflow.md` | The loop: three stages, three hard gates, the progress marker, how to talk to the person, how it stops, the file layout, the non-goals |
| `SKILL.md` | `buildcalmly`, the entry point: finds the resume point, names the next stage, invokes the skill that owns it. Version 0.3.0 |
| `calm-intake/` | Stages 0 and 1: needs against asks, then sequencing. Shipping, version 0.8.0. Its `scripts/say.py` prints the opening and the progress marker, which every gate pastes verbatim |
| `calm-spec/` | Stage 2: the spec and the linter that grades it. Shipping, skill version 0.7.0; the linter prints its own tool and rule-pack versions on every run. Its `rules/RULES.md` is the standard: 39 rules across ten cases, each with its sources, a before-and-after pair, and the judgment it leaves to the person |

## The loop in one pass

```
request  ->  buildcalmly            resume point, or a fresh start
             calm-intake   stage 0  classify needs, asks, mechanisms      GATE 0
             calm-intake   stage 1  order easiest to hardest, pick one    GATE 1
             calm-spec     stage 2  interview, draft, lint until green    GATE 2
                                    then the next feature, or the end
```

Stages 0 and 1 run once. Stage 2 runs once per feature, until the sequence is empty or the person
calls the engagement finished. What they leave with is the record of the request, the ordered list
of features, and a graded spec for each feature that was specified.

The person can stop at any gate, and at any moment inside a stage, by saying so. Every stop writes
a `Paused` block into the sequence file naming the stage, the answer that was being waited on, and
anything left half done, so the next session picks up from one file. `workflow.md` holds the
contract, under "Stopping the loop".

## Where it stops

The loop ends at a spec. Turning that spec into design options, a prototype, and a feedback round
is deferred to a later version, and no skill here offers it. Gate 2 says in one sentence what the
spec is for: hand it to whoever builds, or bring it back when it is time to build.

## Install

Install `buildcalmly` and the two stage skills it routes to. `calm-spec` is also useful
standalone, on a spec that arrived with no loop around it.

```bash
git clone https://github.com/sandeepnapa/buildcalmly.git
cd buildcalmly
mkdir -p ~/.claude/skills
ln -s "$PWD"             ~/.claude/skills/buildcalmly
ln -s "$PWD/calm-spec"   ~/.claude/skills/calm-spec
ln -s "$PWD/calm-intake" ~/.claude/skills/calm-intake
```

The first link points at this folder itself, because `buildcalmly` keeps its `SKILL.md` beside
`workflow.md` rather than in a subfolder of its own.

Both stage skills need Python 3.10 or newer. `calm-spec` runs its linter on the standard library
alone and makes no network calls. `calm-intake` runs `scripts/say.py` on the same terms.

## The voice

One section of `workflow.md`, "How to talk to the person", governs everything all three skills say
out loud. The machinery stays backstage: stage numbers, gate numbers, skill names, rule
identifiers, scores, profiles, file paths. A rule that fires is reported as the thing it caught out
in the world. The full grading is printed on request, in the words *show me the grading*, and it is
never volunteered.

## Status

`calm-spec` is complete and measured against a labeled corpus. `calm-intake` is complete: four
reference briefs, exercised end to end. The voice section in `workflow.md` exists because a loop
that works can still report like a compliance log. `buildcalmly` is thin by
design: it routes and it stops, and every gate stays with the skill that owns the stage.
