#!/usr/bin/env python3
"""
spec_lint.py - the deterministic layer of calm-spec.

Grades a Markdown spec against the rule registry in ../rules/rules.json and prints a
binary gate, per-case sub-scores, and a fix for every finding. Standard library only:
no network, no packages to install, so it runs unchanged in a sandboxed skill container.

    python3 spec_lint.py spec.md
    python3 spec_lint.py spec.md --profile agent
    python3 spec_lint.py spec.md --json
    python3 spec_lint.py --list-rules

Exit code 1 when any gate rule reports a finding, 0 otherwise.

Suppression, on the line before the offending line or anywhere in the file:
    <!-- calm-spec: ignore SL-04.1 -->
    <!-- calm-spec: ignore-file SL-04.1 SL-03.3 -->
    <!-- calm-spec: profile agent -->

The legacy prefix "spec-lint:" is still accepted in place of "calm-spec:".
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

VERSION = "0.1.4"
REGISTRY = Path(__file__).resolve().parent.parent / "rules" / "rules.json"
MAX_FINDINGS_PER_RULE = 10

# --------------------------------------------------------------------------------------
# vocabulary
# --------------------------------------------------------------------------------------

HARD_MODALS = r"MUST NOT|MUST|SHALL NOT|SHALL|REQUIRED|NEVER"
SOFT_MODALS = r"SHOULD NOT|SHOULD|MAY NOT|MAY|RECOMMENDED|OPTIONAL"
# RFC 2119 puts the keywords in capitals. A capitalised modal is a requirement anywhere.
# A lower-case one counts only inside a list item or a typed section, which keeps ordinary
# prose ("this must be why", "never as a wall of ten") out of the findings.
ANY_MODAL_CAPS = re.compile(rf"\b({HARD_MODALS}|{SOFT_MODALS})\b")
HARD_MODAL_CAPS = re.compile(rf"\b({HARD_MODALS})\b")
ANY_MODAL = re.compile(rf"\b({HARD_MODALS}|{SOFT_MODALS})\b", re.I)
HARD_MODAL = re.compile(rf"\b({HARD_MODALS})\b", re.I)

# REQUIRED, OPTIONAL and RECOMMENDED are ordinary English words as well as RFC 2119 modals.
# Below the capitalised form they routinely appear where no demand is being made: as an interface
# field label ("Required: listId, title"), as an aside ("(required for the replay test anyway)"),
# or in the gloss of a field list ("description: optional description"). Blank those occurrences
# before the lower-case modal test, so an interface manifest is not read as a spec. The verb
# modals are never blanked, which keeps "- backoff: must double between attempts" a requirement.
ADJ_MODALS = r"REQUIRED|OPTIONAL|RECOMMENDED"
_LIST_MARKER = r"(?:[-*+]|\d+[\.\)])"
_IDENT = r"[A-Za-z_][\w.\[\]-]*"
# "Required: listId, displayName" labels a parameter list. "Required: every retry carries a key"
# states a demand, so the label form is credited only where the value is a bare identifier list.
ADJ_AS_LABEL = re.compile(
    rf"^(\s*(?:{_LIST_MARKER})?\s*[`*_]*)({ADJ_MODALS})([`*_]*\s*[:=]\s*"
    rf"[`*_]*{_IDENT}(?:\s*,\s*{_IDENT})*,?(?:\s*\([^()]*\))?[`*_.\s]*)$", re.I)
ADJ_IN_PARENS = re.compile(rf"\([^()]*\b({ADJ_MODALS})\b[^()]*\)", re.I)
# "- description: optional description" glosses a field. Group 1 is the key, up to the colon.
FIELD_GLOSS = re.compile(rf"^(\s*{_LIST_MARKER}\s*[`*_]*{_IDENT}(?:\s*,\s*{_IDENT})*[`*_]*\s*:)\s")
ADJ_ANY = re.compile(rf"\b({ADJ_MODALS})\b", re.I)


def _blank(m) -> str:
    """Same width, no word characters, so no new token boundary appears. An upper-case modal is
    the RFC 2119 keyword and always survives."""
    return m.group(0) if m.group(0).isupper() else " " * len(m.group(0))


def demodal(text: str) -> str:
    """Blank the adjective modals where they label or describe a field rather than demand
    something. Width-preserving, so line offsets survive."""
    m = ADJ_AS_LABEL.match(text)
    if m and not m.group(2).isupper():
        text = m.group(1) + " " * len(m.group(2)) + m.group(3)
    text = ADJ_IN_PARENS.sub(lambda x: ADJ_ANY.sub(_blank, x.group(0)), text)
    g = FIELD_GLOSS.match(text)
    if g:
        text = text[:g.end(1)] + ADJ_ANY.sub(_blank, text[g.end(1):])
    return text

CHECK_MARKER = re.compile(r"\b(check|test|gate|verified by|verify|assert|measured by)\s*[:=]", re.I)
# "Check: none yet" carries the marker and no check. Strip these before crediting a marker.
CHECK_PLACEHOLDER = re.compile(
    r"\b(check|test|gate|verified by|verify|assert|measured by)\s*[:=]\s*"
    r"(none|nothing|tbd|todo|n/?a|\?+|pending|later|unknown|open|"
    r"to be (determined|defined|decided|written|added))\b", re.I)

WEASEL = [
    "fast", "quick", "quickly", "snappy", "responsive", "intuitive", "delightful", "delight",
    "seamless", "seamlessly", "smooth", "robust", "scalable", "performant", "user-friendly",
    "easy to use", "clean", "modern", "polished", "professional", "high-quality", "high quality",
    "best-in-class", "world-class", "appropriate", "appropriately", "as needed", "as necessary",
    "reasonable", "reasonably", "sufficient", "sufficiently", "adequate", "adequately", "minimal",
    "efficient", "efficiently", "flexible", "powerful", "rich", "comprehensive", "graceful",
    "gracefully", "engaging", "meaningful", "significant", "substantial", "timely", "simple",
    "straightforward", "lightweight", "reliable", "secure", "accurate", "relevant", "helpful",
]
SCOPE_CREEP = [
    "all", "any", "every", "everything", "anything", "arbitrary", "unlimited", "infinite",
    "exhaustive", "fully", "completely", "entirely", "universal", "whatever",
]
PRONOUNS = ["it", "this", "that", "they", "them", "these", "those"]

SECTION_ALIASES = {
    "constraints": ["constraint", "constraints", "hard rules", "rules", "must", "requirements (hard)"],
    "defaults": ["default", "defaults", "default behavior", "default behaviour"],
    "aspirations": ["aspiration", "aspirations", "objectives", "directions", "optimize for"],
    "goals": ["goal", "goals", "objective", "intent", "purpose"],
    "non_goals": ["non-goal", "non-goals", "non goals", "nongoals", "out of scope",
                  "out-of-scope", "will not", "will not do", "exclusions", "not in scope"],
    "acceptance": ["acceptance", "acceptance criteria", "done", "definition of done",
                   "graduation criteria", "ship criteria", "success criteria", "how we know"],
    "precedence": ["precedence", "priority order", "conflict resolution", "tie-break",
                   "tiebreak", "tie breaker", "tie-breaker", "chain of command", "authority"],
    "tensions": ["known tensions", "tensions", "conflicts", "known conflicts"],
    "tradeoffs": ["tradeoff", "tradeoffs", "trade-off", "trade-offs", "alternatives considered",
                  "rejected", "rejected alternatives", "what we gave up", "what this costs"],
    "trust": ["trust boundary", "trust and actions", "trust", "inputs and trust"],
    "actions": ["actions", "action surface", "action safety", "tools and actions"],
    "budget": ["budget", "budgets", "limits", "resource limits"],
}


def kw(text: str, words) -> bool:
    low = text.lower()
    return any(w in low for w in words)


# --------------------------------------------------------------------------------------
# document model
# --------------------------------------------------------------------------------------

@dataclass
class Section:
    title: str
    level: int
    start: int          # 1-indexed line of the heading
    end: int            # 1-indexed last line of the section


@dataclass
class Doc:
    path: str
    raw: str
    lines: list = field(default_factory=list)          # (lineno, text) with code fences blanked
    sections: list = field(default_factory=list)
    ignore_file: set = field(default_factory=set)
    ignore_line: dict = field(default_factory=dict)    # lineno -> set(rule ids)
    declared_profile: str | None = None
    _typed_ranges: list | None = None

    @classmethod
    def load(cls, path: Path) -> "Doc":
        raw = path.read_text(encoding="utf-8")
        doc = cls(path=str(path), raw=raw)
        doc._scan_pragmas()
        doc._scan_lines()
        doc._scan_sections()
        return doc

    # -- setup -------------------------------------------------------------------------
    def _scan_pragmas(self) -> None:
        pending: set = set()
        for i, text in enumerate(self.raw.splitlines(), start=1):
            m = re.search(r"<!--\s*(?:calm-spec|spec-lint):\s*(.+?)\s*-->", text)
            if m:
                body = m.group(1)
                parts = body.split()
                verb = parts[0].lower()
                args = [a.strip(",") for a in parts[1:]]
                if verb == "ignore-file":
                    self.ignore_file.update(args)
                elif verb == "ignore":
                    pending.update(args)
                elif verb == "profile" and args:
                    self.declared_profile = args[0].lower()
                continue
            if pending and text.strip():
                self.ignore_line.setdefault(i, set()).update(pending)
                pending = set()

    def _scan_lines(self) -> None:
        fenced = False
        for i, text in enumerate(self.raw.splitlines(), start=1):
            if re.match(r"^\s*(```|~~~)", text):
                fenced = not fenced
                self.lines.append((i, ""))
                continue
            self.lines.append((i, "" if fenced else text))

    def _scan_sections(self) -> None:
        heads = []
        for i, text in self.lines:
            m = re.match(r"^(#{1,6})\s+(.*\S)\s*$", text)
            if m:
                heads.append((i, len(m.group(1)), m.group(2)))
        total = len(self.lines)
        for idx, (line, level, title) in enumerate(heads):
            end = total
            for later_line, later_level, _ in heads[idx + 1:]:
                if later_level <= level:
                    end = later_line - 1
                    break
            self.sections.append(Section(title=title, level=level, start=line, end=end))

    # -- queries -----------------------------------------------------------------------
    @property
    def total_lines(self) -> int:
        return len(self.lines)

    def text_of(self, start: int, end: int) -> str:
        return "\n".join(t for i, t in self.lines if start <= i <= end)

    @property
    def body(self) -> str:
        return "\n".join(t for _, t in self.lines)

    def word_count(self) -> int:
        return len(re.findall(r"\b[\w'-]+\b", self.body))

    def find_section(self, key: str) -> Section | None:
        aliases = SECTION_ALIASES[key]
        for s in self.sections:
            norm = re.sub(r"[^a-z0-9 \-]", "", s.title.lower()).strip()
            norm = re.sub(r"^\d+[\.\)]?\s*", "", norm)
            for a in aliases:
                if norm == a or norm.startswith(a + " ") or norm.startswith(a + ":"):
                    return s
        return None

    def items_in(self, section: Section | None) -> list:
        """Bullet or numbered items directly inside a section."""
        if section is None:
            return []
        out = []
        for i, text in self.lines:
            if section.start < i <= section.end:
                if re.match(r"^\s*([-*+]|\d+[\.\)])\s+\S", text):
                    out.append((i, text.strip()))
        return out

    def typed_ranges(self) -> list:
        if self._typed_ranges is None:
            rs = []
            for key in ("constraints", "defaults", "aspirations", "acceptance"):
                s = self.find_section(key)
                if s:
                    rs.append((s.start, s.end))
            self._typed_ranges = rs
        return self._typed_ranges

    def requirement_lines(self, hard_only: bool = False) -> list:
        caps = HARD_MODAL_CAPS if hard_only else ANY_MODAL_CAPS
        lower = HARD_MODAL if hard_only else ANY_MODAL
        ranges = self.typed_ranges()
        out = []
        for i, text in self.lines:
            s = text.strip()
            if not s or s.startswith("#") or s.startswith(">"):
                continue
            if s.endswith("?"):          # a question is not a requirement
                continue
            if caps.search(text):
                out.append((i, s))
                continue
            listed = re.match(r"^\s*([-*+]|\d+[\.\)])\s+\S", text) is not None
            typed = any(a < i <= b for a, b in ranges)
            if (listed or typed) and lower.search(demodal(text)):
                out.append((i, s))
        return out

    def item_blocks(self, section: Section | None) -> list:
        """items_in, with each item's wrapped continuation lines joined back on.
        Returns (start_line, joined_text, end_line) per item."""
        if section is None:
            return []
        out, cur = [], None
        for i, text in self.lines:
            if not (section.start < i <= section.end):
                continue
            s = text.strip()
            if re.match(r"^\s*([-*+]|\d+[\.\)])\s+\S", text):
                if cur:
                    out.append((cur[0], " ".join(cur[1]), cur[2]))
                cur = [i, [s], i]
            elif cur and s and not s.startswith("#"):
                cur[1].append(s)
                cur[2] = i
            elif cur:
                out.append((cur[0], " ".join(cur[1]), cur[2]))
                cur = None
        if cur:
            out.append((cur[0], " ".join(cur[1]), cur[2]))
        return out

    def constraint_lines(self) -> list:
        """Hard-modal lines plus every item inside a Constraints section."""
        seen = {}
        for i, t in self.requirement_lines(hard_only=True):
            seen[i] = t
        sec = self.find_section("constraints")
        for i, t in self.items_in(sec):
            seen.setdefault(i, t)
        return sorted(seen.items())

    def lookahead(self, lineno: int, n: int = 2) -> str:
        got, out = 0, []
        for i, text in self.lines:
            if i <= lineno:
                continue
            if not text.strip():
                continue
            out.append(text)
            got += 1
            if got >= n:
                break
        return "\n".join(out)


# --------------------------------------------------------------------------------------
# findings
# --------------------------------------------------------------------------------------

@dataclass
class Finding:
    rule: str
    detail: str
    line: int = 0
    excerpt: str = ""


CHECKS = {}


def check(name):
    def deco(fn):
        CHECKS[name] = fn
        return fn
    return deco


LABEL = re.compile(r"^\s*([-*+]|\d+[\.\)])?\s*(\*\*)?\b[CDA]\d+\b[\.\):]?\s*(\*\*)?", re.I)


def unlabel(text: str) -> str:
    """Drop a leading list marker and an identifier like C3. or **A1** before word checks."""
    stripped = re.sub(r"^\s*([-*+]|\d+[\.\)])\s*", "", text)
    return LABEL.sub("", stripped) if LABEL.match(text) else stripped


def excerpt(text: str, limit: int = 92) -> str:
    t = re.sub(r"\s+", " ", text.strip().lstrip("-*+ ").strip())
    return t if len(t) <= limit else t[: limit - 3] + "..."


# --- Case 01 --------------------------------------------------------------------------

INLINE_TYPE = re.compile(r"(\*\*)?\b(C|D|A)\d*\b\s*[:.\)]|\[(C|D|A)\]|\b(CONSTRAINT|DEFAULT|ASPIRATION|RULE|OBJECTIVE)\b\s*[:\(]", re.I)


@check("check_typed_statements")
def _typed(doc: Doc, prof: str):
    typed_sections = [doc.find_section(k) for k in ("constraints", "defaults", "aspirations")]
    covered = [(s.start, s.end) for s in typed_sections if s]
    out = []
    for i, text in doc.requirement_lines():
        if any(a < i <= b for a, b in covered):
            continue
        if INLINE_TYPE.search(text):
            continue
        out.append(Finding("SL-01.1", "requirement is not typed as Constraint, Default, or Aspiration", i, excerpt(text)))
    return out


@check("check_constraint_has_check")
def _has_check(doc: Doc, prof: str):
    out = []
    # A constraint's check lives on its own wrapped lines. The lookahead fallback covers
    # hard-modal lines outside a list, where the check may sit on the lines that follow;
    # for list items it would credit an item with its neighbor's check.
    blocks = {a: joined for a, joined, _ in doc.item_blocks(doc.find_section("constraints"))}
    for i, text in doc.constraint_lines():
        window = blocks.get(i) or (text + "\n" + doc.lookahead(i, 2))
        if CHECK_MARKER.search(CHECK_PLACEHOLDER.sub("", window)):
            continue
        detail = ("the stated check is a placeholder, not a check"
                  if CHECK_MARKER.search(window) else "hard rule with no check behind it")
        out.append(Finding("SL-01.2", detail, i, excerpt(text)))
    return out


METRIC_HINT = re.compile(r"\d|%|\b(increase|decrease|reduce|raise|lower|minimi[sz]e|maximi[sz]e|up|down|higher|lower|fewer|more|faster|shorter)\b", re.I)


@check("check_aspiration_metric")
def _aspiration(doc: Doc, prof: str):
    sec = doc.find_section("aspirations")
    if sec is None:
        return []
    out = []
    for i, text, _ in doc.item_blocks(sec):
        bare = unlabel(text)
        if "taste" in bare.lower() or METRIC_HINT.search(bare):
            continue
        out.append(Finding("SL-01.3", "aspiration with no metric, no direction, and no admission of taste", i, excerpt(text)))
    return out


@check("check_default_override")
def _default(doc: Doc, prof: str):
    sec = doc.find_section("defaults")
    if sec is None:
        return []
    out = []
    for i, text, _ in doc.item_blocks(sec):
        if kw(unlabel(text), ["override", "overrid", "unless", "opt out", "opts out", "explicit choice", "when set", "if specified"]):
            continue
        out.append(Finding("SL-01.4", "default does not say what overrides it", i, excerpt(text)))
    return out


# --- Case 02 --------------------------------------------------------------------------

AUTHORITY_WORDS = ["legal", "regulatory", "regulation", "compliance", "platform policy",
                   "policy", "security", "privacy law", "gdpr", "hipaa", "statutory"]
TIER_WORDS = ["tier", "authority", "outranks", "takes precedence", "chain of command",
              "wins over", "ranks above", "precedence order"]


@check("check_authority_tiers")
def _authority(doc: Doc, prof: str):
    reqs = doc.requirement_lines()
    if not any(kw(t, AUTHORITY_WORDS) for _, t in reqs):
        return []
    if kw(doc.body, TIER_WORDS) or doc.find_section("precedence"):
        return []
    return [Finding("SL-02.1", "rules invoke an outside authority with no tier or authority ordering stated")]


PRECEDENCE_PAT = re.compile(
    r"(when|if)\b[^.\n]{0,80}\bconflict[^.\n]{0,80}\b(wins|takes precedence|overrides|prevails)"
    r"|\b(precedence|takes precedence|outranks|C\s*>\s*D\s*>\s*A|constraints over defaults)\b", re.I)


@check("check_precedence_stated")
def _precedence(doc: Doc, prof: str):
    if doc.find_section("precedence") or PRECEDENCE_PAT.search(doc.body):
        return []
    return [Finding("SL-02.2", "no precedence order: nothing says which rule wins when two collide")]


@check("check_known_tensions")
def _tensions(doc: Doc, prof: str):
    if len(doc.constraint_lines()) < 5:
        return []
    if doc.find_section("tensions") or kw(doc.body, ["known tension", "pulls in opposite", "in tension with", "trade against"]):
        return []
    return [Finding("SL-02.3", f"{len(doc.constraint_lines())} constraints and no named tension between any of them")]


# --- Case 03 --------------------------------------------------------------------------

@check("check_non_goals")
def _non_goals(doc: Doc, prof: str):
    sec = doc.find_section("non_goals")
    if sec is None:
        return [Finding("SL-03.1", "no Non-Goals section")]
    items = doc.items_in(sec)
    if len(items) < 3:
        return [Finding("SL-03.1", f"Non-Goals lists {len(items)} item(s); three is the floor", sec.start, excerpt(sec.title))]
    return []


REFUSAL_WORDS = ["refuse", "refusal", "decline", "hand off", "handoff", "hands off", "out of scope",
                 "abstain", "return null", "cannot", "can't", "will not attempt", "escalate",
                 "defer to a human", "say so", "not attempt", "no answer"]


@check("check_refusal_named")
def _refusal(doc: Doc, prof: str):
    if kw(doc.body, REFUSAL_WORDS):
        return []
    return [Finding("SL-03.2", "the spec never names a case where the system declines or hands off")]


@check("check_scope_creep_verbs")
def _scope_creep(doc: Doc, prof: str):
    out = []
    for i, text in doc.requirement_lines():
        hits = [w for w in SCOPE_CREEP if re.search(rf"\b{re.escape(w)}\b", text, re.I)]
        if hits:
            out.append(Finding("SL-03.3", "scope-creep word(s): " + ", ".join(sorted(set(hits))), i, excerpt(text)))
    return out


# --- Case 04 --------------------------------------------------------------------------

def _graded_lines(doc: Doc):
    """Requirement lines plus items in the typed sections. Word rules run only here."""
    seen = {}
    for i, t in doc.requirement_lines():
        seen[i] = t
    for key in ("constraints", "defaults", "aspirations", "acceptance"):
        for i, t in doc.items_in(doc.find_section(key)):
            seen.setdefault(i, t)
    return sorted(seen.items())


@check("check_weasel_words")
def _weasel(doc: Doc, prof: str):
    out = []
    for i, text in _graded_lines(doc):
        hits = [w for w in WEASEL if re.search(rf"\b{re.escape(w)}\b", text, re.I)]
        if hits:
            out.append(Finding("SL-04.1", "weasel word(s): " + ", ".join(sorted(set(hits))), i, excerpt(text)))
    return out


# An "and" opens a second demand only when it introduces a new subject. "abstains and says"
# is one demand with two verbs; "and the ledger MUST record" is a second demand.
AND_NEW_SUBJECT = re.compile(r"\band\s+(the|a|an|each|every|all|its|their|any|no)\b", re.I)


@check("check_hidden_conjunction")
def _conjunction(doc: Doc, prof: str):
    covered, blocks = set(), []
    for key in ("constraints", "defaults", "aspirations", "acceptance"):
        for a, joined, b in doc.item_blocks(doc.find_section(key)):
            blocks.append((a, joined))
            covered.update(range(a, b + 1))
    for i, text in doc.requirement_lines():
        if i not in covered:
            blocks.append((i, text))
    out = []
    for i, text in sorted(blocks):
        stripped = re.sub(r"\([^)]*\)", "", text)
        stripped = CHECK_MARKER.split(stripped)[0]   # the check clause is not a demand
        for sentence in re.split(r"(?<=[.;])\s+", stripped):
            ands = len(AND_NEW_SUBJECT.findall(sentence))
            words = len(re.findall(r"\b[\w'-]+\b", sentence))
            if ands >= 2 or (ands == 1 and words > 14):
                out.append(Finding("SL-04.2", "one item carrying more than one demand", i, excerpt(text)))
                break
    return out


@check("check_ambiguous_referent")
def _referent(doc: Doc, prof: str):
    pat = re.compile(r"(^|[,;:\s])(" + "|".join(PRONOUNS) + r")\s+(is|are|was|were|must|shall|should|may|will|fails?|returns?|happens?)\b", re.I)
    out = []
    for i, text in doc.requirement_lines():
        m = pat.search(text)
        if m:
            out.append(Finding("SL-04.3", f"bare referent '{m.group(2)}' standing in for the subject", i, excerpt(text)))
    return out


# --- Case 05 --------------------------------------------------------------------------

NEGATIVE_ITEM = re.compile(r"^\s*([-*+]|\d+[\.\)])\s*(no |not |never |don'?t |do not |avoid |disallow|forbid|prohibit)", re.I)


@check("check_enumeration_bloat")
def _bloat(doc: Doc, prof: str):
    out = []
    for sec in doc.sections:
        items = doc.items_in(sec)
        if len(items) <= 10:
            continue
        negs = [it for it in items if NEGATIVE_ITEM.match(it[1])]
        if len(negs) > 10 and len(negs) >= len(items) / 2:
            out.append(Finding("SL-05.1",
                               f"{len(negs)} enumerated prohibitions under '{sec.title}': a candidate for a principle plus examples",
                               sec.start, excerpt(sec.title)))
    return out


@check("check_principle_examples")
def _principle(doc: Doc, prof: str):
    out = []
    for i, text in doc.lines:
        if not re.search(r"\bprinciple\b\s*[:*\-]|\*\*principle", text, re.I):
            continue
        window = text + "\n" + doc.lookahead(i, 6)
        if re.search(r"\b(do:|don'?t:|example|for example|e\.g\.|owner:|tiebreak)", window, re.I):
            continue
        out.append(Finding("SL-05.2", "principle with no worked example pair and no tiebreak owner", i, excerpt(text)))
    return out


# Deliberately narrow. "halt" and "logged reason" were here and matched a budget counter
# and an audit trail, neither of which authorizes the system to give up. "human review" is
# also out: it matched "a human reviewer" approving drafts, which is oversight, no hatch.
ESCAPE_WORDS = ["needs_human_review", "needs human review", "escalate",
                "escalates", "abstain", "unable to comply", "cannot comply", "cannot satisfy",
                "hand off", "handoff", "hands off", "override with a logged reason",
                "i don't know", "not sure", "return null", "flag for review",
                "defer to a human", "ask a human", "give up and",
                "rather than guess", "queued for a human", "queues for a human",
                "queue for a human", "falls back to a human", "fall back to a human",
                "manual review", "allowed to fail", "allowed to answer", "allowed to say",
                "allowed to decline", "declines to", "refuses to"]


@check("check_escape_hatch")
def _escape(doc: Doc, prof: str):
    if kw(doc.body, ESCAPE_WORDS):
        return []
    return [Finding("SL-05.3", "no escape hatch: the system is never authorized to fail or say it does not know")]


# --- Case 06 --------------------------------------------------------------------------

GRADEABLE = re.compile(r"\d|%|>=|<=|>|<|\bat least\b|\bno more than\b|\bpass\s*=|\bzero\b|\bwithin\b|\.md\b|\bp\d{2}\b", re.I)


@check("check_acceptance_criteria")
def _acceptance(doc: Doc, prof: str):
    sec = doc.find_section("acceptance")
    if sec is None:
        return [Finding("SL-06.1", "no acceptance criteria: nothing states what done means")]
    items = [(a, t) for a, t, _ in doc.item_blocks(sec)]
    if not items:
        body = doc.text_of(sec.start + 1, sec.end)
        if not GRADEABLE.search(body):
            return [Finding("SL-06.1", "acceptance section carries no number, comparison, or named check", sec.start, excerpt(sec.title))]
        return []
    out = []
    for i, text in items:
        if not GRADEABLE.search(text):
            out.append(Finding("SL-06.1", "acceptance criterion a stranger cannot grade the same way twice", i, excerpt(text)))
    return out


# "page" was here for paging an on-call and matched the words "status page" instead.
TRIGGER_WORDS = ["trigger", "freeze", "roll back", "rollback", "alert", "page the",
                 "pages the", "halt", "block release", "stop shipping", "open a review",
                 "escalate"]
WATCH_WORDS = ["watch", "monitor", "track", "error budget", "rate", "threshold", "slo", "sli", "%"]


@check("check_feedback_gate")
def _feedback(doc: Doc, prof: str):
    if kw(doc.body, TRIGGER_WORDS) and kw(doc.body, WATCH_WORDS):
        return []
    return [Finding("SL-06.2", "no post-launch feedback gate: no watched metric with a threshold that triggers an action")]


EXPIRY_WORDS = ["valid as of", "valid until", "valid for", "expires", "expiry", "re-review",
                "review cadence", "revisit", "goes stale", "stale", "re-validate", "recheck on",
                "review by", "sunset"]


@check("check_expiry")
def _expiry(doc: Doc, prof: str):
    if kw(doc.body, EXPIRY_WORDS):
        return []
    return [Finding("SL-06.3", "no expiry or re-review trigger: nothing says when this spec goes stale")]


EVAL_WORDS = ["eval", "gold set", "golden set", "rubric", "benchmark", "test set", "holdout",
              "judge", "scored set", "fixture set"]


@check("check_eval_contract")
def _eval(doc: Doc, prof: str):
    body = doc.body
    if kw(body, EVAL_WORDS) and re.search(r"\d", body):
        return []
    return [Finding("SL-06.4", "no eval contract: acceptance points at no named dataset or rubric with a threshold")]


ABSOLUTE = re.compile(r"\b(never|always|100\s*%|all cases|every case|zero)\b", re.I)
TOLERANCE = re.compile(r"\d+\s*%|\bn\s*=\s*\d+|\brate\b|\bp\d{2}\b|\bthreshold\b|\bper \d|\b\d+\s*(of|in)\s*\d+", re.I)


@check("check_absolute_tolerance")
def _tolerance(doc: Doc, prof: str):
    out = []
    for i, text in doc.requirement_lines():
        if not ABSOLUTE.search(text):
            continue
        window = text + "\n" + doc.lookahead(i, 2)
        if TOLERANCE.search(window):
            continue
        out.append(Finding("SL-06.5", "absolute claim with no measured tolerance behind it", i, excerpt(text)))
    return out


MODEL_ASSUMPTION = re.compile(
    r"validated (on|against)|model version|\bre-?run the eval|on any model (change|upgrade)|"
    r"\bmodel\s*[:=]|behaviou?r not guaranteed|pinned model", re.I)


@check("check_model_assumptions")
def _model(doc: Doc, prof: str):
    if MODEL_ASSUMPTION.search(doc.body):
        return []
    return [Finding("SL-06.6", "no model assumption recorded and no re-validation trigger on model change")]


# --- Case 07 --------------------------------------------------------------------------

TRUST_WORDS = ["untrusted", "trust boundary", "not commands", "never commands", "data, never",
               "instructions come only", "treat as data", "prompt injection", "data to analyze",
               "not instructions", "as evidence, never"]


@check("check_trust_boundary")
def _trust(doc: Doc, prof: str):
    if kw(doc.body, TRUST_WORDS):
        return []
    return [Finding("SL-07.1", "no trust boundary: the spec never says which inputs are instructions and which are data")]


GROUNDING_WORDS = ["answer only from", "grounded", "grounding", "cite", "citation", "provenance",
                   "passage id", "source for each", "abstain when", "do not use your own knowledge",
                   "only from the provided", "retrieved passages"]


@check("check_grounding_policy")
def _grounding(doc: Doc, prof: str):
    if kw(doc.body, GROUNDING_WORDS):
        return []
    return [Finding("SL-07.2", "no grounding policy: nothing says whether the model may answer from its own knowledge")]


# --- Case 08 --------------------------------------------------------------------------

ACTION_WORDS = ["reversible", "irreversible", "confirmation", "confirm before", "idempoten",
                "least privilege", "destructive", "dry run", "undo", "rollback", "requires approval"]


@check("check_action_classification")
def _actions(doc: Doc, prof: str):
    hits = [w for w in ACTION_WORDS if w in doc.body.lower()]
    if len(set(hits)) >= 2:
        return []
    return [Finding("SL-08.1", "actions are not classified by consequence: no reversibility, confirmation, or idempotency stance")]


BUDGET_WORDS = ["budget", "tool call", "max steps", "maximum steps", "iterations", "timeout",
                "time limit", "token limit", "rate limit", "attempts", "retries", "wall clock"]


@check("check_resource_budget")
def _budget(doc: Doc, prof: str):
    low = doc.body.lower()
    if any(w in low for w in BUDGET_WORDS) and re.search(r"\d", doc.body):
        return []
    return [Finding("SL-08.2", "no resource budget: nothing bounds tool calls, steps, time, or tokens")]


# --- Case 09 --------------------------------------------------------------------------

VERSION_PAT = re.compile(r"^\s*(version|spec version)\s*[:=]\s*\S|^\s*#.*\bv\d+(\.\d+)*\b|\bversion\s+\d+(\.\d+)*\b", re.I | re.M)


@check("check_version_supersedes")
def _version(doc: Doc, prof: str):
    if VERSION_PAT.search(doc.body):
        return []
    return [Finding("SL-09.1", "no version marker: nothing identifies which revision of this spec binds")]


@check("check_length")
def _length(doc: Doc, prof: str):
    n = doc.word_count()
    if n <= 2000:
        return []
    return [Finding("SL-09.2", f"{n} words: past the point where a reader or a model holds the whole spec")]


@check("check_constraint_position")
def _position(doc: Doc, prof: str):
    sec = doc.find_section("constraints")
    if sec is None or doc.total_lines < 40:
        return []
    cutoff = doc.total_lines / 3
    if sec.start <= cutoff:
        return []
    return [Finding("SL-09.3", f"constraints start at line {sec.start} of {doc.total_lines}, past the first third", sec.start, excerpt(sec.title))]


@check("check_tradeoffs")
def _tradeoffs(doc: Doc, prof: str):
    if doc.find_section("tradeoffs"):
        return []
    if kw(doc.body, ["we rejected", "alternative considered", "alternatives considered",
                     "traded away", "weakness we accept", "cost of this choice", "instead of"]):
        return []
    return [Finding("SL-09.4", "no stated tradeoff: nothing names a rejected alternative or the weakness accepted")]


# --------------------------------------------------------------------------------------
# engine
# --------------------------------------------------------------------------------------

def load_registry(path: Path = REGISTRY) -> dict:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"No rule registry at {path}")
    except json.JSONDecodeError as e:
        raise SystemExit(f"Rule registry at {path} is not valid JSON: {e}")


def run(doc: Doc, reg: dict, profile: str) -> dict:
    per_rule = {}
    for rule in reg["rules"]:
        rid = rule["id"]
        status = rule["profiles"].get(profile, "off")
        if status == "off" or rule["layer"] != "form":
            continue
        if rid in doc.ignore_file:
            continue
        fn = CHECKS.get(rule.get("check_fn", ""))
        if fn is None:
            continue
        found = [f for f in fn(doc, profile)
                 if not (f.line and rid in doc.ignore_line.get(f.line, set()))]
        per_rule[rid] = found

    gates_red = [r for r in reg["rules"]
                 if r["id"] in per_rule and r["profiles"][profile] == "gate" and per_rule[r["id"]]]

    cases = {}
    for rule in reg["rules"]:
        rid = rule["id"]
        if rid not in per_rule:
            continue
        c = cases.setdefault(rule["case"], {"earned": 0, "possible": 0, "red": 0})
        c["possible"] += rule["weight"]
        if per_rule[rid]:
            c["red"] += 1
        else:
            c["earned"] += rule["weight"]

    earned = sum(c["earned"] for c in cases.values())
    possible = sum(c["possible"] for c in cases.values())
    review = [r for r in reg["rules"]
              if r["layer"] == "judgment" and r["profiles"].get(profile, "off") != "off"
              and r["id"] not in doc.ignore_file]

    return {"per_rule": per_rule, "gates_red": gates_red, "cases": cases,
            "earned": earned, "possible": possible, "review": review}


# --------------------------------------------------------------------------------------
# reporting
# --------------------------------------------------------------------------------------

def infer_profile(doc: Doc) -> str:
    if doc.declared_profile in ("product", "agent", "eval"):
        return doc.declared_profile
    low = doc.body.lower()
    eval_hits = sum(low.count(w) for w in ("rubric", "gold set", "judge", "eval set", "scoring"))
    agent_hits = sum(low.count(w) for w in ("agent", "tool call", "system prompt", "retrieved", "prompt"))
    if eval_hits >= 3 and eval_hits > agent_hits:
        return "eval"
    if agent_hits >= 3:
        return "agent"
    return "product"


def report_text(doc: Doc, reg: dict, profile: str, res: dict, quiet: bool) -> str:
    by_id = {r["id"]: r for r in reg["rules"]}
    case_title = {c["id"]: c["title"] for c in reg["cases"]}
    out = []
    gate = "FAIL" if res["gates_red"] else "PASS"
    out.append(f"calm-spec {VERSION}   rules {reg['pack_version']}   profile: {profile}   "
               f"{doc.word_count():,} words   {Path(doc.path).name}")
    out.append("")
    red = len(res["gates_red"])
    out.append(f"GATE:  {gate}" + (f"   {red} hard gate(s) red" if red else "   all hard gates green"))
    out.append(f"SCORE: {res['earned']}/{res['possible']} (derived from the rule registry, form layer only)")
    out.append("")

    order = {"gate": 0, "advisory": 1}
    rules_with = [(rid, f) for rid, f in res["per_rule"].items() if f]
    rules_with.sort(key=lambda kv: (order[by_id[kv[0]]["profiles"][profile]], kv[0]))

    if not rules_with:
        out.append("No form findings.")
    for rid, found in rules_with:
        rule = by_id[rid]
        tag = "RED " if rule["profiles"][profile] == "gate" else "WARN"
        if quiet and tag == "WARN":
            continue
        head = f"{tag} {rid}  {rule['name']}"
        if len(found) > 1:
            head += f"   ({len(found)} findings)"
        out.append(head)
        for f in found[:MAX_FINDINGS_PER_RULE]:
            loc = f"L{f.line}" if f.line else "  "
            out.append(f"     {loc:>6}  {f.detail}")
            if f.excerpt:
                out.append(f'             "{f.excerpt}"')
        if len(found) > MAX_FINDINGS_PER_RULE:
            out.append(f"             and {len(found) - MAX_FINDINGS_PER_RULE} more")
        out.append(f"       fix: {rule['fix']}")
        out.append("")

    out.append("Per case (earned/possible, form layer):")
    for cid in sorted(res["cases"]):
        c = res["cases"][cid]
        bar = "green" if c["red"] == 0 else f"{c['red']} rule(s) red"
        out.append(f"  {cid}  {case_title[cid]:<46} {c['earned']:>2}/{c['possible']:<2}  {bar}")
    out.append("")

    if res["review"]:
        out.append(f"Judgment layer, {len(res['review'])} rule(s) this script cannot decide:")
        for r in res["review"]:
            out.append(f"  {r['id']}  {r['name']}")
        out.append("  These need a reader. They carry no weight in the score above.")
    return "\n".join(out)


def report_json(doc: Doc, reg: dict, profile: str, res: dict) -> str:
    by_id = {r["id"]: r for r in reg["rules"]}
    payload = {
        "tool": "calm-spec", "version": VERSION, "pack_version": reg["pack_version"],
        "file": doc.path, "profile": profile, "words": doc.word_count(),
        "gate": "fail" if res["gates_red"] else "pass",
        "score": {"earned": res["earned"], "possible": res["possible"], "derived": True},
        "cases": res["cases"],
        "findings": [
            {"rule": rid, "name": by_id[rid]["name"], "case": by_id[rid]["case"],
             "severity": by_id[rid]["profiles"][profile], "fix": by_id[rid]["fix"],
             "hits": [{"line": f.line, "detail": f.detail, "excerpt": f.excerpt} for f in found]}
            for rid, found in sorted(res["per_rule"].items()) if found
        ],
        "review_rules": [{"id": r["id"], "name": r["name"], "check": r["check"], "fix": r["fix"],
                          "judgment": r.get("judgment", "")}
                         for r in res["review"]],
    }
    return json.dumps(payload, indent=2)


def main() -> None:
    ap = argparse.ArgumentParser(description="Grade a Markdown spec against the calm-spec rule pack.")
    ap.add_argument("input", nargs="?", type=Path, help="Path to the Markdown spec.")
    ap.add_argument("--profile", choices=["product", "agent", "eval"], help="Rule profile. Inferred when omitted.")
    ap.add_argument("--json", action="store_true", help="Machine-readable output.")
    ap.add_argument("--quiet", action="store_true", help="Print red gates only.")
    ap.add_argument("--gate-only", action="store_true", help="Print PASS or FAIL and nothing else.")
    ap.add_argument("--list-rules", action="store_true", help="Print the rule registry and exit.")
    ap.add_argument("--rules", type=Path, default=REGISTRY, help="Path to rules.json.")
    args = ap.parse_args()

    reg = load_registry(args.rules)

    if args.list_rules:
        for c in reg["cases"]:
            print(f"\nCase {c['id']}: {c['title']}\n  test: {c['one_question_test']}")
            for r in reg["rules"]:
                if r["case"] == c["id"]:
                    profs = ",".join(f"{k}={v}" for k, v in r["profiles"].items())
                    print(f"    {r['id']:<10} [{r['layer']:<8} w{r['weight']}] {r['name']}\n"
                          f"               {profs}")
        return

    if args.input is None:
        ap.error("an input file is required unless --list-rules is given")
    if not args.input.is_file():
        raise SystemExit(f"No such file: {args.input}")

    doc = Doc.load(args.input)
    profile = args.profile or infer_profile(doc)
    res = run(doc, reg, profile)

    if args.gate_only:
        print("FAIL" if res["gates_red"] else "PASS")
    elif args.json:
        print(report_json(doc, reg, profile, res))
    else:
        print(report_text(doc, reg, profile, res, args.quiet))

    sys.exit(1 if res["gates_red"] else 0)


if __name__ == "__main__":
    main()
