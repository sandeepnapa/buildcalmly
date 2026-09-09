# calm-spec

An Agent Skill that interviews you for the inputs a spec needs, drafts the spec from those inputs,
and grades any spec against 39 rules covering the ways specs lie.

One test decides everything here: **a checker outside the loop can pass or fail this spec without
asking the author a question.** Every rule is a way that test fails.

```
calm-spec 0.1.4   rules 0.2.0   profile: agent   1,240 words   triage-agent.md

GATE:  FAIL   2 hard gate(s) red
SCORE: 38/70 (derived from the rule registry, form layer only)

RED  SL-03.1  An explicit Non-Goals section with at least three entries
             no Non-Goals section
       fix: Name three things this explicitly will not do in this version.

RED  SL-01.2  Every constraint carries a falsifiable check   (4 findings)
        L23  hard rule with no check behind it
             "The agent MUST NOT leak user data."
       fix: State the test, assertion, lint rule, query, or gate that fails when the rule is
            violated. No check means it is an aspiration.
```

Three version numbers move independently, and the banner prints two of them:

- **skill 0.7.0**, the Agent Skill itself, in `SKILL.md`
- **script 0.1.4**, the linter `scripts/spec_lint.py`, printed in the banner beside the name
- **rule pack 0.2.0**, the registry `rules/rules.json`, printed in the banner as `rules`

## How it works

Rules split by one question: can a program compute this from the text alone?

- **Form**, 30 rules, decided by a bundled Python script. Same input, same verdict, every run.
- **Judgment**, 9 rules, decided by a reader. Whether a check is real or theatrical. Whether two
  readers would build different things. Whether the acceptance measures the goal or a cheaper proxy.
  Whether the spec shows the target with examples, or only forbids things, and whether it says what
  happens when the system is unsure.

Every rule carries a before-and-after pair, one on a product spec line and one on an agent prompt
line, and one sentence naming the call the tool leaves to the person.

**The binary gate is computed only from the form layer.** A model cannot fail your spec on an
impression, and anyone can reproduce the verdict by running the script. The judgment layer carries
advisories and fixes, and a person decides whether one of them blocks.

The tool enforces the form. You supply the judgment: the actual threshold, the actual non-goal,
whose interest wins, what done means. That gap is the job.

## Three phases

| Phase | What it does |
|---|---|
| `interview` | Ten questions, one at a time. Four of them block the draft. Writes `intake.md` |
| `draft` | Turns a complete intake into a spec, then lints its own output until the gate is green |
| `lint` | Grades any Markdown spec: gate, per-case scores, and a fix for every finding |

## Profiles

| Profile | For | What it adds |
|---|---|---|
| `product` | Product requirements document, feature spec | Cases 00 to 06 and 09, with case 00 advisory. Trust boundary, action safety, and the model-assumption rule SL-06.6 are off |
| `agent` | System prompt, agent instruction file | Trust boundary and action safety become hard gates |
| `eval` | Eval definition, scoring rubric | The rubric must be gradeable by a judge who did not build the thing |

The profile is inferred when you do not name one.

## Install

Skills do not sync between surfaces, so install it where you want it.

**Claude Code.** Clone the repository, then link this folder in:
`ln -s "$PWD/calm-spec" ~/.claude/skills/calm-spec` for personal use, or the same link under
`.claude/skills/` inside one project. The repository root `README.md` installs all three skills
together. Keep `calm-spec/` inside the repository: `SKILL.md` reads `../workflow.md` and runs
`../calm-intake/scripts/say.py`, which exist only beside it.

Then `/calm-spec`, or just ask for a spec to be linted.

**claude.ai.** Zip the repository root rather than this folder alone, so `workflow.md` and
`calm-intake/` travel with it, and upload it under Settings, Features, Skills. Needs code execution
enabled on a Pro, Max, Team, or Enterprise plan.

**The Skills application programming interface (API).** Upload through the `/v1/skills` endpoints and reference the returned skill id in the
`container` parameter alongside the code execution tool.

**Command line, no Claude involved.** The form layer is a standalone linter:

```bash
python3 scripts/spec_lint.py my-spec.md --profile agent
python3 scripts/spec_lint.py my-spec.md --json
python3 scripts/spec_lint.py --list-rules
```

Exit code 1 when a hard gate is red, so it drops into continuous integration unchanged. Python 3.9
or newer (developed on 3.11), standard library only, no network calls, nothing to install.

## Rewriting an existing spec

The lint phase reports findings and leaves your document alone. When you want the edit made, ask
for the rewrite: the session doing the linting reads `reference/rewrite.md` and restructures the
document itself, into Goals, Non-Goals, Constraints with their checks, Defaults with what
overrides them, Aspirations with a metric or an honest "this is taste", Precedence, and an audit
of every line it reclassified. It then lints its own output until the gate is green. No package
install, no API key: the rewrite runs wherever the skill runs. Whole-document context is what
earns the rewrite its keep: it finds a real constraint buried in a list of nice-to-haves, and it
finds a document so over-constrained that nothing is left to optimize.

It never invents a number. A threshold the source does not supply comes back as
`<define threshold>`, flagged in the notes at the end.

Origin: the rewrite brief predates the rule pack and implements Case 01 alone, the Constraint,
Default, Aspiration split that the rest of the pack grew out of. It started as the article series
"the curious case of the lying spec" and originally shipped as an API-calling script; it became an
in-session brief in 0.2.0.

## Suppression

```
<!-- calm-spec: ignore SL-04.1 -->        # the next non-blank line only
<!-- calm-spec: ignore-file SL-03.3 -->   # the whole file
<!-- calm-spec: profile agent -->         # declare the profile in the document
```

## Does the linter work?

`corpus/` holds 39 labeled fixtures: three clean specs that must pass, 33 copies of those specs
with a small named defect planted in each, and three copies carrying a healthy pattern the
rules once misread, which must still pass clean. The two folder names record provenance rather
than verdict: `bad/` means mutated from a clean base, and two of those mutations are healthy
rewrites that must fire nothing, while `good/` holds the clean bases and their variants.
`labels.json` records which rules should fire in each fixture. `run_corpus.py` measures what
actually fires. Derived from the labels: 37 planted defects across the 33 defect fixtures, because
four of them plant a coupled pair (stripping every refusal word from a spec also strips its escape
hatch, so the label records both).

```bash
python3 corpus/run_corpus.py
```

Current result, rule pack 0.2.0: **all 30 form rules at 100 percent precision and 100 percent
recall across 37 planted defects.**

Read that number with its limits, which are large:

- The corpus is small, and it was written by the same person who wrote the rules. It proves the
  rules fire on the defects they were built to catch, in documents shaped like the three bases.
- It is not a claim about specs in the wild. Real documents are messier, and the word-level rules
  in case 04 will produce false positives on prose the author had good reason to write.
- Building the corpus found and fixed five real defects in the rules. Four were keyword lists loose
  enough to match ordinary English: "page" matched the words "status page", "human review" matched
  "a human reviewer", "halt" matched a budget counter halting, and "above" matched "at or above".
  That is what the corpus is for.
- Manual testing on a real-world spec found and fixed four more, now pinned by fixtures:
  the escape-hatch word list missed real hatches phrased outside it, the one-requirement rule
  missed a multi-demand constraint written in indicative mood across wrapped lines, the check
  rule credited "Check: none yet" as a check while also crediting a constraint with its
  neighbor's check through the lookahead window, and the aspiration rule read only the first
  physical line of a wrapped item, missing the metric on the line below.
- A higher number on a corpus you wrote yourself is a weaker claim than a lower number on one you
  did not. Independent fixtures are the obvious next contribution.

Pointing the linter at a document that is not a spec, such as a design note or a rubric, produces a
FAIL that correctly means "this is not a spec" and tells you nothing useful.

## How to game this linter

Structure without substance passes every form rule. Add the headings, put the word "Check:" beside
each constraint, name three non-goals, and the gate goes green on a document that specifies nothing.
That is Goodhart's law pointed at the tool, and `reference/principles.md` covers what limits the
damage and what does not.

The gate is a floor. It says the document has the parts. It says nothing about whether the parts are
any good.

## Layout

```
SKILL.md                 the skill: three phases, under 5k tokens
rules/rules.json         the registry both layers read
rules/RULES.md           all 39 rules, generated from the registry
reference/interview.md   the ten intake questions
reference/spec-template.md   the shape the draft phase fills
reference/rewrite.md     the brief for rewriting an existing spec into Constraint, Default, Aspiration (C/D/A) form
reference/principles.md  where the rules come from, and how to game them
scripts/spec_lint.py     the form layer and the command line tool
scripts/gen_rules_md.py  regenerates RULES.md from the registry
corpus/                  labeled fixtures and the measurement
```

Editing a rule means editing `rules/rules.json`, then running `scripts/gen_rules_md.py` and
`corpus/run_corpus.py`. The registry is the single source; the script and the documentation both
read it.

## Sources

The rules are not new. Their lineage is in `reference/principles.md`: Popper on falsifiability,
IEEE 830 and RFC 2119 and EARS (Easy Approach to Requirements Syntax) on requirements language, Gilb's Planguage on quantifying a vague
word, Goodhart and Campbell on proxy gaming, the OpenAI Model Spec on objectives and rules and
defaults, constitutional approaches to model behavior for where rules cannot enumerate, and the
Kubernetes Enhancement Proposal template on goals, non-goals, and graduation criteria.

## License

MIT.

## Renamed

This skill was called `spec-lint` through version 0.2.0. It became `calm-spec` when it joined the
build calmly loop as its spec stage, alongside `calm-intake`. The
rule identifiers, the `SL-` prefix, the script name, and the rule pack version are unchanged, and
the suppression prefix `spec-lint:` is still parsed.
