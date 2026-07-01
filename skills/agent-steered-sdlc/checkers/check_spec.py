#!/usr/bin/env python3
"""Deterministic mechanical verifier for a Software Requirements Spec.

Parses an SRS markdown file, validates IDs/structure, and computes structural
coverage metrics (e.g. % of use cases and FRs referenced by acceptance tests).
It also checks obvious NFR unit/quality mismatches and acceptance-test scenario
shape. Exits 0 only when every structural gate passes. No semantic judgment,
fully reproducible.

Usage:
    python check_spec.py [spec.md] [--json] [--feature] [--parent product.md]

--feature  Treat the file as a feature-level spec (a subset of a product).
           Full-section presence is not required; coverage still enforced.
--parent   A product spec whose IDs may be referenced (so they are not orphans).
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

from schemas import SPEC_SECTIONS  # noqa: E402

SLUG_TOKEN = r"[A-Z][A-Z0-9]{1,31}"
ID = re.compile(rf"\b(UN|FEAT|UC|FR|NFR|AT)-({SLUG_TOKEN})-({SLUG_TOKEN})\b")
ID_CANDIDATE = re.compile(r"\b(?:UN|FEAT|UC|FR|NFR|AT|TEST)(?:-[A-Za-z0-9]+)+\b", re.I)
VAGUE = re.compile(r"\b(?:and/or|tbd|as appropriate|as needed|fast|easy)\b|etc\.", re.I)
NUM_UNIT = re.compile(
    r"\d+(?:\.\d+)?\s*(ms|s|sec|min|%|mb|gb|kb|req|rps|users|days|hrs|"
    r"hours|decimal|decimals|dp|c|°c)(?:\b|$)",
    re.I,
)
QUALITY_UNITS = [
    (
        re.compile(r"\b(latency|response|respond|complete|within)\b", re.I),
        {"ms", "s", "sec", "min"},
    ),
    (re.compile(r"\b(throughput|request|requests|rate)\b", re.I), {"req", "rps"}),
    (re.compile(r"\b(availability|uptime|reliability|success rate)\b", re.I), {"%"}),
    (re.compile(r"\b(memory|storage|size|payload)\b", re.I), {"kb", "mb", "gb"}),
    (
        re.compile(r"\b(retention|retain|purge|delete after)\b", re.I),
        {"days", "hrs", "hours"},
    ),
    (
        re.compile(r"\b(precision|accuracy|round|rounded)\b", re.I),
        {"%", "decimal", "decimals", "dp", "c", "°c"},
    ),
]
# Leading markdown list markers that precede a defining ID (not table pipes).
LEAD = re.compile(r"^[\s#>\-\*\+\d\.\)]*")
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*$")
DEF_MARKER = re.compile(r"^\s*(?:#{1,6}\s+|[-*+]\s+|\d+[\.)]\s+)")


def _defline(line: str):
    """Match an ID at the start of a line after stripping list/heading markers."""
    if not DEF_MARKER.match(line):
        return None
    return ID.match(LEAD.sub("", line.strip()))


def _norm_heading(title: str) -> str:
    title = re.sub(r"\s+#*$", "", title.strip())
    title = title.replace("*", "").replace("`", "")
    return re.sub(r"\s+", " ", title).casefold()


def sections_present_in_order(text: str, required: list[str]) -> bool:
    """Required headings must appear as headings, in order."""
    headings = [
        _norm_heading(m.group(1))
        for line in text.splitlines()
        if (m := HEADING.match(line.strip()))
    ]
    pos = 0
    required_norm = [_norm_heading(s) for s in required]
    for heading in headings:
        if pos < len(required_norm) and heading == required_norm[pos]:
            pos += 1
    return pos == len(required_norm)


def item_blocks(text: str, kinds: set[str]) -> dict[str, str]:
    """Map defining ID to its markdown block, up to the next definition or heading."""
    blocks: dict[str, str] = {}
    cur, buf = None, []
    in_fence = False
    for line in text.splitlines():
        fence = line.strip().startswith("```")
        m = None if in_fence else _defline(line)
        is_heading = HEADING.match(line.strip()) is not None
        if m and m.group(1) in kinds:
            if cur:
                blocks[cur] = "\n".join(buf)
            cur, buf = m.group(0), [line]
        elif cur:
            if is_heading or (m and m.group(1) in kinds):
                blocks[cur] = "\n".join(buf)
                cur, buf = None, []
            else:
                buf.append(line)
        if fence:
            in_fence = not in_fence
    if cur:
        blocks[cur] = "\n".join(buf)
    return blocks


def defs_and_refs(text: str):
    """Return {kind: set(ids defined on their own line)} and all referenced ids."""
    defined: dict[str, set] = {
        k: set() for k in ("UN", "FEAT", "UC", "FR", "NFR", "AT")
    }
    refs: set[str] = set()
    in_fence = False
    for line in text.splitlines():
        if line.strip().startswith("```"):
            in_fence = not in_fence
            refs.update(m.group(0) for m in ID.finditer(line))
            continue
        ids = [m.group(0) for m in ID.finditer(line)]
        if ids:  # first id on a line that defines an item
            first = None if in_fence else _defline(line)
            if first:
                defined[first.group(1)].add(first.group(0))
            refs.update(ids)
    return defined, refs


def covered_by(targets: set, ats: dict[str, set], kinds: set) -> set:
    """IDs in targets that appear in some AT's reference set."""
    referenced = set().union(*ats.values()) if ats else set()
    return {t for t in targets if t in referenced and t[: t.index("-")] in kinds}


def vague_count(text: str) -> int:
    return len(VAGUE.findall(text))


def malformed_ids(text: str) -> list[str]:
    """ID-looking tokens that do not follow KIND-AREA-NAME slug grammar."""
    return sorted(
        {
            m.group(0)
            for m in ID_CANDIDATE.finditer(text)
            if not ID.fullmatch(m.group(0))
        }
    )


def unit_mismatches(blocks: dict[str, str]) -> list[str]:
    mismatches = []
    for nfr, block in blocks.items():
        units = {m.group(1).lower() for m in NUM_UNIT.finditer(block)}
        if not units:
            continue
        for pattern, allowed in QUALITY_UNITS:
            if pattern.search(block) and not units & allowed:
                mismatches.append(nfr)
                break
    return sorted(mismatches)


def ats_missing_scenario_shape(blocks: dict[str, str]) -> list[str]:
    missing = []
    for at, block in blocks.items():
        has_gwt = all(
            re.search(rf"\b{word}\b", block, re.I) for word in ("given", "when", "then")
        )
        has_measurable_check = re.search(
            r"\b(observe|verify|measure|expect|assert|check)\b", block, re.I
        )
        if not (has_gwt or has_measurable_check):
            missing.append(at)
    return sorted(missing)


def main() -> int:
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    as_json = "--json" in sys.argv
    feature = "--feature" in sys.argv
    parent_ids: set[str] = set()
    if "--parent" in sys.argv:
        p = sys.argv[sys.argv.index("--parent") + 1]
        pd, _ = defs_and_refs(Path(p).read_text(encoding="utf-8"))
        parent_ids = set().union(*pd.values())
    path = Path(args[0] if args else "spec.md")
    text = path.read_text(encoding="utf-8")
    defined, refs = defs_and_refs(text)
    all_ids = set().union(*defined.values()) | parent_ids

    # AT -> referenced ids in the whole acceptance-test block.
    ats = {
        at: {x.group(0) for x in ID.finditer(block)}
        for at, block in item_blocks(text, {"AT"}).items()
    }
    at_blocks = item_blocks(text, {"AT"})

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
    orphans = sorted(r for r in refs if r not in all_ids)
    vague = vague_count(text)
    nfr_blocks = item_blocks(text, {"NFR"})
    nfr_no_unit = [
        n for n in defined["NFR"] if not NUM_UNIT.search(nfr_blocks.get(n, ""))
    ]
    nfr_bad_unit = unit_mismatches(nfr_blocks)
    weak_ats = ats_missing_scenario_shape(at_blocks)

    uc, fr = defined["UC"], defined["FR"]
    uc_cov = covered_by(uc, ats, {"UC"})
    fr_cov = covered_by(fr, ats, {"FR"})

    def pct(a, b):
        return round(100 * len(a) / len(b), 1) if b else 100.0

    gates = {
        "id_format_slug_only": not bad_fmt,
        "no_duplicates": not dupes,
        "no_orphan_refs": not orphans,
        "uc_at_coverage_100": uc_cov == uc,
        "fr_at_coverage_100": fr_cov == fr,
        "nfr_has_units": not nfr_no_unit,
        "nfr_units_match_quality": not nfr_bad_unit,
        "ats_have_scenario_shape": not weak_ats,
        "no_vagueness": vague == 0,
    }
    if not feature:
        gates["sections_present"] = sections_present_in_order(text, SPEC_SECTIONS)
    report = {
        "mode": "feature" if feature else "product",
        "counts": {k: len(v) for k, v in defined.items()},
        "uc_at_coverage_pct": pct(uc_cov, uc),
        "fr_at_coverage_pct": pct(fr_cov, fr),
        "uncovered_use_cases": sorted(uc - uc_cov),
        "uncovered_frs": sorted(fr - fr_cov),
        "orphan_refs": orphans,
        "duplicates": dupes,
        "bad_id_format": bad_fmt,
        "nfr_missing_units": nfr_no_unit,
        "nfr_unit_mismatches": nfr_bad_unit,
        "ats_missing_scenario_shape": weak_ats,
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
        uc_pct = report["uc_at_coverage_pct"]
        fr_pct = report["fr_at_coverage_pct"]
        print(f"\nUC->AT {uc_pct}%  FR->AT {fr_pct}%")
        print(f"{report['passed']}/{report['total']} gates passed")
    return 0 if all(gates.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
