# Worked example: one messy request through stages 0 and 1

A single paragraph from a head of customer success, taken to a named first feature. The company
and the people are invented. Dates are kept because the tests need them.

## The request, verbatim

Received 2026-09-02, from the head of customer success, in a chat message:

> "We need a Slack integration so the team knows when a customer replies, the reports page needs a
> bulk CSV export because finance keeps asking, and we have to have SSO before the Acme renewal in
> October. Also can we make search faster."

## Stage 0

**Q0.1, the split.** Four verbs, four items. The person confirmed the split.

1. A Slack integration so the team knows when a customer replies.
2. A bulk comma-separated values (CSV) export on the reports page, for finance.
3. Single sign-on (SSO) before the Acme renewal in October.
4. Make search faster.

**Item 1.** Names a destination, so the agent proposed `mechanism` and inferred the problem: a
response-time commitment being missed. Through Q0.3 the person confirmed it, and the ladder
supplied the evidence: on 2026-08-26 a customer replied during a team meeting, nobody saw it for
ninety minutes, and the customer escalated against a one-hour response the contract promises. The
workaround is refreshing the queue between meetings. Cost of leaving it: one escalation a month,
and a service credit paid once in July.

Need statement: *When a customer replies to an open ticket while I am in a meeting, I want to know
before they escalate, so I can answer inside the one-hour response we sold them.* Three mechanisms:
a chat notification, a text message, a shared queue with an owner on rotation. Build nothing: an
auto-reply that promises a time and buys the hour.

Tests: AN-1 through AN-5 pass. AN-6: one source. AN-8: concrete.
Verdict: need found. **Ruling: need**, by the person, 2026-09-02.

**Item 2.** "Because finance keeps asking" is a relay, so AN-7 fails until the person who feels the
pain is named. Through Q0.6 the person named the finance analyst who builds the quarterly board
pack. The person could answer the ladder second-hand: at the June close the analyst read figures off
the screen and retyped them, about four hours. The agent proposed `mechanism` with the inferred
problem "figures reach the board pack by retyping", and the person confirmed it.

Need statement: *When the board pack is due at quarter close, I want last quarter's figures inside
the spreadsheet the deck is built from, so the deck is finished without retyping anything.*
Mechanisms: scheduled delivery into the existing file, a live connector, an application
programming interface (API) the analyst calls. Build nothing: the report produces the slide.

Tests: AN-1 through AN-5 pass, AN-7 filled. AN-6: one source here, though `reframing-bank.md`
shows the same need arriving from other accounts. AN-8: four hours a quarter.
Verdict: need found. **Ruling: need**, by the person, 2026-09-02.

**Item 3.** Names a protocol, so `mechanism`. Through Q0.3 the person chose "the mechanism is the
requirement", and through Q0.4 the exemption: contractual. The Acme renewal's security
questionnaire requires SSO for any vendor holding customer data, and the renewal date is
2026-10-15. The agent recorded the inferred need underneath, offboarding without visiting each
tool, because it decides later whether provisioning or deprovisioning ships first.

Tests: skipped under the exemption, recorded as skipped.
Verdict: ask is the requirement (contractual). **Ruling: mechanism, exempt**, by the person,
2026-09-02.

**Item 4.** No occurrence, no cost, no workaround. The agent proposed `ask` and cited AN-3 and
AN-4. Through Q0.5 the person chose "park it and investigate", naming the support lead as the
person to interview.

Verdict: ask only. **Ruling: ask**, by the person, 2026-09-02. Recorded and dropped at stage 1.

**Q0.7.** Two needs, one exempt mechanism, one ask parked. The person said proceed. `build/00
intake.md` written. **Gate 0 green.**

## Stage 1

Three items travel: items 1, 2 and 3. Item 4 is recorded in the same file with its ruling and the
name of who to interview.

**Difficulty, easiest first.**

1. **Reply notification** (item 1). One event, one channel, small blast radius when wrong. Fewest
   unknowns.
2. **Figures into the spreadsheet** (item 2). The mechanism is open, three real options, and the
   analyst's file format is unknown until someone looks.
3. **SSO** (item 3). Depends on Acme's identity provider, touches login for every user, and a
   mistake locks people out. Most unknowns, largest blast radius.

**Dependency edges.** None. No item unblocks another, so Q1.2 was skipped.

**Q1.3, the deadline.** SSO carries 2026-10-15 and sits third. The agent asked which wins. The
person moved it first: the renewal is the largest account and the loop cannot say whether the order
reaches the date. Recorded as the person's override of difficulty for a date.

**Q1.1, the order.** With the override applied, the recommended order became SSO, reply
notification, figures. The alternative offered, reply notification first for a fast win before the
hard one, was declined.

**Q1.4, the first feature.** The person named SSO. `build/01 sequence.md` written, every feature at
`queued`. **Gate 1 green.**

## The files, abridged

```markdown
# 00 intake.md

Request received 2026-09-02 from the head of customer success. Split into 4 items, confirmed.

### Item 1: reply notification
- Quoted: "We need a Slack integration so the team knows when a customer replies" (head of customer success, 2026-09-02)
- Need statement: When a customer replies to an open ticket while I am in a meeting, I want to know before they escalate, so I can answer inside the one-hour response we sold them.
- Mechanisms: chat notification; text message; shared queue on rotation; build nothing (auto-reply that buys the hour)
- Evidence: 2026-08-26, reply unseen for ninety minutes during a meeting, customer escalated
- Workaround: refreshing the queue between meetings
- Convergence: 1 source
- Cost of leaving it: one escalation a month; one service credit paid in July
- Tests: AN-1 to AN-5 pass, AN-6 one source, AN-7 user, AN-8 concrete
- Verdict: need found
- Proposed class: need
- Ruling: need, head of customer success, 2026-09-02

### Item 3: SSO
- Quoted: "we have to have SSO before the Acme renewal in October" (head of customer success, 2026-09-02)
- Need statement (recorded, not tested): When someone leaves the team, I want their access gone without visiting each tool, so I can answer the security questionnaire truthfully.
- Tests: skipped under exemption
- Verdict: ask is the requirement (contractual: Acme renewal questionnaire, due 2026-10-15)
- Proposed class: mechanism, exempt
- Ruling: mechanism, exempt, head of customer success, 2026-09-02

### Item 4: faster search
- Quoted: "Also can we make search faster" (head of customer success, 2026-09-02)
- Tests: AN-3 fail (no occurrence), AN-4 fail (no workaround named)
- Verdict: ask only
- Ruling: ask, parked, interview the support lead. Dropped at stage 1.
```

```markdown
# 01 sequence.md

| # | Feature | Status | Why here |
|---|---|---|---|
| 1 | SSO | queued | Person's override: contractual date 2026-10-15 outranks difficulty |
| 2 | Reply notification | queued | Fewest unknowns, smallest blast radius |
| 3 | Figures into the spreadsheet | queued | Mechanism open, file format unknown |

Dropped at stage 0: faster search (ask, parked, interview the support lead).
Dependency edges: none.
First feature: SSO, named by the head of customer success, 2026-09-02.
```

## Handing off

"Starting on single sign-on. Next is ten questions on what it has to do and how you would know it
worked." Nothing about the spec is drafted here.
