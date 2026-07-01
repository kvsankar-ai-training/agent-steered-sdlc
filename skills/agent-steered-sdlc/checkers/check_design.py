#!/usr/bin/env python3
"""Deterministic mechanical verifier for a Software Design Document.

Parses an SDD markdown file, validates IDs/structure, and computes structural
metrics for requirement references, explicit TEST- obligation coverage, single
interface ownership, and dependency-cycle freedom through interfaces. Exits 0
only when every structural gate passes. No semantic judgment, fully reproducible.

Usage:
    python check_design.py [design.md] [--json] [--component]
                           [--parent product.md] [--spec spec.md]

--component  Treat the file as a component-level design (a subset of a product).
             Full-section presence is not required; coverage still enforced.
--parent     A product design whose IDs may be referenced (so they are not orphans).
--spec       A spec file whose FR-/UC- IDs components may realize (so they resolve).
"""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

CHECKER_DIR = Path(__file__).resolve().parent
if str(CHECKER_DIR) not in sys.path:
    sys.path.insert(0, str(CHECKER_DIR))

from schemas import DESIGN_SECTIONS  # noqa: E402

SLUG_TOKEN = r"[A-Z][A-Z0-9]{1,31}"
ID = re.compile(
    rf"\b(?:(?:LAYER|COMP|IFACE|DEC|RISK)-{SLUG_TOKEN}|"
    rf"TEST-{SLUG_TOKEN}-{SLUG_TOKEN})\b"
)
DESIGN_ENTITY = re.compile(rf"\b(LAYER|COMP|IFACE|DEC|RISK)-({SLUG_TOKEN})\b")
REQ = re.compile(rf"\b(FR|UC|NFR|AT)-({SLUG_TOKEN})-({SLUG_TOKEN})\b")
VALID_ANY = re.compile(
    rf"\b(?:(?:LAYER|COMP|IFACE|DEC|RISK)-{SLUG_TOKEN}|"
    rf"(?:FR|UC|NFR|AT|TEST)-{SLUG_TOKEN}-{SLUG_TOKEN})\b"
)
ID_CANDIDATE = re.compile(
    r"\b(?:LAYER|COMP|IFACE|DEC|RISK|FR|UC|NFR|AT|TEST)"
    r"(?:-[A-Za-z0-9]+)+\b",
    re.I,
)
VAGUE = re.compile(r"\b(?:and/or|tbd|as appropriate|as needed)\b|etc\.", re.I)
# Leading markdown list markers that precede a defining ID (not table pipes).
LEAD = re.compile(r"^[\s#>\-\*\+\d\.\)]*")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
DEF_MARKER = re.compile(r"^\s*(?:#{1,6}\s+|[-*+]\s+|\d+[\.)]\s+)")


def _defline(line: str):
    """Match a design ID at the start of a line after stripping list markers."""
    if not DEF_MARKER.match(line):
        return None
    return ID.match(LEAD.sub("", line.strip()))


def id_kind(token: str) -> str:
    return token.split("-", 1)[0]


def _norm_heading(title: str) -> str:
    title = re.sub(r"\s+#*$", "", title.strip())
    title = title.replace("*", "").replace("`", "")
    return re.sub(r"\s+", " ", title).casefold()


def sections_present_in_order(text: str, required: list[str | tuple[str, ...]]) -> bool:
    headings = [
        _norm_heading(m.group(1))
        for line in text.splitlines()
        if (m := HEADING.match(line.strip()))
    ]
    pos = 0
    required_norm = [
        tuple(_norm_heading(x) for x in s) if isinstance(s, tuple) else _norm_heading(s)
        for s in required
    ]
    for heading in headings:
        if pos >= len(required_norm):
            break
        wanted = required_norm[pos]
        matched = heading in wanted if isinstance(wanted, tuple) else heading == wanted
        if matched:
            pos += 1
    return pos == len(required_norm)


def item_blocks(text: str, kinds: set[str]) -> dict[str, str]:
    blocks: dict[str, str] = {}
    cur, buf = None, []
    in_fence = False
    for line in text.splitlines():
        fence = line.strip().startswith("```")
        m = None if in_fence else _defline(line)
        is_heading = HEADING.match(line.strip()) is not None
        if m and id_kind(m.group(0)) in kinds:
            if cur:
                blocks[cur] = "\n".join(buf)
            cur, buf = m.group(0), [line]
        elif cur:
            if is_heading or (m and id_kind(m.group(0)) in kinds):
                blocks[cur] = "\n".join(buf)
                cur, buf = None, []
            else:
                buf.append(line)
        if fence:
            in_fence = not in_fence
    if cur:
        blocks[cur] = "\n".join(buf)
    return blocks


def section_text(text: str, title: str) -> str:
    wanted = _norm_heading(title)
    lines = text.splitlines()
    start = None
    start_level = 0
    for i, line in enumerate(lines):
        if (m := HEADING.match(line.strip())) and _norm_heading(m.group(1)) == wanted:
            start, start_level = i + 1, len(line) - len(line.lstrip("#"))
            break
    if start is None:
        return ""
    end = len(lines)
    for i in range(start, len(lines)):
        head = HEADING.match(lines[i].strip())
        level = len(lines[i]) - len(lines[i].lstrip("#"))
        if head and level <= start_level:
            end = i
            break
    return "\n".join(lines[start:end])


def defs_and_refs(text: str):
    """Return {kind: set(ids defined on their own line)} and all referenced ids."""
    defined: dict[str, set] = {
        k: set() for k in ("LAYER", "COMP", "IFACE", "DEC", "RISK", "TEST")
    }
    refs: set[str] = set()
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            refs.update(m.group(0) for m in ID.finditer(line))
            continue
        ids = [m.group(0) for m in ID.finditer(line)]
        if ids:
            first = None if in_fence else _defline(line)
            if first:
                defined[id_kind(first.group(0))].add(first.group(0))
            refs.update(ids)
    return defined, refs


def malformed_ids(text: str) -> list[str]:
    """ID-looking tokens that do not follow design/spec slug grammar."""
    return sorted(
        {
            m.group(0)
            for m in ID_CANDIDATE.finditer(text)
            if not VALID_ANY.fullmatch(m.group(0))
        }
    )


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    as_json = "--json" in sys.argv
    component = "--component" in sys.argv
    parent_ids: set[str] = set()
    req_ids: set[str] = set()
    if "--parent" in sys.argv:
        p = sys.argv[sys.argv.index("--parent") + 1]
        pd, _ = defs_and_refs(Path(p).read_text(encoding="utf-8"))
        parent_ids = set().union(*pd.values())
    if "--spec" in sys.argv:
        s = sys.argv[sys.argv.index("--spec") + 1]
        req_ids = {
            m.group(0) for m in REQ.finditer(Path(s).read_text(encoding="utf-8"))
        }
    path = Path(args[0] if args else "design.md")
    text = path.read_text(encoding="utf-8")
    defined, refs = defs_and_refs(text)
    all_ids = set().union(*defined.values()) | parent_ids

    # Per-component lines: requirement refs and explicit test-obligation refs.
    comps = defined["COMP"]
    comp_blocks = item_blocks(text, {"COMP"})
    iface_blocks = item_blocks(text, {"IFACE"})
    test_blocks = item_blocks(text, {"TEST"})
    comp_reqs = {
        c: {x.group(0) for x in REQ.finditer(block)} for c, block in comp_blocks.items()
    }
    ts_text = section_text(text, "Test Strategy")
    ts_tests = {
        m.group(0) for m in ID.finditer(ts_text) if id_kind(m.group(0)) == "TEST"
    }
    tested = {c for c in comps if any(c in block for block in test_blocks.values())}
    untraced_tests = []
    for test_id, block in test_blocks.items():
        linked_design = {
            m.group(0)
            for m in ID.finditer(block)
            if id_kind(m.group(0)) in {"COMP", "IFACE"}
        }
        linked_outcome = {m.group(0) for m in REQ.finditer(block)} | {
            m.group(0)
            for m in DESIGN_ENTITY.finditer(block)
            if m.group(1) in {"DEC", "RISK"}
        }
        if not linked_design or not linked_outcome:
            untraced_tests.append(test_id)
    covered = {c for c in comps if comp_reqs.get(c)}

    # Each interface must declare exactly one real component owner.
    iface_def_ids = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and (m := _defline(line)) and id_kind(m.group(0)) == "IFACE":
            iface_def_ids.append(m.group(0))
    iface_defs = Counter(iface_def_ids)
    iface_dupes = [i for i, n in iface_defs.items() if n > 1]
    iface_owners: dict[str, str] = {}
    iface_owner_issues = []
    for iface, block in iface_blocks.items():
        owner_refs: list[str] = []
        for line in block.splitlines():
            if re.search(r"\bowner\b", line, re.I):
                owner_refs.extend(
                    m.group(0)
                    for m in ID.finditer(line)
                    if id_kind(m.group(0)) == "COMP"
                )
        unique_owners = sorted(set(owner_refs))
        if len(unique_owners) != 1 or unique_owners[0] not in comps:
            iface_owner_issues.append(iface)
        else:
            iface_owners[iface] = unique_owners[0]

    def_ids = []
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            continue
        if not in_fence and (m := _defline(line)):
            def_ids.append(m.group(0))
    dupes = [i for i, n in Counter(def_ids).items() if n > 1]
    bad_fmt = malformed_ids(text)
    known = all_ids | req_ids
    orphans = sorted(r for r in refs if r not in known)
    vague = len(VAGUE.findall(text))

    # Dependency cycles: COMP -> owning COMP for any referenced interface.
    deps: dict[str, set] = {c: set() for c in comps}
    for comp, block in comp_blocks.items():
        for ref in {
            x.group(0) for x in ID.finditer(block) if id_kind(x.group(0)) == "IFACE"
        }:
            owner = iface_owners.get(ref)
            if owner and owner != comp:
                deps[comp].add(owner)

    def dependency_cycles(graph: dict[str, set]) -> list[list[str]]:
        cycles: list[list[str]] = []
        stack: list[str] = []
        visiting: set[str] = set()
        visited: set[str] = set()

        def dfs(n: str):
            visiting.add(n)
            stack.append(n)
            for nb in graph.get(n, ()):
                if nb in visiting:
                    cycles.append(stack[stack.index(nb) :] + [nb])
                elif nb not in visited:
                    dfs(nb)
            stack.pop()
            visiting.remove(n)
            visited.add(n)

        for node in graph:
            if node not in visited:
                dfs(node)
        return cycles

    cycles = dependency_cycles(deps)

    def pct(a, b):
        return round(100 * len(a) / len(b), 1) if b else 100.0

    gates = {
        "id_format_slug_only": not bad_fmt,
        "no_duplicates": not dupes,
        "no_orphan_refs": not orphans,
        "comp_req_coverage_100": covered == comps,
        "comp_test_coverage_100": tested == comps,
        "test_obligations_declared": bool(ts_tests) if comps else True,
        "test_obligation_traceability_100": not untraced_tests,
        "iface_single_owner": not iface_dupes and not iface_owner_issues,
        "no_dependency_cycles": not cycles,
        "no_vagueness": vague == 0,
    }
    if not component:
        gates["sections_present"] = sections_present_in_order(text, DESIGN_SECTIONS)
    report = {
        "mode": "component" if component else "product",
        "counts": {k: len(v) for k, v in defined.items()},
        "comp_req_coverage_pct": pct(covered, comps),
        "comp_test_coverage_pct": pct(tested, comps),
        "uncovered_components": sorted(comps - covered),
        "untested_components": sorted(comps - tested),
        "test_obligation_count": len(defined["TEST"]),
        "test_obligations_in_strategy": sorted(ts_tests),
        "untraced_test_obligations": sorted(untraced_tests),
        "iface_owner_count": len(iface_owners),
        "dependency_cycles": cycles,
        "orphan_refs": orphans,
        "duplicates": dupes,
        "bad_id_format": bad_fmt,
        "iface_duplicates": iface_dupes,
        "iface_owner_issues": sorted(iface_owner_issues),
        "vague_hits": vague,
        "gates": gates,
        "passed": sum(gates.values()),
        "total": len(gates),
    }
    if as_json:
        print(json.dumps(report, indent=2))
    else:
        for k, v in gates.items():
            print(f"{'PASS' if v else 'FAIL'}  {k}")
        print(
            f"\nCOMP->REQ {report['comp_req_coverage_pct']}%"
            f"  COMP->TEST {report['comp_test_coverage_pct']}%"
        )
        print(f"{report['passed']}/{report['total']} gates passed")
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
