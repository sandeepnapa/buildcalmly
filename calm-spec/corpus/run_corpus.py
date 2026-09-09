#!/usr/bin/env python3
"""
run_corpus.py - measure the deterministic layer against the labeled corpus.

For every fixture, run the form rules for that fixture's profile and compare what fired
against labels.json. A rule that fires where the label expects it is a hit. A rule that
fires where no label expects it is a false alarm. A rule the label expects that stays
silent is a miss.

    python3 run_corpus.py
    python3 run_corpus.py --json

Exit code 1 if any rule scores below the floor, so the corpus can gate a release.
"""

import argparse
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.dont_write_bytecode = True  # bytecode embeds the absolute source path; keep it out of the package
sys.path.insert(0, str(HERE.parent / "scripts"))

import spec_lint  # noqa: E402

FLOOR = 1.0  # every rule must hit every planted defect and raise no false alarm


def check_orphans(labels) -> None:
    """Stop before grading if labels.json and the fixture files on disk disagree."""
    on_disk = {f"{sub}/{p.name}" for sub in ("good", "bad") for p in (HERE / sub).glob("*.md")}
    for rel in sorted(set(labels) - on_disk):
        print(f"orphan label, no file on disk: {rel}", file=sys.stderr)
    for rel in sorted(on_disk - set(labels)):
        print(f"orphan fixture, no entry in labels.json: {rel}", file=sys.stderr)
    if set(labels) != on_disk:
        sys.exit(2)


def measure():
    labels = json.loads((HERE / "labels.json").read_text(encoding="utf-8"))
    check_orphans(labels)
    reg = spec_lint.load_registry()
    form_ids = [r["id"] for r in reg["rules"] if r["layer"] == "form"]
    stat = {rid: {"hit": 0, "false_alarm": 0, "miss": 0} for rid in form_ids}
    per_fixture = {}

    for rel, meta in sorted(labels.items()):
        doc = spec_lint.Doc.load(HERE / rel)
        res = spec_lint.run(doc, reg, meta["profile"])
        fired = {rid for rid, found in res["per_rule"].items() if found}
        expected = set(meta["expect"])
        applicable = {r["id"] for r in reg["rules"]
                      if r["layer"] == "form" and r["profiles"].get(meta["profile"]) != "off"}
        for rid in expected & applicable:
            if rid in fired:
                stat[rid]["hit"] += 1
            else:
                stat[rid]["miss"] += 1
        for rid in fired - expected:
            stat[rid]["false_alarm"] += 1
        per_fixture[rel] = {"expected": sorted(expected), "fired": sorted(fired),
                            "missed": sorted((expected & applicable) - fired),
                            "false_alarms": sorted(fired - expected)}
    return reg, stat, per_fixture


def rate(hit, other):
    total = hit + other
    return 1.0 if total == 0 else hit / total


def main() -> None:
    ap = argparse.ArgumentParser(description="Measure calm-spec against its labeled corpus.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    reg, stat, per_fixture = measure()
    by_id = {r["id"]: r for r in reg["rules"]}

    rows = []
    for rid, s in sorted(stat.items()):
        prec = rate(s["hit"], s["false_alarm"])
        rec = rate(s["hit"], s["miss"])
        rows.append({"rule": rid, "name": by_id[rid]["name"], "planted": s["hit"] + s["miss"],
                     "hit": s["hit"], "miss": s["miss"], "false_alarm": s["false_alarm"],
                     "precision": round(prec, 3), "recall": round(rec, 3)})

    failing = [r for r in rows if r["precision"] < FLOOR or r["recall"] < FLOOR]

    if args.json:
        print(json.dumps({"rows": rows, "failing": [r["rule"] for r in failing],
                          "fixtures": per_fixture}, indent=2))
    else:
        print(f"calm-spec corpus   rules {reg['pack_version']}   "
              f"{len(per_fixture)} fixtures   {len(rows)} form rules\n")
        print(f"{'rule':<10} {'planted':>7} {'hit':>4} {'miss':>5} {'false':>6} {'prec':>6} {'rec':>6}  name")
        for r in rows:
            flag = "!" if r in failing else " "
            print(f"{r['rule']:<10} {r['planted']:>7} {r['hit']:>4} {r['miss']:>5} "
                  f"{r['false_alarm']:>6} {r['precision']:>6.2f} {r['recall']:>6.2f}{flag} {r['name'][:44]}")
        print()
        if failing:
            print(f"{len(failing)} rule(s) below the floor of {FLOOR:.0%}:\n")
            for r in failing:
                print(f"  {r['rule']}  precision {r['precision']:.2f}  recall {r['recall']:.2f}")
                for rel, f in sorted(per_fixture.items()):
                    if r["rule"] in f["missed"]:
                        print(f"      miss on {rel}")
                    if r["rule"] in f["false_alarms"]:
                        print(f"      false alarm on {rel}")
        else:
            print(f"All {len(rows)} form rules at {FLOOR:.0%} precision and recall on this corpus.")
    sys.exit(1 if failing else 0)


if __name__ == "__main__":
    main()
