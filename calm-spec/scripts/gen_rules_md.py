#!/usr/bin/env python3
"""Generate rules/RULES.md from rules/rules.json so the two cannot drift apart."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REG = HERE.parent / "rules" / "rules.json"
OUT = HERE.parent / "rules" / "RULES.md"

def main() -> None:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    L = []
    L.append("# calm-spec rule pack\n")
    L.append(f"Generated from `rules.json`, pack version {reg['pack_version']}. Do not edit by hand: "
             "edit the registry and re-run `scripts/gen_rules_md.py`.\n")
    L.append(f"{len(reg['rules'])} rules across {len(reg['cases'])} cases. "
             f"{sum(1 for r in reg['rules'] if r['layer'] == 'form')} are computed by the script "
             f"(FORM). {sum(1 for r in reg['rules'] if r['layer'] == 'judgment')} need a reader "
             "(JUDGMENT) and carry no weight in the script's score.\n")
    L.append("Each rule carries a fixed weight, set per rule in the registry; the score sums the "
             "weights of the form rules that pass. Severity (gate, advisory, off) is set per "
             "profile, and a rule marked `off` for a profile is not run for that profile.\n")
    L.append("Every rule carries a before-and-after pair, one on a product spec line and one on an "
             "agent prompt line, and one sentence naming the call the tool leaves to the person.\n")
    L.append("## Sources\n")
    for k, v in reg["sources"].items():
        L.append(f"- **{k}** {v}")
    L.append("")
    for case in reg["cases"]:
        L.append(f"## Case {case['id']}: {case['title']}\n")
        L.append(f"**The one-question test:** {case['one_question_test']}\n")
        L.append("| Rule | Layer | product | agent | eval | Name |")
        L.append("|---|---|---|---|---|---|")
        rules = [r for r in reg["rules"] if r["case"] == case["id"]]
        for r in rules:
            p = r["profiles"]
            L.append(f"| `{r['id']}` | {r['layer']} w{r['weight']} | {p['product']} | "
                     f"{p['agent']} | {p['eval']} | {r['name']} |")
        L.append("")
        for r in rules:
            L.append(f"### {r['id']}  {r['name']}\n")
            L.append(f"*Sources: {', '.join(r['sources'])}.*\n")
            L.append(f"**Why it is here.** {r['why']}\n")
            L.append(f"**What is checked.** {r['check']}\n")
            L.append(f"**Fix.** {r['fix']}\n")
            if r.get("examples"):
                L.append("**Before and after.**\n")
                for ex in r["examples"]:
                    label = {"product": "Product spec", "agent": "Agent prompt"}.get(ex["kind"], ex["kind"])
                    L.append(f"- *{label}.* Lie: {ex['lie']} Fix: {ex['fix']}")
                L.append("")
            if r.get("judgment"):
                L.append(f"**The call that stays with the person.** {r['judgment']}\n")
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"wrote {OUT} ({len(reg['rules'])} rules)")


if __name__ == "__main__":
    main()
