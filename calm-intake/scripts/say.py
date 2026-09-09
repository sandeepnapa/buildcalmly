#!/usr/bin/env python3
"""Print the lines calm-intake says out loud, so they cannot be skipped or paraphrased.

Two subcommands:

    say.py opening                 the stage 0 opening, with the invitation
    say.py opening --request TEXT  the same opening, ending in a reflection of TEXT
    say.py gate N                  the progress marker for gate N (0 to 2)

Paste the output verbatim. This script is the source of truth for both strings; the copies in
../reference/questions.md and ../../workflow.md are documentation and follow it.

No arguments beyond these, no filesystem writes, no network calls.
"""

from __future__ import annotations

import argparse
import sys

OPENING = """Hello! My goal is to help you get a real problem written down clearly enough to build from, yours or your users'. We'll do it in two passes.

First, we figure out what's needed. You tell me what you want, I sort the underlying needs from the asks, and we put them in an order.

Then we pin down what the first one has to do. I ask you ten questions, write it up, and check it against the ways a spec usually goes wrong. What you get is a spec a builder can work from without coming back to ask you what you meant.

At each stage I'll pause and ask for your feedback. We can stop whenever you like and pick up later from wherever we left off."""

INVITATION = """Whenever you're ready, tell me in your own words, or your users' words, what you'd like to build or fix. Rough is fine, and messy is genuinely useful. Something like: "People keep asking me for the same dashboard and I keep rebuilding it by hand."

If it helps to have a starting point: what breaks today, who it happens to, and what you do instead right now. For that same one: "It broke again on Monday. It's mostly the ops team, and right now I copy last month's file and edit it for an hour." """

REFLECTION = """You've already described it: "{request}". I'm taking that as our starting point, so you don't have to type it twice. Add anything you left out, or just say go and I'll start sorting it into pieces."""

# Gates passed, going in and once green, for each gate. Read off this table so no session
# recomputes a different figure. ../../workflow.md carries the same scale as documentation.
SCALE = {0: 0, 1: 33, 2: 67, 3: 100}

GLOSS = "A gate is a point where I stop and wait for your answer."


def marker(gates_passed: int) -> str:
    return f"Gates passed: {gates_passed} of 3 ({SCALE[gates_passed]}%)"


def say_opening(request: str | None) -> str:
    if request:
        return OPENING + "\n\n" + REFLECTION.format(request=request)
    return OPENING + "\n\n" + INVITATION.rstrip()


def say_gate(n: int) -> str:
    if n not in range(3):
        raise SystemExit(f"gate must be 0 to 2, got {n}")
    line = f"{marker(n)}, and {n + 1} of 3 ({SCALE[n + 1]}%) once this is settled."
    if n == 0:
        return line + " " + GLOSS
    return line


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description="Print what calm-intake says out loud.")
    sub = p.add_subparsers(dest="what", required=True)

    o = sub.add_parser("opening", help="the stage 0 opening")
    o.add_argument("--request", default=None,
                   help="the person's verbatim words, when the request arrived with the invocation")

    g = sub.add_parser("gate", help="the progress marker for a gate")
    g.add_argument("n", type=int, help="gate number, 0 to 2")

    a = p.parse_args(argv)
    if a.what == "opening":
        print(say_opening(a.request))
    else:
        print(say_gate(a.n))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
