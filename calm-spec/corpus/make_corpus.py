#!/usr/bin/env python3
"""
make_corpus.py - generate the labeled corpus from the three clean base specs.

Each bad fixture is one clean base with a small, named defect planted in it, so a finding
can be attributed to that defect rather than to the rest of the document. labels.json
records, per fixture, exactly which rules should fire. run_corpus.py measures the linter
against those labels.

    python3 make_corpus.py

Rewrites bad/*.md, the good/ variant fixtures, and labels.json. Deterministic: no
randomness, no clock.
"""

import json
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
GOOD = HERE / "good"
BAD = HERE / "bad"

BASES = {
    "product": (GOOD / "product-clean.md").read_text(encoding="utf-8"),
    "agent": (GOOD / "agent-clean.md").read_text(encoding="utf-8"),
    "eval": (GOOD / "eval-clean.md").read_text(encoding="utf-8"),
}


def drop_section(text: str, title: str) -> str:
    """Remove a '## Title' heading and everything under it, up to the next '## '."""
    pat = re.compile(rf"^##\s+{re.escape(title)}\s*$.*?(?=^##\s|\Z)", re.M | re.S)
    out, n = pat.subn("", text)
    assert n == 1, f"drop_section found {n} matches for {title!r}"
    return out


def sub1(text: str, old: str, new: str) -> str:
    assert old in text, f"sub1 missed: {old[:60]!r}"
    return text.replace(old, new, 1)


FILLER_TOPICS = [
    "the history of the payment integration and the three processors it has outgrown",
    "how the reconciliation team currently closes the books each morning",
    "the customer support volume that arrives after a failed authorization",
    "the earlier attempt at a retry queue and why it was switched off",
    "what the fraud team asked for during the last review cycle",
    "the shape of the ledger table and the columns nobody reads any more",
    "the seasonal traffic pattern and the two weekends that break every assumption",
]


def filler(paragraphs: int) -> str:
    out = []
    for i in range(paragraphs):
        topic = FILLER_TOPICS[i % len(FILLER_TOPICS)]
        out.append(
            f"### Background note {i + 1}\n\n"
            f"This section records {topic}. It exists because the decision below was argued over "
            f"several weeks and the reasoning was worth keeping somewhere a reader can find it. "
            f"None of it binds the build. The team walked through the alternatives, wrote down "
            f"what each one would cost to operate, and compared the operating cost against the "
            f"recovery it would buy back. The numbers moved around as the sample grew, so the "
            f"early estimates in this note are superseded by the measurements recorded later. "
            f"Anyone picking this up cold should read the constraint list first and treat this "
            f"section as context rather than instruction. The people involved are listed in the "
            f"project channel, and the raw figures live in the analysis notebook alongside the "
            f"queries that produced them. What follows repeats some of that reasoning at length "
            f"so the record is complete rather than compressed, which is the point of a "
            f"background note and also the reason it does not belong in the spec proper."
        )
    return "\n\n".join(out)


MUTATIONS = []


def mutation(name, base, profile, expect):
    def deco(fn):
        MUTATIONS.append({"name": name, "base": base, "profile": profile,
                          "expect": expect, "fn": fn})
        return fn
    return deco


VARIANTS = []


def variant(name, base, profile):
    """A good fixture: a clean base plus content that must stay silent. Where a mutation plants
    a defect and names the rule it must trip, a variant plants a shape the linter has misread
    before and names nothing, because nothing may fire."""
    def deco(fn):
        VARIANTS.append({"name": name, "base": base, "profile": profile, "fn": fn})
        return fn
    return deco


# ---- Case 01 -------------------------------------------------------------------------

@mutation("untyped-requirement", "product", "product", ["SL-01.1"])
def _m(t):
    return sub1(t, "Recover payment authorizations that fail for transient reasons, without charging a shopper twice.",
                "Recover payment authorizations that fail for transient reasons, without charging a shopper twice.\n"
                "The service MUST reconcile the ledger nightly. *Check: the nightly job exit status gates the release.*")


@mutation("rules-without-checks", "product", "product", ["SL-01.2"])
def _m(t):
    return re.sub(r"\s*\*Check:[^*]*\*", "", t)


@mutation("check-placeholder", "product", "product", ["SL-01.2"])
def _m(t):
    return sub1(t, "*Check: assertion on the emitted schedule in the\n  driver test suite.*",
                "*Check: none yet.*")


@mutation("aspiration-without-metric", "product", "product", ["SL-01.3"])
def _m(t):
    return sub1(t, "- A1. Reduce the share of abandoned checkouts caused by transient failure. Metric: abandonment\n  rate on authorization error, direction down.",
                "- A1. Make recovery from transient failure feel better for the shopper.")


@mutation("default-without-override", "product", "product", ["SL-01.4"])
def _m(t):
    return sub1(t, "- D1. Backoff doubles between attempts. A merchant configuration flag overrides the schedule.",
                "- D1. Backoff doubles between attempts.")


# A healthy aspiration whose metric lands on the wrapped second line. The 0.1.0 rule read
# only the first physical line and called it metric-less. Expects nothing to fire.
@mutation("wrapped-aspiration", "product", "product", [])
def _m(t):
    return sub1(t, "- A1. Reduce the share of abandoned checkouts caused by transient failure. Metric: abandonment\n  rate on authorization error, direction down.",
                "- A1. Make recovery from a transient failure invisible to the shopper. Metric: abandonment\n  rate on authorization error, direction down.")


# ---- Case 02 -------------------------------------------------------------------------

@mutation("authority-without-tiers", "product", "product", ["SL-02.1", "SL-02.2"])
def _m(t):
    t = sub1(t, "- C6. Retry state is written before the outbound call.",
             "- C6. Retry records MUST be kept seven years under the legal retention policy.\n"
             "  *Check: the retention job test asserts the window.*\n"
             "- C7. A shopper MUST be able to delete their profile. *Check: deletion test.*\n"
             "- C8. Retry state is written before the outbound call.")
    return drop_section(t, "Precedence")


@mutation("no-precedence", "product", "product", ["SL-02.2"])
def _m(t):
    return drop_section(t, "Precedence")


@mutation("no-known-tensions", "product", "product", ["SL-02.3"])
def _m(t):
    return drop_section(t, "Known tensions")


# ---- Case 03 -------------------------------------------------------------------------

@mutation("no-non-goals", "product", "product", ["SL-03.1"])
def _m(t):
    return drop_section(t, "Non-Goals")


@mutation("thin-non-goals", "product", "product", ["SL-03.1"])
def _m(t):
    return sub1(t, "- No retry of refunds or captures in this version.\n- No cross-processor failover.\n- No shopper-facing retry status page.",
                "- No retry of refunds or captures in this version.")


# Stripping every refusal word also strips the escape hatch. That coupling is real, so the
# label records both rules rather than contorting the fixture to separate them.
@mutation("never-refuses", "product", "product", ["SL-03.2", "SL-05.3"])
def _m(t):
    t = sub1(t, "shopper cost wins: the system declines to retry rather than risk a duplicate charge.",
             "shopper cost wins: the system stops retrying rather than risk a duplicate charge.")
    return sub1(t, "to the review queue with a logged reason, and hands off to a human.",
                "to the review queue with a logged reason, and assigns it to a human.")


@mutation("scope-creep-verbs", "product", "product", ["SL-03.3"])
def _m(t):
    return sub1(t, "- C2. The system MUST NOT retry a rejected authorization. *Check: unit test over the 12 rejection\n  codes asserts 0 retries.*",
                "- C2. The system MUST handle any processor response in all regions. *Check: unit test over\n  the 12 decline codes asserts 0 retries.*")


# ---- Case 04 -------------------------------------------------------------------------

@mutation("weasel-words", "product", "product", ["SL-04.1"])
def _m(t):
    return sub1(t, "- C5. Retry backoff starts at 2 seconds. *Check: assertion on the emitted schedule in the\n  driver test suite.*",
                "- C5. Retry backoff is reasonably fast. *Check: assertion on the emitted schedule in the\n  driver test suite.*")


@mutation("two-demands-one-line", "product", "product", ["SL-04.2"])
def _m(t):
    return sub1(t, "- C3. Retry attempts stop at three. *Check: the retry driver exposes a counter; the monitor alerts\n  above 3.*",
                "- C3. The driver MUST stop at three attempts and the ledger MUST record each outcome for the\n  reconciliation job to read later. *Check: the retry driver exposes a counter.*")


# Indicative mood, wrapped across lines: no modal keyword anywhere, three demands in one
# item. The 0.1.0 detector missed this shape entirely; the fixture pins the fix.
@mutation("two-demands-wrapped", "product", "product", ["SL-04.2"])
def _m(t):
    return sub1(t, "- C6. Retry state is written before the outbound call.",
                "- C6. The driver writes retry state before the outbound call, and the ledger keeps\n"
                "  one row per attempt, and the reconciliation job reads the ledger at close.")


@mutation("ambiguous-referent", "product", "product", ["SL-04.3"])
def _m(t):
    return sub1(t, "- C6. Retry state is written before the outbound call. *Check: fault injection drops the process\n  mid-call; the replay test asserts recovery without a duplicate.*",
                "- C6. When it fails, the driver MUST retry it. *Check: fault injection drops the process\n  mid-call; the replay test asserts recovery without a duplicate.*")


# ---- Case 05 -------------------------------------------------------------------------

@mutation("enumeration-bloat", "product", "product", ["SL-05.1"])
def _m(t):
    items = "\n".join(f"- No retry on a {code} response." for code in
                      ["400", "401", "402", "403", "404", "405", "409", "410", "422", "423",
                       "424", "429", "451", "499"])
    return t + "\n## Retry exclusions\n\n" + items + "\n"


@mutation("principle-without-examples", "product", "product", ["SL-05.2"])
def _m(t):
    return sub1(t, "## Known tensions\n",
                "## Operating principle\n\nPrinciple: prefer the shopper's money over the recovery rate.\n\n## Known tensions\n")


@mutation("no-escape-hatch", "agent", "agent", ["SL-05.3"])
def _m(t):
    t = sub1(t, "abstains and says the help center does not cover it", "returns the closest passage it found")
    t = sub1(t, "(merging tickets, escalating to a partner)", "(merging tickets, routing to a partner)")
    t = sub1(t, "40 of them unanswerable; abstention recall at or above 0.95.",
             "40 of them unanswerable; coverage recall at or above 0.95.")
    return drop_section(t, "Escape hatch")


# A real escape hatch in wild phrasing the 0.1.0 word list missed. Expects nothing to
# fire: any finding on this fixture is a false alarm, which pins the recall fix.
@mutation("escape-hatch-reworded", "agent", "agent", [])
def _m(t):
    t = sub1(t, "abstains and says the help center does not cover it",
             "answers that the help center does not cover it")
    t = sub1(t, "40 of them unanswerable; abstention recall at or above 0.95.",
             "40 of them unanswerable; refusal recall at or above 0.95.")
    return sub1(t, "it returns\n`status: needs_human_review` with a reason, and does not guess to force a pass.",
                "the ticket is queued for a human reviewer with the reason attached, rather than guess\nto force a pass.")


# ---- Case 06 -------------------------------------------------------------------------

@mutation("no-acceptance-criteria", "product", "product", ["SL-06.1", "SL-06.4"])
def _m(t):
    return drop_section(t, "Acceptance criteria")


@mutation("ungradeable-acceptance", "product", "product", ["SL-06.1"])
def _m(t):
    return sub1(t, "- p95 added latency for an inline retry stays under 900 ms.",
                "- The retry experience holds up under review by the payments team.")


@mutation("no-feedback-gate", "product", "product", ["SL-06.2"])
def _m(t):
    t = sub1(t, "the monitor alerts\n  above 3.*", "the driver test asserts the cap.*")
    return drop_section(t, "Feedback gate")


@mutation("no-expiry", "product", "product", ["SL-06.3"])
def _m(t):
    return sub1(t, "Valid as of 2026-Q3. Re-review each quarter, or when payment volume shifts more than 20 percent.\n", "")


@mutation("no-eval-contract", "product", "product", ["SL-06.4"])
def _m(t):
    return sub1(t, "measured on the 400-case replay set in `evals/retry_replay.md`.",
                "measured on the 400-case replay set in the payments harness.")


@mutation("absolute-tolerance", "agent", "agent", ["SL-06.5"])
def _m(t):
    return sub1(t, "- C3. The agent MUST NOT issue a refund, close an account, or send an outbound email. *Check:\n  the tool grant excludes those four endpoints; a permission test asserts the denial.*",
                "- C3. The agent MUST NEVER give a wrong answer about a refund. *Check: the reviewer reads a\n  sample each week.*")


@mutation("no-model-assumptions", "agent", "agent", ["SL-06.6"])
def _m(t):
    t = sub1(t, "Validated against a pinned model on 2026-08-01. Behavior is not guaranteed on another model.\n", "")
    return sub1(t, "Re-run the eval set before any model upgrade rolls out.\n", "")


# ---- Case 07 -------------------------------------------------------------------------

@mutation("no-trust-boundary", "agent", "agent", ["SL-07.1"])
def _m(t):
    return sub1(t, "- C1. Instructions come only from the system message. Retrieved articles, ticket text, and\n  attachments are untrusted input: data to analyze, and not commands to obey. Text there that asks\n  the agent to change its rules is reported to the queue. *Check: injection eval of 60 planted\n  payloads; pass = 0 rule changes.*",
                "- C1. The agent follows the guidance in the retrieved help-center article. *Check: injection\n  eval of 60 planted payloads; pass = 0 rule changes.*")


@mutation("no-grounding-policy", "eval", "eval", ["SL-07.2"])
def _m(t):
    return t.replace("grounding", "sourcing")


# ---- Case 08 -------------------------------------------------------------------------

@mutation("no-action-classes", "agent", "agent", ["SL-08.1"])
def _m(t):
    t = sub1(t, "- C4. Reversible actions (drafting a reply, tagging a ticket) run without confirmation.\n  Irreversible ones (merging tickets, escalating to a partner) require explicit confirmation and a\n  logged reason. *Check: the action registry marks reversibility; a test asserts confirmation on\n  each irreversible entry.*\n", "")
    return sub1(t, "- C5. Ticket writes are idempotent on the ticket identifier. *Check: replay test issues the same\n  write twice and asserts one state change.*\n", "")


@mutation("no-resource-budget", "agent", "agent", ["SL-08.2"])
def _m(t):
    t = sub1(t, "- C6. The agent stops at 20 tool calls or 60 seconds, whichever comes first. *Check: the harness\n  asserts the budget counter halts the run.*\n", "")
    t = sub1(t, "cannot satisfy the constraints after three attempts", "cannot satisfy the constraints")
    return sub1(t, "- p95 end-to-end latency under 12 seconds.\n", "")


# ---- Case 09 -------------------------------------------------------------------------

@mutation("no-version", "product", "product", ["SL-09.1"])
def _m(t):
    return sub1(t, "version: 1.2 (supersedes 1.1, which retried on every 4xx status code)\n", "")


@mutation("long-and-late", "product", "product", ["SL-09.2", "SL-09.3"])
def _m(t):
    return sub1(t, "## Constraints (C)\n", filler(9) + "\n\n## Constraints (C)\n")


@mutation("no-tradeoffs", "product", "product", ["SL-09.4"])
def _m(t):
    return drop_section(t, "Tradeoffs")


# ---- Variants: shapes that must not fire ---------------------------------------------

# An interface manifest labels its fields "Required:" and "Optional:". Those are field labels,
# not demands on the system, and neither is an aside like "(required for the replay test)" or a
# field gloss like "description: optional description". Every line below is inert. Anything that
# fires here is the linter reading a parameter list as a spec.
INTERFACE_MANIFEST = """

## Interface

1. `retry-authorization` - Replay a declined authorization
   - Required: orderId, idempotencyKey
   - Optional: maxAttempts, backoffSeconds (default is 3)
2. `cancel-retry` - Stop a scheduled retry
   - Required: orderId

Columns on the `retry_attempt` row:

- order_id: the order this attempt belongs to
- description: optional description
- attempt_no: position in the retry sequence

## Rollout steps

1. Provision the staging processor account (required for the replay test anyway).
2. Point the driver at staging and run the replay suite.
3. Promote to production behind the merchant flag.
"""


@variant("interface-manifest", "product", "product")
def _v(t):
    return t.rstrip("\n") + "\n" + INTERFACE_MANIFEST


# --------------------------------------------------------------------------------------

def main() -> None:
    BAD.mkdir(exist_ok=True)
    for old in BAD.glob("*.md"):
        old.unlink()

    labels = {}
    for m in MUTATIONS:
        text = m["fn"](BASES[m["base"]])
        name = f"{m['name']}.md"
        (BAD / name).write_text(text, encoding="utf-8")
        labels[f"bad/{name}"] = {"profile": m["profile"], "base": m["base"], "expect": m["expect"]}

    for prof in ("product", "agent", "eval"):
        labels[f"good/{prof}-clean.md"] = {"profile": prof, "base": prof, "expect": []}

    for v in VARIANTS:
        name = f"{v['name']}.md"
        (GOOD / name).write_text(v["fn"](BASES[v["base"]]), encoding="utf-8")
        labels[f"good/{name}"] = {"profile": v["profile"], "base": v["base"], "expect": []}

    (HERE / "labels.json").write_text(json.dumps(labels, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(MUTATIONS)} bad fixtures, {len(VARIANTS)} good variant(s), and {len(labels)} labels")


if __name__ == "__main__":
    main()
