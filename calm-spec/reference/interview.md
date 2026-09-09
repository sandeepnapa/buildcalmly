# The intake interview

Ten questions. Each one exists because a rule in the pack fails without its answer.

**Ask one at a time.** Where the AskUserQuestion tool exists, use it with two to four labeled
options, the recommended one first. Where it does not, ask in prose, still one at a time. Where the
session cannot take a reply, ask all ten in one pass, answer what the supplied material settles,
and list the gaps without inventing anything.

**Four answers block the draft: 1, 3, 5, 6.** Missing one of those, name it, say why it blocks, and
stop.

**The headings below are internal labels.** Each question carries a **Header** line holding the
words the person actually sees on the question chip, twelve characters at most. A question headed
"Cheap kill", "Expiry", or "Escape hatch" makes a person decode the tool before answering it. Every
question, option label, and option description is written in the second person, per "How to talk to
the person" in `../../workflow.md`.

---

## 1. Intent (blocking)

**Header:** `Purpose`

*In one sentence, what is this for, and who is it for?*

Rules served: SL-01.1, SL-09.5R. A spec with no single-sentence intent is a spec whose author has
not decided what it is.

Offer options when the person is circling: the narrowest reading, the widest reading, and the
reading you think they mean.

## 2. The cheap kill

**Header:** `Tried yet?`

*Have you tried anything already, even roughly, and what did it teach you?*

No rule fires on the answer. It is here because a spec written before anything was tried is the
most expensive document in the pack. Most ideas die in their first hour of life, cheaply, and the
mockup is what kills them. The spec is for the survivor.

Warn rather than block. Record the answer, including "nothing yet", in the intake.

## 3. Result (blocking)

**Header:** `Done means`

*What does done look like, stated so a stranger would grade it the same way you would?*

Rules served: SL-06.1, SL-06.4, SL-06.7R. Push until the answer contains a number, a comparison, or
a named check. "Users are happy" fails. "At least 98 percent exact match on the 100-record gold
set" passes.

Ask the follow-up that does the work: *who grades this, and what do they look at?*

## 4. Limits

**Header:** `Never do`

*What must this never do on its way there?*

Rules served: SL-03.1, SL-03.2. Collect at least three. These become the Non-Goals section, and
they are a sharper statement of strategy than the goals are.

## 5. Tie-breaker (blocking)

**Header:** `Which wins`

*When two of these collide, which one wins? Here is the collision most likely to actually happen:
<the real one, in a sentence>.*

Rules served: SL-02.2, SL-02.3. This is the question people most want to skip. Skipping it hands
the collision to whoever builds the thing, where the goal that is easier to score wins by default.

Offer the two or three real collisions you can already see in their answers, and ask them to rank.

## 6. Check (blocking)

**Header:** `Who checks`

*Who checks this from outside, using something the thing being checked does not control? A check
graded by the same source it is checking would be marking its own homework.*

Rules served: SL-01.2, SL-01.2R. A check the builder authors and grades approves its own work.
Press on any answer that amounts to review, sign-off, or approval. The homework line is the gloss
that works on a first hearing, so keep it.

## 7. Trust and action (agent profile)

**Header:** `Risk limits`

*Which inputs do you not trust, which actions cannot be taken back, and what is the budget?*

Rules served: SL-07.1, SL-07.2, SL-08.1, SL-08.2. Skip for a product spec. For anything an agent
executes, all four parts are needed: the trust boundary, the grounding policy, the reversibility
split, and the resource cap.

## 8. Tradeoffs

**Header:** `Rejected`

*What did you rule out, and what did you give up by ruling it out?*

Rules served: SL-09.4. Almost nobody writes this down. A spec with no stated tradeoff has either
made no choice or is hiding one.

## 9. Expiry

**Header:** `Goes stale`

*What would make this out of date, and when should someone read it again?*

Rules served: SL-06.3, SL-06.6. A date, a cadence, or an event. For anything model-facing, the
model and the date it was validated against belong here too.

## 10. Document type

**Header:** `Doc type`

*Is this a product spec, an agent instruction, or an eval definition?*

Sets the profile, which decides which rules gate. Infer it from the other nine answers and confirm
rather than asking cold.

---

## Writing the intake

Write `intake.md` next to where the spec will live:

```markdown
# Intake: <spec name>

Recorded <date>. Profile: <product | agent | eval>.

## 1. Intent
## 2. Cheap kill
## 3. Result
## 4. Limits
## 5. Tie-breaker
## 6. Check
## 7. Trust and action
## 8. Tradeoffs
## 9. Expiry

## Gaps
<anything unanswered, named plainly>
```

An unanswered non-blocking question is recorded as a gap. It is never filled with a guess.

## Questions raised at the gate

The draft raises its own questions: a `<define ...>` to resolve, an ambiguity the reading found, an
escape hatch with no behaviour behind it. Those get the same treatment. Plain headers, twelve
characters at most, and the option text says what happens in the world.

| Instead of | Use |
|---|---|
| `Escape hatch` | `When unsure` |
| `Home game def.` | `Which days` |
| `D1 data source` | `Score source` |
| `SL-06.4` | do not raise it as a question at all; report the call and the reason |
