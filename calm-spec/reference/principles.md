# Principles: where these rules come from

A spec lies when it says one thing and means another. This pack collects the ways that happens,
each as a rule with a check behind it. The lineage matters, because none of this is new. What is
new is that the reader is now often a machine, which raises the cost of every ambiguity that used
to get resolved in a meeting.

## The one test

**A checker outside the loop can pass or fail this spec without asking the author a question.**

Every rule is a way that test fails. It is a restatement of falsifiability applied to a working
document. The philosophy of science version is Popper's: a good theory forbids things, and the more
it forbids the better it is. Irrefutability is a vice, and people routinely mistake it for a
virtue. A requirement nothing can fail is the same object. It feels safe, because nobody can accuse
you of missing it, and it carries no information.

The requirements-engineering tradition reached the same place from the other direction. IEEE 830
listed the bad words decades ago. Gilb's Planguage answered the question the criticism raises, which
is what you write instead of the vague word: name the scale, the meter, the target, and the
constraint. RFC 2119 gave the keywords their weight, and EARS (Easy Approach to Requirements Syntax) gave
the sentence a fixed shape so two readers parse it the same way.

## Two layers, and why the gate is deterministic

Rules split by one question: can a program compute this from the text alone?

The **form** layer is thirty rules a script decides. Section presence, a check next to every hard
rule, weasel words, scope-creep verbs, a stated precedence, acceptance criteria, an expiry, a
tradeoff, length, ordering. Same input, same verdict, every run.

The **judgment** layer is nine rules a reader decides. Whether a check is real or theatrical.
Whether two readers would build different things. Whether a rule should have been a principle.
Whether the acceptance measures the goal or a cheaper proxy. Whether the spec shows its target or
only forbids things, and whether it says what to do when unsure.

Every rule also carries a before-and-after pair, one on a product spec line and one on an agent
prompt line, and one sentence naming the call the tool leaves to the person. The pair shows the
fix; the sentence marks where the form ends and the judgment begins.

The binary gate is computed only from the form layer. A model reading your spec cannot fail it on
an impression, and the verdict is reproducible by anyone who runs the same script. The judgment
layer carries advisories and fixes, and a person decides whether any of them blocks.

This split is the whole design. The tool enforces the form. The person supplies the judgment: the
actual threshold, the actual non-goal, whose interest wins, what done means. That gap is the job,
and a tool that pretended to close it would be lying in the same way the specs do.

## The ten cases

**00. The spec the model misreads.** Three habits that cut across every other case, grounded in
how a model reads. A model completes patterns and represents negation weakly, so a wall of "never
X" raises the odds of X; the positive target, shown by example, steers. A few sharp examples move a
model more than paragraphs of prose, so the examples are spec content and the edge cases chosen
reveal what the author cares about. And a model is confidently wrong in a way a deterministic
system is not, so the spec has to say what happens when the system is unsure and when the input is
missing or ambiguous. All three are judgment rules: a script can count prohibitions, and it cannot
tell whether the positive statement that should replace them is any good.

**01. The wish in a rule's clothing.** Every load-bearing line is a constraint, a default, or an
aspiration, and each carries what its type requires. The three-tier split follows the OpenAI Model
Spec's objectives, rules, and defaults. The demand that every constraint carry a check comes from
requirements engineering and from the Kubernetes Enhancement Proposal test plan. No check, no
constraint.

**02. The rule that contradicts itself.** Precedence, authority tiers, and named tensions. The
chain of command idea is the Model Spec's. The insistence on writing the tension down rather than
letting both stakeholders believe they won is ordinary product honesty, and it is the rule most
often skipped.

**03. The spec with no walls.** Non-goals, refusals, and the scope-creep vocabulary. Goals and
Non-Goals is the KEP move, and it is the section most specs omit. A document that only says what to
build has an unbounded blast radius, because whoever builds it fills the gaps with guesses.

**04. The word that means nothing.** Weasel words, one demand per line, no bare referents. IEEE 830
and EARS. This is the case where a linter is most obviously right and most likely to annoy, which is
why the whole case is advisory rather than gating.

**05. When the rule should have been a principle.** Some domains cannot be enumerated, and a longer
rulebook always misses one. The answer is a principle, worked examples, and an escalation path. The
lineage is constitutional approaches to model behavior, where rules that cannot enumerate are
replaced by principles that generalize. The escape hatch belongs here too: a system authorized to
say it does not know is the only kind whose confident answers mean anything.

**06. The spec that never defined done.** Acceptance criteria, a post-launch trigger, an expiry,
an eval contract, a statistical tolerance, and recorded model assumptions. Graduation criteria are
the KEP's. The tolerance rule exists because you cannot promise "always" from a probabilistic
system: the honest contract is a rate on a named dataset. The expiry rule exists because stale
context is worse than none, since it is trusted.

**07. The spec that trusts the wrong things.** There is no privilege gap between your instructions
and the page the model just fetched. The spec has to say which inputs are instructions and which
are data, and what happens when the data contains something shaped like an instruction.

**08. The spec that cannot act safely.** A single boolean MUST is the wrong shape for a destructive
action. Sort by reversibility, gate the irreversible ones, make writes idempotent, and bound the
resources. Work until the task is done is an unbounded authorization.

**09. The spec the machine cannot use.** Versioned and retiring what it replaces, short enough to
hold, constraints early, and honest about what it traded away. These come from operating practice
in shops where agents build from the written artifact. Shortness is a correctness property there
rather than a courtesy: more context dilutes attention, and models lose the middle.

## How to game this linter

Structure without substance passes every form rule. Add the headings, put the word "Check:" beside
each constraint, name three non-goals, state a precedence, and the gate goes green on a document
that specifies nothing.

This is Goodhart's law pointed at the tool. A measure that becomes a target stops measuring what it
measured, and the cheapest way to move this particular number is to add scaffolding rather than
decisions.

Three things limit the damage, and none of them eliminates it:

1. The gate is a floor rather than a certificate. Passing means the document has the parts, and it
   says nothing about whether the parts are any good.
2. The judgment layer exists precisely for the gap. `SL-01.2R` asks whether each check is real.
   `SL-06.7R` asks what the cheapest way to move each acceptance number would be. Those questions
   are unanswerable by pattern matching, which is why they are labeled as needing a reader.
3. The score is reported per case, so scaffolding shows up as a flat profile across the scored
   cases, nine on the agent profile and seven on product, where a real spec is usually uneven.

Saying this out loud in the documentation is the honest move, and it is also the strongest argument
for why the judgment layer is in the design at all.

## What this tool cannot do

It cannot tell you whether the spec was worth writing. A document can satisfy every rule here and
still specify the wrong thing, and nothing in the pipeline catches that. The build passes
verification and the product is still wrong, because the spec was wrong.

That residual has a name, which is taste, and it belongs to a person. This tool exists to clear
everything below it, so the person's attention lands there instead of on a missing non-goals
section.
