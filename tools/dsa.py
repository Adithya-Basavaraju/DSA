#!/usr/bin/env python3
"""dsa: progress tracker for the pattern-first DSA plan.

Cycle per pattern:  learn (invariant) -> variants + recognition drill -> solve problems
                    -> cold implementation -> edge cases  => "usable", then start the next one.
Spaced reviews come due at D+1, D+3, D+7, D+14 after a pattern is started; passing
D+7 and D+14 marks it "mastered".

Run `./dsa help` for commands. Standard library only (Python 3.9+).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TRACKER = ROOT / "tracker"
CURRICULUM = TRACKER / "curriculum.json"
STATE = TRACKER / "state.json"
ATTEMPTS = TRACKER / "attempts.csv"
DRILLS = TRACKER / "drills.csv"
REVIEWS = TRACKER / "reviews.csv"
PATTERNS_DIR = ROOT / "patterns"
ROADMAP = ROOT / "roadmap.md"
DASH_TEMPLATE = ROOT / "tools" / "dashboard_template.html"
DASH_OUT = ROOT / "dashboard" / "index.html"

ATTEMPT_COLS = ["date", "problem", "pattern", "variant", "difficulty", "mins", "result", "errors", "note"]
DRILL_COLS = ["date", "pattern", "correct", "total", "confusions", "note"]
REVIEW_COLS = ["date", "pattern", "stage", "result", "note"]

RESULTS = {
    "clean": "solved on my own",
    "hint": "solved after hints",
    "peeked": "looked at the solution",
    "unsolved": "did not finish",
}
SOLVED = {"clean", "hint"}
ERROR_TYPES = {"R": "Recognition", "I": "Invariant", "C": "Coding", "E": "Edge case", "X": "Complexity"}
GATES = [
    ("invariant", "Invariant", "state what must stay true, in 1-2 sentences (checked with Claude)"),
    ("recognition", "Recognition", "score >= 80% on a recognition drill (auto from `dsa drill`)"),
    ("application", "Application", "solve an unseen Medium/Hard on your own (auto from `dsa log ... clean`)"),
    ("cold", "Cold impl", "write the primitive from a blank file, no notes"),
    ("edges", "Edge cases", "come up with 3+ adversarial test cases yourself"),
]
GATE_IDS = [g[0] for g in GATES]
AUTO_GATES = {"recognition", "application"}
STAGES = [1, 3, 7, 14]
TARGET_MINS = {"E": 15, "M": 30, "H": 45}
DIFF_NAMES = {"E": "Easy", "M": "Medium", "H": "Hard"}
SMALL_WORDS = {"a", "an", "and", "at", "by", "for", "from", "in", "of", "on", "or", "the", "to", "with"}
ROMAN = {"Ii": "II", "Iii": "III", "Iv": "IV", "Bst": "BST", "Ipo": "IPO", "Cpu": "CPU", "3sum": "3Sum"}

# ---------------------------------------------------------------- output helpers

_COLOR = sys.stdout.isatty() and not os.environ.get("NO_COLOR")


def _c(code: str, s: str) -> str:
    return f"\033[{code}m{s}\033[0m" if _COLOR else s


def bold(s):
    return _c("1", s)


def dim(s):
    return _c("2", s)


def green(s):
    return _c("32", s)


def yellow(s):
    return _c("33", s)


def red(s):
    return _c("31", s)


def cyan(s):
    return _c("36", s)


def die(msg: str):
    print(red(f"error: {msg}"), file=sys.stderr)
    sys.exit(1)


def today() -> dt.date:
    override = os.environ.get("DSA_TODAY")
    return dt.date.fromisoformat(override) if override else dt.date.today()


def parse_date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def fmt_date(d: dt.date) -> str:
    return d.strftime("%a %d %b")


# ---------------------------------------------------------------- data loading


def titleize(slug: str) -> str:
    words = slug.split("-")
    out = []
    for i, w in enumerate(words):
        if i > 0 and w in SMALL_WORDS:
            out.append(w)
        else:
            t = w[:1].upper() + w[1:]
            out.append(ROMAN.get(w, ROMAN.get(t, t)))
    return " ".join(out)


def problem_url(slug: str) -> str:
    return f"https://leetcode.com/problems/{slug}/"


def read_csv(path: Path) -> list:
    if not path.exists():
        return []
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def append_csv(path: Path, cols: list, row: dict):
    new = not path.exists() or path.stat().st_size == 0
    with path.open("a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        if new:
            w.writeheader()
        w.writerow({k: row.get(k, "") for k in cols})


class DB:
    def __init__(self):
        data = json.loads(CURRICULUM.read_text())
        self.stage_text = data.get("review_stages", {})
        self.patterns = data["patterns"]
        for p in self.patterns:
            p["problems"] = [
                {"slug": s, "diff": d, "variant": v, "title": titleize(s)} for s, d, v in p["problems"]
            ]
        self.by_id = {p["id"]: p for p in self.patterns}
        self.problem_index = {}
        for p in self.patterns:
            for pr in p["problems"]:
                self.problem_index[pr["slug"]] = (p, pr)
        self.state = json.loads(STATE.read_text()) if STATE.exists() else {}
        self.state.setdefault("patterns", {})
        self.state.setdefault("timers", {})
        self.attempts = read_csv(ATTEMPTS)
        self.drills = read_csv(DRILLS)
        self.reviews = read_csv(REVIEWS)

    def save_state(self):
        STATE.write_text(json.dumps(self.state, indent=2) + "\n")

    # -- lookup

    def pattern(self, key: str) -> dict:
        key = key.strip().lower()
        if key.isdigit() and 1 <= int(key) <= len(self.patterns):
            return self.patterns[int(key) - 1]
        if key in self.by_id:
            return self.by_id[key]
        hits = [p for p in self.patterns if key in p["id"]]
        if len(hits) == 1:
            return hits[0]
        if not hits:
            die(f"no pattern matches '{key}'. Try `dsa list`.")
        die(f"'{key}' is ambiguous: {', '.join(p['id'] for p in hits)}")

    def folder(self, p: dict) -> Path:
        return PATTERNS_DIR / f"{p['num']:02d}-{p['id']}"

    # -- per-pattern derived state

    def started(self, pid: str):
        s = self.state["patterns"].get(pid, {}).get("started")
        return parse_date(s) if s else None

    def gates(self, pid: str) -> dict:
        """gate id -> ISO date passed. Includes automatic gates and retention."""
        out = dict(self.state["patterns"].get(pid, {}).get("gates", {}))
        if "recognition" not in out:
            for d in self.drills:
                if d["pattern"] == pid and int(d["total"]) and int(d["correct"]) / int(d["total"]) >= 0.8:
                    out["recognition"] = d["date"]
                    break
        if "application" not in out:
            for a in self.attempts:
                if a["pattern"] == pid and a["result"] == "clean" and a["difficulty"] in ("M", "H"):
                    out["application"] = a["date"]
                    break
        passed, _, _ = self.review_progress(pid)
        if 7 in passed and 14 in passed:
            out["retention"] = passed[14]
        return out

    def status(self, pid: str) -> str:
        if not self.started(pid):
            return "not started"
        g = self.gates(pid)
        if all(x in g for x in GATE_IDS):
            return "mastered" if "retention" in g else "usable"
        return "learning"

    def review_progress(self, pid: str):
        """Returns (passed stages {stage: date}, next stage or None, due date or None)."""
        start = self.started(pid)
        if not start:
            return {}, None, None
        passed = {}
        last = None
        for r in self.reviews:
            if r["pattern"] != pid:
                continue
            last = r["date"]
            if r["result"] == "pass":
                passed[int(r["stage"])] = r["date"]
        nxt = next((s for s in STAGES if s not in passed), None)
        if nxt is None:
            return passed, None, None
        due = start + dt.timedelta(days=nxt)
        if last:
            due = max(due, parse_date(last) + dt.timedelta(days=1))
        return passed, nxt, due

    def attempts_for(self, pid: str) -> list:
        return [a for a in self.attempts if a["pattern"] == pid]

    def solved_slugs(self, pid=None) -> set:
        return {a["problem"] for a in self.attempts if a["result"] in SOLVED and (pid is None or a["pattern"] == pid)}

    def covered_variants(self, pid: str) -> set:
        return {a["variant"] for a in self.attempts_for(pid) if a["result"] in SOLVED and a["variant"]}

    def suggestions(self, p: dict, n: int = 3) -> list:
        solved = self.solved_slugs(p["id"])
        covered = self.covered_variants(p["id"])
        todo = [pr for pr in p["problems"] if pr["slug"] not in solved]
        order = {"E": 0, "M": 1, "H": 2}
        prio = {v["name"]: v["priority"] for v in p["variants"]}
        prank = {"core": 0, "important": 1, "stretch": 2}
        todo.sort(key=lambda pr: (pr["variant"] in covered, prank.get(prio.get(pr["variant"]), 1), order[pr["diff"]]))
        return todo[:n]

    def redo_queue(self) -> list:
        """Problems whose latest attempt was not solved, or was solved only with hints/peeking."""
        latest = {}
        for a in self.attempts:
            latest[a["problem"]] = a
        return [a for a in latest.values() if a["result"] != "clean"]

    def activity_days(self) -> Counter:
        days = Counter()
        for rows in (self.attempts, self.drills, self.reviews):
            for r in rows:
                days[r["date"]] += 1
        for ps in self.state["patterns"].values():
            if ps.get("started"):
                days[ps["started"]] += 1
        return days

    def streak(self) -> int:
        days = set(self.activity_days())
        d = today()
        if d.isoformat() not in days:
            d -= dt.timedelta(days=1)
        n = 0
        while d.isoformat() in days:
            n += 1
            d -= dt.timedelta(days=1)
        return n


# ---------------------------------------------------------------- templates

NOTES_TMPL = """# {num:02d} · {name}

> Write this in YOUR words during the learn phase. Claude checks it, not writes it.
> Reference: `./dsa show {id}` (variants + signals), reference/deep-research-report.md

## Core idea
<!-- What problem does this technique make cheap? What's the brute force it replaces? -->


## Invariant
<!-- One or two sentences: what stays true at every step? This is the `invariant` gate. -->
>

## Variants I identified
<!-- List them yourself FIRST, then compare with `./dsa show {id}` and add what you missed. -->
-

## Recognition signals
<!-- Which wording or constraints in a problem should make me think of this? -->
-

## Closest competing pattern
<!-- Which pattern "almost works", and what property decides between them? -->


## Template
<!-- Keep the canonical code in primitive.py. Note the moving parts here. -->


## Pitfalls / edge cases
-

## Complexity

"""

PRIMITIVE_TMPL = '''"""{num:02d} · {name}: core primitives.

Write these yourself once you understand the pattern. Later, reproduce them from a
BLANK file with `./dsa cold {id}` (no peeking at this file).

To write:
{prims}
"""
'''

PROBLEM_TMPL = '''"""
{title} ({diff_name}): {url}
Pattern: {num:02d} {pid} | Variant: {variant}
Started: {date}

Answer these BEFORE coding (they are what makes the pattern stick):
  Brute force:
  Signal that pointed to the pattern:
  State / invariant I maintain:
  Nearby pattern that almost works, and why it doesn't:
  Time / space:
"""
from typing import *


class Solution:
    pass


if __name__ == "__main__":
    s = Solution()
    # Add at least 3 adversarial cases: empty / single element / duplicates / negatives / max size
    # assert s.method(...) == ...
    print("ok")
'''

COLD_TMPL = '''"""
COLD IMPLEMENTATION: {num:02d} · {name}  ({date})
No notes, no autocomplete, no looking at primitive.py or old solutions.

Write from scratch:
{prims}

Then add tests below, run it, and record the result:
  ./dsa gate {id} cold            (first time: passes the cold gate)
  ./dsa review {id} pass|fail     (when a spaced review is due)
"""
'''


def write_if_missing(path: Path, content: str) -> bool:
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return True


# ---------------------------------------------------------------- rendering helpers


def gate_line(db: DB, pid: str) -> str:
    g = db.gates(pid)
    parts = []
    for gid, label, _ in GATES:
        parts.append(green(f"✓ {label}") if gid in g else dim(f"· {label}"))
    parts.append(green("✓ Retention") if "retention" in g else dim("· Retention"))
    return "  ".join(parts)


def next_step(db: DB, p: dict) -> str:
    g = db.gates(p["id"])
    pid = p["id"]
    folder = db.folder(p).relative_to(ROOT)
    if "invariant" not in g:
        return (f"{bold('LEARN')} (30-45 min): ask Claude \"teach me {p['name']}\"; write {folder}/notes.md "
                f"in your own words.\n      When you can state the invariant: {cyan(f'./dsa gate {pid} invariant')}")
    if "recognition" not in g:
        return (f"{bold('VARIANTS + RECOGNITION')}: list the variants in notes.md, compare with "
                f"{cyan(f'./dsa show {pid}')}, then ask Claude for a recognition drill.\n"
                f"      Log the score: {cyan(f'./dsa drill {pid} 8/10')}")
    if "application" not in g:
        return (f"{bold('SOLVE')}: work through the problems below. {cyan('./dsa new <problem>')} -> solve -> "
                f"{cyan('./dsa log <problem> clean|hint|peeked|unsolved')}\n"
                f"      The gate passes on your first clean Medium/Hard.")
    if "cold" not in g:
        return f"{bold('COLD')}: {cyan(f'./dsa cold {pid}')}, write the primitive from a blank file, then {cyan(f'./dsa gate {pid} cold')}"
    if "edges" not in g:
        return (f"{bold('EDGE CASES')}: write 3+ adversarial tests (empty, single, duplicates, extremes...) "
                f"and have Claude check them. Then {cyan(f'./dsa gate {pid} edges')}")
    return green("All gates passed. Keep covering variants, or start the next pattern.")


def next_pattern(db: DB):
    return next((p for p in db.patterns if not db.started(p["id"])), None)


def regen_roadmap(db: DB):
    lines = [
        "# Roadmap",
        "",
        "_Auto-generated by `./dsa` after every change. Don't edit by hand._",
        "",
        f"Updated {today().isoformat()} · streak {db.streak()} day(s) · "
        f"{len(db.solved_slugs())} problems solved · "
        f"{sum(1 for p in db.patterns if db.status(p['id']) in ('usable', 'mastered'))}/{len(db.patterns)} patterns usable",
        "",
        "Gates: **I**nvariant · **R**ecognition · **A**pplication · **C**old implementation · **E**dge cases · "
        "**T** retention (D+7 and D+14 reviews passed)",
        "",
        "Status: ⬜ not started · 🟨 learning · 🟩 usable · ⭐ mastered",
        "",
    ]
    icon = {"not started": "⬜", "learning": "🟨", "usable": "🟩", "mastered": "⭐"}
    area = None
    for p in db.patterns:
        if p["area"] != area:
            area = p["area"]
            lines += ["", f"## {area}", "", "| # | Pattern | Status | I R A C E T | Solved | Variants | Next review |",
                      "|---|---|---|---|---|---|---|"]
        pid = p["id"]
        g = db.gates(pid)
        marks = " ".join("✓" if x in g else "·" for x in GATE_IDS + ["retention"])
        solved = len(db.solved_slugs(pid) & {pr["slug"] for pr in p["problems"]})
        cov = len(db.covered_variants(pid))
        _, stage, due = db.review_progress(pid)
        rev = f"D+{stage} {due.isoformat()}" if due else ("done" if db.started(pid) else "")
        link = f"[{p['name']}](patterns/{p['num']:02d}-{pid}/notes.md)" if db.started(pid) else p["name"]
        st = db.status(pid)
        lines.append(f"| {p['num']} | {link} | {icon[st]} {st} | `{marks}` | {solved}/{len(p['problems'])} | "
                     f"{cov}/{len(p['variants'])} | {rev} |")
    redo = db.redo_queue()
    if redo:
        lines += ["", "## Redo queue", "", "Problems whose latest attempt wasn't a clean solve:", ""]
        for a in redo:
            lines.append(f"- [{titleize(a['problem'])}]({problem_url(a['problem'])}) ({a['pattern']}, {a['result']}"
                         f"{', errors ' + a['errors'] if a['errors'] else ''})")
    ROADMAP.write_text("\n".join(lines) + "\n")


# ---------------------------------------------------------------- commands


def cmd_today(db: DB, args):
    t = today()
    started = [p for p in db.patterns if db.started(p["id"])]
    first = min((db.started(p["id"]) for p in started), default=None)
    day = f"day {(t - first).days + 1}" if first else "day 0"
    print(bold(f"DSA · {fmt_date(t)} · {day} · streak {db.streak()}"))
    print(dim(f"{len(db.solved_slugs())} problems solved · {len(db.attempts)} attempts · "
              f"{sum(1 for p in db.patterns if db.status(p['id']) in ('usable', 'mastered'))}/26 patterns usable"))
    print()

    learning = [p for p in started if db.status(p["id"]) == "learning"]
    if not learning:
        nxt = next_pattern(db)
        if nxt is None:
            print(green("Every pattern is started. Keep up the reviews and the redo queue."))
        else:
            print(bold("NEXT PATTERN"), f"{nxt['num']:02d} {nxt['name']}")
            print(f"  Start it: {cyan('./dsa start ' + nxt['id'])}  (creates notes, primitive and problem files, and schedules reviews)")
    for p in learning:
        pid = p["id"]
        cov = db.covered_variants(pid)
        print(bold(f"NOW  {p['num']:02d} {p['name']}"), dim(f"(started {fmt_date(db.started(pid))})"))
        print("  " + gate_line(db, pid))
        print(f"  Variants covered: {len(cov)}/{len(p['variants'])}")
        print("  Next: " + next_step(db, p))
        sugg = db.suggestions(p)
        if sugg and "invariant" in db.gates(pid):
            print("  Problems:")
            for pr in sugg:
                tag = "" if pr["variant"] in cov else yellow(" (new variant)")
                print(f"    - {pr['title']} [{pr['diff']}] · {pr['variant']}{tag}  {dim(pr['slug'])}")
        print()

    due, upcoming = [], []
    for p in started:
        _, stage, d = db.review_progress(p["id"])
        if d is None:
            continue
        (due if d <= t else upcoming).append((d, stage, p))
    print(bold("REVIEWS DUE") if due else dim("No reviews due today."))
    for d, stage, p in sorted(due, key=lambda x: x[0]):
        late = (t - d).days
        late_s = red(f" ({late}d overdue)") if late > 0 else ""
        pid = p["id"]
        print(f"  - {p['num']:02d} {p['name']}: D+{stage}, {db.stage_text.get(str(stage), '')}{late_s}")
        print(f"      {cyan(f'./dsa cold {pid}')} -> then {cyan(f'./dsa review {pid} pass|fail')}")
    soon = sorted(x for x in upcoming if (x[0] - t).days <= 3)
    if soon:
        print(dim("  Coming up: " + ", ".join(f"{p['id']} D+{s} {d.strftime('%a')}" for d, s, p in soon)))

    redo = db.redo_queue()
    if redo:
        print()
        print(bold("REDO QUEUE"), dim(f"({len(redo)}) problems you haven't solved cleanly yet; retry after a few days"))
        for a in redo[:5]:
            print(f"  - {titleize(a['problem'])} ({a['pattern']}, last: {a['result']})")


def cmd_start(db: DB, args):
    p = db.pattern(args.pattern)
    pid = p["id"]
    if db.started(pid):
        print(yellow(f"{p['name']} was already started on {db.started(pid)}."))
        return
    blocking = [q for q in db.patterns if db.started(q["id"]) and db.status(q["id"]) == "learning"]
    if blocking and not args.force:
        names = ", ".join(q["id"] for q in blocking)
        die(f"mastery gate: finish the gates for {names} first (see `./dsa today`), or use --force.")
    when = parse_date(args.date) if args.date else today()
    db.state["patterns"].setdefault(pid, {})["started"] = when.isoformat()
    db.state["patterns"][pid].setdefault("gates", {})
    db.save_state()
    folder = db.folder(p)
    prims = "\n".join(f"  - {x}" for x in p["primitives"])
    write_if_missing(folder / "notes.md", NOTES_TMPL.format(**p))
    write_if_missing(folder / "primitive.py", PRIMITIVE_TMPL.format(prims=prims, **p))
    (folder / "problems").mkdir(parents=True, exist_ok=True)
    regen_roadmap(db)
    print(green(f"Started {p['num']:02d} {p['name']} on {fmt_date(when)}."))
    print(f"  Folder: {folder.relative_to(ROOT)}/")
    print("  Reviews scheduled: " + ", ".join(f"D+{s} {fmt_date(when + dt.timedelta(days=s))}" for s in STAGES))
    print(f"  Next: ask Claude \"teach me {p['name']}\" and fill in notes.md as you go.")


def cmd_show(db: DB, args):
    p = db.pattern(args.pattern)
    pid = p["id"]
    print(bold(f"{p['num']:02d} {p['name']}"), dim(f"[{p['area']}] · {db.status(pid)}"))
    if db.started(pid):
        print("  " + gate_line(db, pid))
    print(bold("\nRecognition signals"))
    for s in p["signals"]:
        print(f"  - {s}")
    print(bold("\nPrimitives to own (cold)"))
    for s in p["primitives"]:
        print(f"  - {s}")
    cov = db.covered_variants(pid)
    solved = db.solved_slugs(pid)
    tried = {a["problem"]: a["result"] for a in db.attempts_for(pid)}
    print(bold("\nVariants & problems"))
    for v in p["variants"]:
        mark = green("✓") if v["name"] in cov else "·"
        print(f"  {mark} {v['name']} {dim('(' + v['priority'] + ')')}")
        for pr in p["problems"]:
            if pr["variant"] != v["name"]:
                continue
            if pr["slug"] in solved:
                st = green("solved")
            elif pr["slug"] in tried:
                st = yellow(tried[pr["slug"]])
            else:
                st = dim("todo")
            print(f"      [{pr['diff']}] {pr['title']:<52} {st}  {dim(pr['slug'])}")
    passed, stage, due = db.review_progress(pid)
    if db.started(pid):
        print(bold("\nReviews"), " ".join(green(f"D+{s}✓") if s in passed else dim(f"D+{s}") for s in STAGES),
              f" next: D+{stage} on {fmt_date(due)}" if due else "")


def resolve_problem(db: DB, raw: str, pattern_key=None):
    m = re.search(r"leetcode\.com/problems/([^/?#]+)", raw)
    slug = (m.group(1) if m else raw).strip().lower().strip("/")
    if pattern_key:
        p = db.pattern(pattern_key)
        pr = next((x for x in p["problems"] if x["slug"] == slug), None)
        return slug, p, pr
    if slug in db.problem_index:
        p, pr = db.problem_index[slug]
        return slug, p, pr
    return slug, None, None


def cmd_new(db: DB, args):
    slug, p, pr = resolve_problem(db, args.problem, args.pattern)
    if p is None:
        die(f"'{slug}' isn't in the curriculum. Add --pattern <id> (and optionally --variant/--diff).")
    diff = args.diff or (pr["diff"] if pr else "M")
    variant = args.variant or (pr["variant"] if pr else "")
    path = db.folder(p) / "problems" / f"{slug.replace('-', '_')}.py"
    created = write_if_missing(path, PROBLEM_TMPL.format(
        title=titleize(slug), diff_name=DIFF_NAMES[diff], url=problem_url(slug), num=p["num"], pid=p["id"],
        variant=variant or "?", date=today().isoformat()))
    db.state["timers"][slug] = dt.datetime.now().isoformat(timespec="minutes")
    db.save_state()
    print(("Created " if created else "Exists: ") + str(path.relative_to(ROOT)))
    print(f"  {problem_url(slug)}")
    print(dim(f"  Timer started. Target: {TARGET_MINS[diff]} min for {DIFF_NAMES[diff]}. When done: ./dsa log {slug} <result>"))


def cmd_log(db: DB, args):
    slug, p, pr = resolve_problem(db, args.problem, args.pattern)
    if p is None:
        die(f"'{slug}' isn't in the curriculum. Add --pattern <id> --diff E|M|H --variant '...'.")
    mins = args.mins
    timer = db.state["timers"].pop(slug, None)
    if mins is None and timer:
        elapsed = (dt.datetime.now() - dt.datetime.fromisoformat(timer)).total_seconds() / 60
        if elapsed <= 240:
            mins = round(elapsed)
        else:
            print(yellow(f"Timer for {slug} is {elapsed / 60:.1f}h old, so not using it. Pass --mins next time."))
    errors = ""
    if args.errors:
        letters = re.findall(r"[A-Za-z]", args.errors.upper())
        bad = [x for x in letters if x not in ERROR_TYPES]
        if bad:
            die(f"unknown error type(s) {bad}. Use R I C E X ({', '.join(f'{k}={v}' for k, v in ERROR_TYPES.items())}).")
        errors = ";".join(dict.fromkeys(letters))
    before = db.gates(p["id"])
    row = {
        "date": (parse_date(args.date) if args.date else today()).isoformat(),
        "problem": slug,
        "pattern": p["id"],
        "variant": args.variant or (pr["variant"] if pr else ""),
        "difficulty": args.diff or (pr["diff"] if pr else "M"),
        "mins": "" if mins is None else str(mins),
        "result": args.result,
        "errors": errors,
        "note": args.note or "",
    }
    append_csv(ATTEMPTS, ATTEMPT_COLS, row)
    db.attempts.append(row)
    db.save_state()
    regen_roadmap(db)
    t = f"{mins} min" if mins is not None else "no time"
    target = TARGET_MINS[row["difficulty"]]
    pace = "" if mins is None else (green(" (within target)") if mins <= target else yellow(f" (target {target})"))
    print(green(f"Logged {titleize(slug)}: {args.result}, {t}{pace}") + (f", errors {errors}" if errors else ""))
    if args.result != "clean" and not errors:
        print(yellow("  Tip: tag what went wrong with --errors (R=recognition I=invariant C=coding E=edge X=complexity) "
                     "and --note \"what exactly\". That's where the insights come from."))
    for gid in GATE_IDS:
        if gid in db.gates(p["id"]) and gid not in before:
            print(green(f"  🎉 Gate passed: {gid}"))
    cov = db.covered_variants(p["id"])
    print(dim(f"  {p['name']}: {len(cov)}/{len(p['variants'])} variants covered, "
              f"{len(db.solved_slugs(p['id']))} problems solved"))


def cmd_drill(db: DB, args):
    pid = "mixed" if args.pattern == "mixed" else db.pattern(args.pattern)["id"]
    m = re.fullmatch(r"(\d+)\s*/\s*(\d+)", args.score)
    if not m:
        die("score must look like 8/10")
    correct, total = int(m.group(1)), int(m.group(2))
    if total == 0 or correct > total:
        die("bad score")
    conf = []
    for c in args.confused or []:
        parts = re.split(r"[:>]", c, maxsplit=1)
        if len(parts) != 2:
            die("--confused takes expected:chosen, e.g. prefix-state:sliding-window")
        a, b = parts
        conf.append(f"{db.pattern(a)['id']}>{db.pattern(b)['id']}")
    before = db.gates(pid) if pid != "mixed" else {}
    row = {"date": today().isoformat(), "pattern": pid, "correct": correct, "total": total,
           "confusions": ";".join(conf), "note": args.note or ""}
    append_csv(DRILLS, DRILL_COLS, row)
    db.drills.append({k: str(v) for k, v in row.items()})
    regen_roadmap(db)
    print(green(f"Drill logged: {pid} {correct}/{total} ({100 * correct // total}%)"))
    if pid != "mixed" and "recognition" in db.gates(pid) and "recognition" not in before:
        print(green("  🎉 Gate passed: recognition"))
    elif pid != "mixed" and correct / total < 0.8:
        print(yellow("  Below 80%: review the signals (`./dsa show " + pid + "`) and drill again tomorrow."))


def cmd_review(db: DB, args):
    p = db.pattern(args.pattern)
    pid = p["id"]
    _, stage, due = db.review_progress(pid)
    if stage is None:
        die(f"all reviews for {pid} are already passed.")
    if due > today():
        print(yellow(f"Note: D+{stage} isn't due until {fmt_date(due)}. Logging it anyway (spacing works best when you wait)."))
    before = db.gates(pid)
    append_csv(REVIEWS, REVIEW_COLS, {"date": today().isoformat(), "pattern": pid, "stage": stage,
                                      "result": args.result, "note": args.note or ""})
    db.reviews.append({"date": today().isoformat(), "pattern": pid, "stage": str(stage), "result": args.result})
    regen_roadmap(db)
    if args.result == "pass":
        print(green(f"D+{stage} review passed for {p['name']}."))
    else:
        print(yellow(f"D+{stage} review failed for {p['name']}; it's due again tomorrow. "
                     "Note what broke with --note next time."))
    if "retention" in db.gates(pid) and "retention" not in before:
        print(green("  ⭐ Retention gate passed: pattern mastered!"))
    _, s2, d2 = db.review_progress(pid)
    if s2:
        print(dim(f"  Next: D+{s2} on {fmt_date(d2)}"))


def cmd_cold(db: DB, args):
    p = db.pattern(args.pattern)
    prims = "\n".join(f"  - {x}" for x in p["primitives"])
    path = db.folder(p) / "cold" / f"{today().isoformat()}.py"
    created = write_if_missing(path, COLD_TMPL.format(prims=prims, date=today().isoformat(), **p))
    print(("Created " if created else "Exists: ") + str(path.relative_to(ROOT)))
    print(dim("  Close notes.md and primitive.py. Timer's on you."))


def cmd_gate(db: DB, args):
    p = db.pattern(args.pattern)
    pid = p["id"]
    if args.gate not in GATE_IDS:
        die(f"gate must be one of {', '.join(GATE_IDS)}")
    if not db.started(pid):
        die(f"{pid} isn't started yet (`./dsa start {pid}`).")
    gates = db.state["patterns"][pid].setdefault("gates", {})
    if args.undo:
        if gates.pop(args.gate, None) is None:
            msg = " (it's automatic: it comes from drills/attempts)" if args.gate in AUTO_GATES else ""
            die(f"{args.gate} wasn't manually set{msg}.")
        print(yellow(f"Removed {args.gate} gate for {pid}."))
    else:
        gates[args.gate] = today().isoformat()
        print(green(f"✓ {args.gate} gate passed for {p['name']}."))
    db.save_state()
    regen_roadmap(db)
    if db.status(pid) == "usable" and not args.undo:
        nxt = next_pattern(db)
        print(green("  🟩 Pattern is now USABLE.") + (f" Next up: {cyan('./dsa start ' + nxt['id'])}" if nxt else ""))


def cmd_list(db: DB, args):
    icon = {"not started": dim("⬜"), "learning": "🟨", "usable": "🟩", "mastered": "⭐"}
    area = None
    for p in db.patterns:
        if p["area"] != area:
            area = p["area"]
            print(bold(area))
        st = db.status(p["id"])
        progress = f"{len(db.solved_slugs(p['id']))}/{len(p['problems'])}"
        print(f"  {icon[st]} {p['num']:02d} {p['id']:<20} {p['name']:<58} {dim(progress)}")


# ---------------------------------------------------------------- insights


def compute_insights(db: DB) -> dict:
    A = db.attempts
    mins = lambda a: int(a["mins"]) if a.get("mins") else None
    res = Counter(a["result"] for a in A)
    errs = Counter(e for a in A for e in a["errors"].split(";") if e)

    by_diff = {}
    for d in "EMH":
        rows = [a for a in A if a["difficulty"] == d]
        timed = [mins(a) for a in rows if a["result"] in SOLVED and mins(a) is not None]
        by_diff[d] = {
            "attempts": len(rows),
            "clean": sum(1 for a in rows if a["result"] == "clean"),
            "avg_mins": round(sum(timed) / len(timed), 1) if timed else None,
            "within_target": sum(1 for m in timed if m <= TARGET_MINS[d]),
            "timed": len(timed),
            "target": TARGET_MINS[d],
        }

    patterns = []
    for p in db.patterns:
        pid = p["id"]
        rows = db.attempts_for(pid)
        timed = [mins(a) for a in rows if mins(a) is not None]
        _, stage, due = db.review_progress(pid)
        patterns.append({
            "id": pid, "num": p["num"], "name": p["name"], "area": p["area"],
            "status": db.status(pid),
            "started": db.state["patterns"].get(pid, {}).get("started"),
            "gates": db.gates(pid),
            "attempts": len(rows),
            "clean": sum(1 for a in rows if a["result"] == "clean"),
            "solved": len(db.solved_slugs(pid)),
            "total_problems": len(p["problems"]),
            "variants_total": len(p["variants"]),
            "variants": [{"name": v["name"], "priority": v["priority"],
                          "covered": v["name"] in db.covered_variants(pid)} for v in p["variants"]],
            "errors": dict(Counter(e for a in rows for e in a["errors"].split(";") if e)),
            "avg_mins": round(sum(timed) / len(timed), 1) if timed else None,
            "next_review": {"stage": stage, "due": due.isoformat()} if due else None,
        })

    weak = [x for x in patterns if x["attempts"] >= 2]
    weak.sort(key=lambda x: (x["clean"] / x["attempts"], -sum(x["errors"].values())))
    weak = [x for x in weak if x["clean"] / x["attempts"] < 0.67][:5]

    conf = Counter(c for d in db.drills for c in d.get("confusions", "").split(";") if c)
    days = db.activity_days()
    daily_mins = Counter()
    for a in A:
        if mins(a):
            daily_mins[a["date"]] += mins(a)

    return {
        "generated": dt.datetime.now().isoformat(timespec="minutes"),
        "today": today().isoformat(),
        "streak": db.streak(),
        "totals": {
            "attempts": len(A),
            "solved": len(db.solved_slugs()),
            "clean_rate": round(res["clean"] / len(A), 3) if A else None,
            "hours": round(sum(mins(a) or 0 for a in A) / 60, 1),
            "usable": sum(1 for x in patterns if x["status"] in ("usable", "mastered")),
            "mastered": sum(1 for x in patterns if x["status"] == "mastered"),
            "patterns": len(patterns),
            "drills": len(db.drills),
            "reviews": len(db.reviews),
        },
        "results": dict(res),
        "errors": dict(errs),
        "error_names": ERROR_TYPES,
        "by_difficulty": by_diff,
        "patterns": patterns,
        "weak": [{"id": x["id"], "name": x["name"], "attempts": x["attempts"], "clean": x["clean"],
                  "errors": x["errors"]} for x in weak],
        "confusions": [{"expected": k.split(">")[0], "chosen": k.split(">")[1], "count": n} for k, n in conf.most_common(10)],
        "drills": [{"date": d["date"], "pattern": d["pattern"], "pct": round(int(d["correct"]) / int(d["total"]), 3)}
                   for d in db.drills],
        "activity": [{"date": d, "events": n, "mins": daily_mins.get(d, 0)} for d, n in sorted(days.items())],
        "redo": [{"problem": a["problem"], "title": titleize(a["problem"]), "pattern": a["pattern"],
                  "result": a["result"], "errors": a["errors"]} for a in db.redo_queue()],
        "recent_errors": [{"date": a["date"], "problem": titleize(a["problem"]), "pattern": a["pattern"],
                           "errors": a["errors"], "note": a["note"]} for a in A if a["note"] or a["errors"]][-10:][::-1],
    }


def cmd_stats(db: DB, args):
    ins = compute_insights(db)
    T = ins["totals"]
    if not T["attempts"] and not T["drills"]:
        print("No attempts logged yet. Solve something and `./dsa log` it, then come back.")
        return
    print(bold("OVERALL"))
    cr = f"{T['clean_rate'] * 100:.0f}%" if T["clean_rate"] is not None else "-"
    print(f"  {T['solved']} solved · {T['attempts']} attempts · clean-solve rate {cr} · {T['hours']}h logged · "
          f"streak {ins['streak']}d · {T['usable']}/{T['patterns']} usable, {T['mastered']} mastered")
    print(bold("\nRESULTS"))
    for k in RESULTS:
        n = ins["results"].get(k, 0)
        print(f"  {k:<9} {'█' * n} {n}")
    if ins["errors"]:
        print(bold("\nWHERE YOUR MISTAKES COME FROM"))
        tot = sum(ins["errors"].values())
        for k, n in sorted(ins["errors"].items(), key=lambda x: -x[1]):
            print(f"  {k} {ERROR_TYPES[k]:<12} {'█' * n} {n} ({100 * n // tot}%)")
        top = max(ins["errors"], key=ins["errors"].get)
        advice = {
            "R": "you're picking the wrong pattern. Ask Claude for more mixed (interleaved) recognition drills.",
            "I": "you know the pattern but break its rule. Restate the invariant before coding each problem.",
            "C": "the ideas are fine but the code isn't automatic yet. Do more cold rewrites of the primitives.",
            "E": "edge cases are slipping. Write 3 adversarial tests BEFORE coding.",
            "X": "complexity misses. State the target time/space from the constraints before choosing an approach.",
        }
        print(yellow(f"  → Biggest leak is {ERROR_TYPES[top]}: {advice[top]}"))
    print(bold("\nTIME BY DIFFICULTY") + dim("  (solved attempts with a time)"))
    for d, x in ins["by_difficulty"].items():
        if x["attempts"]:
            avg = f"{x['avg_mins']} min avg" if x["avg_mins"] is not None else "no times"
            print(f"  {DIFF_NAMES[d]:<7} {x['attempts']} attempts · {x['clean']} clean · {avg} · "
                  f"{x['within_target']}/{x['timed']} within {x['target']} min")
    active = [x for x in ins["patterns"] if x["attempts"]]
    if active:
        print(bold("\nBY PATTERN"))
        for x in active:
            e = " ".join(f"{k}{v}" for k, v in sorted(x["errors"].items()))
            print(f"  {x['num']:02d} {x['id']:<20} {x['clean']}/{x['attempts']} clean · "
                  f"variants {sum(v['covered'] for v in x['variants'])}/{x['variants_total']}"
                  f"{' · ' + str(x['avg_mins']) + ' min avg' if x['avg_mins'] else ''}{' · errors ' + e if e else ''}")
    if ins["weak"]:
        print(bold("\nWEAKEST PATTERNS"))
        for w in ins["weak"]:
            print(f"  - {w['name']}: {w['clean']}/{w['attempts']} clean")
    if ins["confusions"]:
        print(bold("\nPATTERNS YOU MIX UP") + dim("  (expected → what you picked)"))
        for c in ins["confusions"]:
            print(f"  - {c['expected']} → {c['chosen']} ×{c['count']}")
    if ins["recent_errors"]:
        print(bold("\nRECENT ERROR NOTES"))
        for r in ins["recent_errors"][:6]:
            print(f"  {r['date']} {r['problem']} [{r['errors'] or '-'}] {dim(r['note'])}")
    gaps = [(x, [v["name"] for v in x["variants"] if not v["covered"] and v["priority"] == "core"])
            for x in ins["patterns"] if x["status"] != "not started"]
    gaps = [(x, g) for x, g in gaps if g]
    if gaps:
        print(bold("\nUNTOUCHED CORE VARIANTS"))
        for x, g in gaps:
            print(f"  {x['id']}: {', '.join(g)}")


def cmd_dashboard(db: DB, args):
    if not DASH_TEMPLATE.exists():
        die(f"missing {DASH_TEMPLATE.relative_to(ROOT)}")
    data = json.dumps(compute_insights(db)).replace("</", "<\\/")
    html = DASH_TEMPLATE.read_text().replace("/*__DSA_DATA__*/null", data)
    DASH_OUT.parent.mkdir(exist_ok=True)
    DASH_OUT.write_text(html)
    print(green(f"Wrote {DASH_OUT.relative_to(ROOT)}"))
    print(dim("  Open locally: open dashboard/index.html, or ask Claude to publish/refresh it."))


def cmd_roadmap(db: DB, args):
    regen_roadmap(db)
    print(green(f"Regenerated {ROADMAP.relative_to(ROOT)}"))


# ---------------------------------------------------------------- CLI


HELP = f"""{bold('dsa')}: pattern-first DSA tracker

{bold('Daily')}
  ./dsa today                          what to do now: current pattern, next step, reviews due
  ./dsa stats                          insights: error types, timing, weak patterns, mix-ups
  ./dsa dashboard                      regenerate dashboard/index.html

{bold('Pattern cycle')}
  ./dsa start <pattern>                begin learning (creates notes and schedules D+1/3/7/14 reviews)
  ./dsa show <pattern>                 signals, primitives, variants, problems and your progress
  ./dsa new <problem>                  create a solution file and start the timer (slug or LeetCode URL)
  ./dsa log <problem> <result>         result: clean | hint | peeked | unsolved
        [--errors RC] [--note "..."] [--mins N] [--pattern id] [--variant "..."] [--diff E|M|H]
  ./dsa drill <pattern|mixed> 8/10     log a recognition drill [--confused expected:chosen ...]
  ./dsa cold <pattern>                 blank file for a from-memory implementation
  ./dsa review <pattern> pass|fail     record a due spaced review [--note "..."]
  ./dsa gate <pattern> <gate>          mark a gate passed: {', '.join(GATE_IDS)} [--undo]

{bold('Overview')}
  ./dsa list                           all 26 patterns and their status
  ./dsa roadmap                        regenerate roadmap.md

Error types: {', '.join(f'{k}={v}' for k, v in ERROR_TYPES.items())}
Patterns can be given by id, number or unique prefix: `two-pointers`, `2`, `slid`."""


def main(argv=None):
    ap = argparse.ArgumentParser(prog="dsa", add_help=False)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("today")
    sub.add_parser("help")
    sub.add_parser("list")
    sub.add_parser("stats")
    sub.add_parser("dashboard")
    sub.add_parser("roadmap")
    s = sub.add_parser("start"); s.add_argument("pattern"); s.add_argument("--force", action="store_true"); s.add_argument("--date")
    s = sub.add_parser("show"); s.add_argument("pattern")
    s = sub.add_parser("new"); s.add_argument("problem"); s.add_argument("--pattern"); s.add_argument("--variant"); s.add_argument("--diff", choices=list("EMH"))
    s = sub.add_parser("log")
    s.add_argument("problem"); s.add_argument("result", choices=list(RESULTS))
    s.add_argument("--mins", type=int); s.add_argument("--errors"); s.add_argument("--note")
    s.add_argument("--pattern"); s.add_argument("--variant"); s.add_argument("--diff", choices=list("EMH")); s.add_argument("--date")
    s = sub.add_parser("drill"); s.add_argument("pattern"); s.add_argument("score"); s.add_argument("--confused", action="append"); s.add_argument("--note")
    s = sub.add_parser("review"); s.add_argument("pattern"); s.add_argument("result", choices=["pass", "fail"]); s.add_argument("--note")
    s = sub.add_parser("cold"); s.add_argument("pattern")
    s = sub.add_parser("gate"); s.add_argument("pattern"); s.add_argument("gate"); s.add_argument("--undo", action="store_true")

    args = ap.parse_args(argv)
    if args.cmd in (None, "help"):
        print(HELP)
        return
    db = DB()
    {
        "today": cmd_today, "list": cmd_list, "stats": cmd_stats, "dashboard": cmd_dashboard,
        "roadmap": cmd_roadmap, "start": cmd_start, "show": cmd_show, "new": cmd_new, "log": cmd_log,
        "drill": cmd_drill, "review": cmd_review, "cold": cmd_cold, "gate": cmd_gate,
    }[args.cmd](db, args)


if __name__ == "__main__":
    main()
