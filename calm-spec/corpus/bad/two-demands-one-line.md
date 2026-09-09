# Checkout retry policy

version: 1.2 (supersedes 1.1, which retried on every 4xx status code)
Valid as of 2026-Q3. Re-review each quarter, or when payment volume shifts more than 20 percent.

## Goals

Recover payment authorizations that fail for transient reasons, without charging a shopper twice.

## Constraints (C)

- C1. A retried authorization carries the same idempotency key as the original attempt.
  *Check: integration test asserts one ledger row per key across 500 replayed 5xx responses.*
- C2. The system MUST NOT retry a rejected authorization. *Check: unit test over the 12 rejection
  codes asserts 0 retries.*
- C3. The driver MUST stop at three attempts and the ledger MUST record each outcome for the
  reconciliation job to read later. *Check: the retry driver exposes a counter.*
- C4. A shopper sees one charge line per completed order. *Check: nightly query joins ledger to
  orders; more than one line per order fails the job.*
- C5. Retry backoff starts at 2 seconds. *Check: assertion on the emitted schedule in the
  driver test suite.*
- C6. Retry state is written before the outbound call. *Check: fault injection drops the process
  mid-call; the replay test asserts recovery without a duplicate.*

## Defaults (D)

- D1. Backoff doubles between attempts. A merchant configuration flag overrides the schedule.
- D2. Retries run in the background. A checkout tagged `interactive` overrides this and retries
  inline.

## Aspirations (A)

- A1. Reduce the share of abandoned checkouts caused by transient failure. Metric: abandonment
  rate on authorization error, direction down.
- A2. Keep the retry driver readable enough for an on-call engineer to trace one order. Taste,
  not a gate.

## Non-Goals

- No retry of refunds or captures in this version.
- No cross-processor failover.
- No shopper-facing retry status page.

## Precedence

When guidance conflicts, apply C over D over A. When shopper cost and recovery rate conflict,
shopper cost wins: the system declines to retry rather than risk a duplicate charge.

## Known tensions

C3 caps attempts at three while A1 pushes recovery rate up. The cap wins. Raising it needs a new
version of this document and a fresh duplicate-charge measurement.

## Acceptance criteria

- At least 92 percent of transient authorization failures recover within the three attempts,
  measured on the 400-case replay set in `evals/retry_replay.md`.
- Duplicate charge count is 0 across the replay set.
- p95 added latency for an inline retry stays under 900 ms.

## Feedback gate

Watch the duplicate-charge rate weekly. Above 0.05 percent for two consecutive weeks, freeze
retry changes until the rate recovers.

## Escape hatch

When the processor returns a status the policy does not cover, the driver stops, writes the order
to the review queue with a logged reason, and hands off to a human.

## Tradeoffs

We rejected cross-processor failover for this version. It raises the recovery rate and it doubles
the reconciliation surface, which is the weakness we accepted by leaving it out.
