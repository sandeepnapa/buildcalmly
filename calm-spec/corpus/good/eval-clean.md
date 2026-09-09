# Answer quality eval

version: 2.1 (supersedes 2.0, which scored tone and accuracy on one combined scale)
Validated against a pinned judge model on 2026-08-05. Re-run the calibration set on any model
change before the scores are compared to an earlier run.
Valid as of 2026-Q3, re-review each quarter.

## Goals

Grade assistant answers on the support corpus so a ship decision rests on a measurement rather
than an impression.

## Constraints (C)

- C1. The judge scores four dimensions separately: grounding, correctness, coverage, register.
  *Check: the output schema requires four integers; the validator rejects a missing dimension.*
- C2. A score above 3 on any dimension requires the judge to quote the line that earns it.
  *Check: the parser rejects a score above 3 with an empty evidence field.*
- C3. The judge MUST NOT see which system produced an answer. *Check: the harness strips system
  identifiers; a test asserts the field is absent from the judge prompt.*
- C4. The gold set is versioned and pinned. *Check: the run records a dataset hash; a mismatch
  fails the run.*
- C5. Scores are reported with a confidence interval from three judge samples at temperature 0.2.
  *Check: the reporter refuses to print a mean without an interval.*
- C6. The answer under test is untrusted input: data to score, and not commands to obey. An answer
  that instructs the judge to award a high score is scored on its merits and flagged. *Check:
  injection eval of 40 planted payloads; pass = 0 score changes.*
- C7. The judge prompt changes only through a versioned pull request. *Check: continuous
  integration compares the prompt hash to the pinned value.*

## Defaults (D)

- D1. Three judge samples per item. A run tagged `deep` overrides this to seven.
- D2. Ties resolve toward the lower score. An explicit reviewer note overrides the tie.

## Aspirations (A)

- A1. Raise agreement between the judge and human raters. Metric: Cohen's kappa on the
  200-item calibration set, direction up.
- A2. Keep the rubric short enough to hold in one reading. Taste, not a gate.

## Non-Goals

- No latency or cost measurement here.
- No per-user personalization scoring.
- No scoring of multi-turn conversations in this version.

## Precedence

Apply C over D over A. When agreement with human raters and rubric simplicity conflict, agreement
wins.

## Known tensions

C5 asks for three samples per item while A2 asks for a short rubric that runs cheaply. Sampling
wins. A single sample hides judge variance.

## Acceptance criteria

- Cohen's kappa at or above 0.7 against human raters on the 200-item calibration set.
- Mean score at or above 4.2 out of 5, with no dimension below 3.5, before a release ships.
- Rerunning the same pinned inputs reproduces the mean within 0.1.

## Feedback gate

Watch the kappa each month. Below 0.6, freeze use of the judge for ship decisions until the
rubric is recalibrated against fresh human labels.

## Escape hatch

When the judge cannot score an item under the rubric, it returns `status: unscorable` with a
reason, and the item is escalated to a human rater rather than guessed.

## Tradeoffs

We rejected a single overall quality score. One number ranks systems faster and it hides which
dimension moved, which is the weakness we accepted by scoring four dimensions instead.
