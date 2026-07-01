#!/usr/bin/env python3
"""Deterministic mechanical verifier for TDD code against a Work Plan.

Runs the test suite, checks labeled coverage output, verifies every plan PR-ID
and every spec/design FR/AT/COMP/TEST is referenced by a named test, looks for
nearby assertions, and reports git diff/TDD evidence when available. These are
structural gates, not proof of semantic correctness. Exits 0 only when every
gate passes. No semantic judgment, reproducible.

Usage:
    python check_code.py --plan plan.md [--tests-argv '["pytest","-q"]']
                         [--tests "pytest -q"] [--tests-shell]
                         [--cov-min 80] [--tests-dir tests] [--src .]
                         [--max-loc 600] [--max-diff-loc 300]
                         [--diff-base <ref>] [--allow-missing-git-evidence]
                         [--allow-missing-tdd-evidence]
                         [--src-ext .py,.ts,.tsx,.js,.jsx]
                         [--spec spec.md] [--design design.md] [--json]
"""

from __future__ import annotations

import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path

SLUG_TOKEN = r"[A-Z][A-Z0-9]{1,31}"
PR = re.compile(rf"\bPR-{SLUG_TOKEN}-{SLUG_TOKEN}\b")
ID = re.compile(rf"\b(?:(?:FR|AT|TEST)-{SLUG_TOKEN}-{SLUG_TOKEN}|COMP-{SLUG_TOKEN})\b")
VALID_ANY = re.compile(
    rf"\b(?:(?:UN|FEAT|UC|FR|NFR|AT|TEST|MILE|WORK|PR)-"
    rf"{SLUG_TOKEN}-{SLUG_TOKEN}|"
    rf"(?:LAYER|COMP|IFACE|DEC|RISK)-{SLUG_TOKEN})\b"
)
ID_CANDIDATE = re.compile(
    r"\b(?:UN|FEAT|UC|FR|NFR|AT|TEST|MILE|WORK|PR|LAYER|COMP|IFACE|DEC|RISK)"
    r"(?:-[A-Za-z0-9]+)+\b",
    re.I,
)
SKIP = re.compile(r"\b(skip|skipif|xfail)\b", re.I)
VAGUE = re.compile(r"\b(TODO|FIXME|XXX|etc\.)\b", re.I)
COV_TOTAL = re.compile(r"(?im)^\s*TOTAL\b.*?(\d+(?:\.\d+)?)\s*%\s*$")
COV_LABEL = re.compile(
    r"(?im)^\s*(?:coverage|total coverage|line coverage)\s*[:=]\s*"
    r"(\d+(?:\.\d+)?)\s*%\s*$"
)
ASSERTION = re.compile(
    r"\b(assert|expect\(|should|toBe\(|toEqual\(|toStrictEqual\(|raises\(|"
    r"pytest\.raises|assertThat|XCTAssert|require\.|verify\()",
    re.I,
)
WEAK_ASSERTION = re.compile(
    r"\b(assert\s+true|expect\(\s*true\s*\)|assert\.ok\(\s*true\s*\)|"
    r"assertTrue\(\s*true\s*\)|XCTAssertTrue\(\s*true\s*\)|"
    r"assert\s+(?P<num>\d+(?:\.\d+)?)\s*==\s*(?P=num)|"
    r"assert\s+(?P<quote>['\"])(?P<text>.*?)(?P=quote)\s*==\s*"
    r"(?P=quote)(?P=text)(?P=quote)|"
    r"expect\(\s*(?P<expect_num>\d+(?:\.\d+)?)\s*\)\.to(?:Be|Equal)"
    r"\(\s*(?P=expect_num)\s*\))",
    re.I,
)
TDD_RED = re.compile(r"\b(red|failing test|fail(?:ing)? first|test first)\b", re.I)
TDD_GREEN = re.compile(r"\b(green|pass(?:ing)? test|implement|implementation)\b", re.I)
TEST_START = re.compile(
    r"^\s*(?:def\s+test_|async\s+def\s+test_|function\s+test|"
    r"(?:it|test|describe)\s*\(|[\w.]+\.test\s*\()",
    re.I,
)


def arg(flag, default=None):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default


def ids(path, pat):
    p = Path(path)
    if not p.exists():
        return set()
    return {m.group(0) for m in pat.finditer(p.read_text(encoding="utf-8"))}


def malformed_ids_in_text(text: str) -> set[str]:
    """ID-looking tokens that do not follow slug-only artifact grammar."""
    return {
        m.group(0)
        for m in ID_CANDIDATE.finditer(text)
        if not VALID_ANY.fullmatch(m.group(0))
    }


def malformed_ids(path: str | None) -> set[str]:
    if path is None:
        return set()
    p = Path(path)
    if not p.exists():
        return set()
    return malformed_ids_in_text(p.read_text(encoding="utf-8", errors="ignore"))


def source_files(root: Path, suffixes: set[str]):
    skipped = {
        ".git",
        ".hg",
        ".svn",
        "node_modules",
        ".venv",
        "venv",
        "__pycache__",
        "dist",
        "build",
    }
    for f in root.rglob("*"):
        if any(part in skipped for part in f.parts):
            continue
        if f.is_file() and f.suffix in suffixes:
            yield f


def extract_coverage(text: str) -> float | None:
    """Extract coverage from labeled output, ignoring unrelated percent text."""
    for pattern in (COV_TOTAL, COV_LABEL):
        hits = pattern.findall(text)
        if hits:
            return float(hits[-1])
    return None


def test_command() -> tuple[list[str] | str | None, bool]:
    """Return a safe argv command by default; shell execution requires opt-in."""
    argv_json = arg("--tests-argv")
    if argv_json:
        parsed = json.loads(argv_json)
        if not isinstance(parsed, list) or not all(isinstance(x, str) for x in parsed):
            raise ValueError("--tests-argv must be a JSON array of strings")
        return parsed, False
    cmd = arg("--tests")
    if not cmd:
        return None, False
    if "--tests-shell" in sys.argv:
        return cmd, True
    return shlex.split(cmd, posix=os.name != "nt"), False


def test_blocks(test_text: str) -> list[str]:
    blocks: list[list[str]] = []
    current: list[str] = []
    for line in test_text.splitlines():
        if TEST_START.search(line) and current:
            blocks.append(current)
            current = [line]
        else:
            current.append(line)
    if current:
        blocks.append(current)
    return ["\n".join(block) for block in blocks]


def has_nontrivial_assertion(block: str) -> bool:
    return bool(ASSERTION.search(block)) and not bool(WEAK_ASSERTION.search(block))


def assertion_linked_ids(test_text: str, wanted: set[str]) -> set[str]:
    """IDs whose own test/function block has a non-trivial assertion-like statement."""
    linked: set[str] = set()
    for block in test_blocks(test_text):
        ids_here = {
            item for item in wanted if item in block or item.replace("-", "_") in block
        }
        if not ids_here or not has_nontrivial_assertion(block):
            continue
        linked.update(ids_here)
    return linked


def git_output(args: list[str], cwd: Path) -> tuple[int, str]:
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, check=False)
    return result.returncode, result.stdout.strip()


def is_git_repo(root: Path) -> bool:
    rc, _ = git_output(["git", "rev-parse", "--is-inside-work-tree"], root)
    return rc == 0


def git_ref_exists(root: Path, ref: str) -> bool:
    rc, _ = git_output(["git", "rev-parse", "--verify", ref], root)
    return rc == 0


def auto_diff_base(root: Path, explicit_base: str | None) -> tuple[str | None, str]:
    if not is_git_repo(root):
        return None, "not_git_repo"
    if explicit_base:
        return explicit_base, f"explicit:{explicit_base}"
    rc, current = git_output(["git", "rev-parse", "--abbrev-ref", "HEAD"], root)
    if rc != 0:
        return None, "no_current_branch"
    rc, default_ref = git_output(
        ["git", "symbolic-ref", "--quiet", "--short", "refs/remotes/origin/HEAD"],
        root,
    )
    candidates = [default_ref] if rc == 0 and default_ref else []
    candidates.extend(["origin/main", "origin/master", "main", "master"])
    seen: set[str] = set()
    for candidate in candidates:
        if candidate in seen or not git_ref_exists(root, candidate):
            continue
        seen.add(candidate)
        if current == candidate.split("/")[-1]:
            return None, "on_default_branch_no_review_base"
        rc, merge_base = git_output(["git", "merge-base", "HEAD", candidate], root)
        if rc == 0 and merge_base:
            return merge_base, f"merge_base:{candidate}"
    return None, "no_merge_base"


def git_diff_loc(root: Path, base: str | None) -> tuple[int | None, str]:
    resolved_base, evidence = auto_diff_base(root, base)
    if resolved_base is None:
        return None, evidence
    diff_args = ["git", "diff", "--numstat", resolved_base, "HEAD", "--"]
    rc, out = git_output(diff_args, root)
    if rc != 0:
        return None, "diff_failed"
    total = 0
    for line in out.splitlines():
        added, deleted, *_ = line.split("\t")
        if added == "-" or deleted == "-":
            continue
        total += int(added) + int(deleted)
    return total, evidence


def git_tdd_evidence(root: Path, base: str | None) -> dict[str, object]:
    resolved_base, base_evidence = auto_diff_base(root, base)
    if resolved_base is None:
        return {"available": False, "reason": base_evidence}
    rev_range = f"{resolved_base}..HEAD"
    rc, log = git_output(["git", "log", "--format=%s%n%b", rev_range], root)
    if rc != 0:
        return {"available": False, "reason": "log_failed"}
    return {
        "available": True,
        "base": base_evidence,
        "red_marker": bool(TDD_RED.search(log)),
        "green_marker": bool(TDD_GREEN.search(log)),
    }


def main() -> int:
    as_json = "--json" in sys.argv
    plan = arg("--plan", "plan.md")
    tests_dir = Path(arg("--tests-dir", "tests"))
    src = Path(arg("--src", "."))
    cov_min = float(arg("--cov-min", "80"))
    max_loc = int(arg("--max-loc", "600"))
    max_diff_loc = int(arg("--max-diff-loc", "300"))
    diff_base = arg("--diff-base")
    require_git = "--allow-missing-git-evidence" not in sys.argv
    require_tdd = "--allow-missing-tdd-evidence" not in sys.argv
    src_ext = {
        e.strip()
        for e in arg("--src-ext", ".py,.ts,.tsx,.js,.jsx").split(",")
        if e.strip()
    }
    cmd, use_shell = test_command()

    test_text = ""
    if tests_dir.exists():
        for f in tests_dir.rglob("*.*"):
            if f.suffix in (".py", ".ts", ".js", ".tsx", ".jsx"):
                test_text += f.read_text(encoding="utf-8", errors="ignore") + "\n"

    spec_path = arg("--spec", "spec.md")
    design_path = arg("--design", "design.md")
    bad_ids = (
        malformed_ids(plan)
        | malformed_ids(spec_path)
        | malformed_ids(design_path)
        | malformed_ids_in_text(test_text)
    )

    plan_prs = ids(plan, PR)
    seen_prs = {
        p for p in plan_prs if p.replace("-", "_") in test_text or p in test_text
    }
    want = ids(spec_path, ID) | ids(design_path, ID)
    seen = {i for i in want if i in test_text or i.replace("-", "_") in test_text}
    assertion_seen = assertion_linked_ids(test_text, want)

    oversized = sorted(
        str(f)
        for f in source_files(src, src_ext)
        if f.is_file()
        and len(f.read_text(encoding="utf-8", errors="ignore").splitlines()) > max_loc
    )
    vague = VAGUE.findall(test_text) + SKIP.findall(test_text)

    tests_pass, cov = None, None
    if cmd:
        r = subprocess.run(cmd, shell=use_shell, capture_output=True, text=True)
        tests_pass = r.returncode == 0
        cov = extract_coverage(r.stdout + r.stderr)

    cwd = Path.cwd()
    diff_loc, diff_evidence = git_diff_loc(cwd, diff_base)
    tdd_evidence = git_tdd_evidence(cwd, diff_base)
    diff_ok = diff_loc is not None and diff_loc <= max_diff_loc
    oversized_diff = diff_loc is not None and diff_loc > max_diff_loc
    tdd_ok = bool(tdd_evidence.get("red_marker")) and bool(
        tdd_evidence.get("green_marker")
    )

    pr_pct = round(100 * len(seen_prs) / len(plan_prs), 1) if plan_prs else 100.0
    id_pct = round(100 * len(seen) / len(want), 1) if want else 100.0
    assertion_id_pct = (
        round(100 * len(assertion_seen) / len(want), 1) if want else 100.0
    )
    gates = {
        "tests_pass": bool(tests_pass),
        "id_format_slug_only": not bad_ids,
        "coverage_ok": cov is not None and cov >= cov_min,
        "pr_traceability_100": seen_prs == plan_prs,
        "id_traceability_100": seen == want,
        "id_assertion_traceability_100": assertion_seen == want,
        "no_oversized_modules": not oversized,
        "diff_size_ok": diff_ok if require_git else diff_loc is None or diff_ok,
        "tdd_evidence_ok": tdd_ok if require_tdd else True,
        "no_vagueness": len(vague) == 0,
    }
    report = {
        "tests_pass": gates["tests_pass"],
        "coverage_pct": cov,
        "cov_min": cov_min,
        "pr_traceability_pct": pr_pct,
        "id_traceability_pct": id_pct,
        "id_assertion_traceability_pct": assertion_id_pct,
        "uncovered_prs": sorted(plan_prs - seen_prs),
        "uncovered_ids": sorted(want - seen),
        "ids_without_nearby_assertion": sorted(want - assertion_seen),
        "bad_id_format": sorted(bad_ids),
        "oversized_modules": oversized,
        "diff_loc": diff_loc,
        "max_diff_loc": max_diff_loc,
        "diff_evidence": diff_evidence,
        "git_evidence_required": require_git,
        "oversized_diff": oversized_diff,
        "tdd_evidence": tdd_evidence,
        "tdd_evidence_required": require_tdd,
        "vague_hits": len(vague),
        "gates": gates,
        "passed": sum(gates.values()),
        "total": len(gates),
    }
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        for k, v in gates.items():
            print(f"{'PASS' if v else 'FAIL'}  {k}")
        print(f"\nPR {pr_pct}%  ID {id_pct}%  cov {cov}")
        print(f"{report['passed']}/{report['total']} gates passed")
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
