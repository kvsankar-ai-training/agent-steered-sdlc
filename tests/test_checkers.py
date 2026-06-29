import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_checker(name: str):
    path = ROOT / "checkers" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def run_main(module, args, monkeypatch, capsys, cwd: Path):
    monkeypatch.chdir(cwd)
    monkeypatch.setattr(sys, "argv", [module.__file__, *args])
    rc = module.main()
    out = capsys.readouterr().out
    return rc, json.loads(out)


def write_valid_spec(path: Path) -> None:
    path.write_text(
        """# Mission Statement
Work Scope: Slice/change
Implementation Readiness: Code-ready

# User Needs
- UN-AUTH-10 Users need authenticated access.

# Non-Goals
- Anonymous posting is out of scope.

# Features
- FEAT-AUTH-10 Login satisfies UN-AUTH-10.

# Use Cases
- UC-AUTH-10 Actor: user. Goal: sign in. FEAT-AUTH-10.

# Functional Requirements
- FR-AUTH-10 The system shall allow valid users to sign in. UC-AUTH-10.

# Non-Functional Requirements
- NFR-PERF-10 Sign-in shall complete within 200 ms. Verification: timing.

# Acceptance Tests
- AT-AUTH-10 Given a valid user, when they sign in, then access is granted.
  Verifies UC-AUTH-10, FR-AUTH-10, and NFR-PERF-10.

# Traceability Matrix
UN-AUTH-10 -> FEAT-AUTH-10 -> UC-AUTH-10 -> FR-AUTH-10 -> AT-AUTH-10.

# Assumptions & Open Questions
- Credentials already exist.
""",
        encoding="utf-8",
    )


def write_valid_design(path: Path) -> None:
    path.write_text(
        """# Overview
Work Scope: Slice/change
Design Depth: LLD
Implementation Readiness: Code-ready

# Tech Stack
Python.

# Drivers & Constraints
FR-AUTH-10 and UC-AUTH-10 drive the design.

# Layers
- LAYER-APP Application orchestration.

# Components
- COMP-AUTH in LAYER-APP realizes FR-AUTH-10 and UC-AUTH-10 through IFACE-AUTH.

# Interfaces
- IFACE-AUTH owner: COMP-AUTH. Contract: authenticate credentials.

# Core vs. Shell
COMP-AUTH keeps credential policy pure and I/O at the shell.

# Key Flows
User calls IFACE-AUTH and COMP-AUTH validates credentials.

# Data Model
No persistent state is introduced.

# Design Decisions
- DEC-AUTH Use existing credential store.

# Test Strategy
COMP-AUTH has unit tests for policy and contract tests for IFACE-AUTH.

# Risks & Trade-offs
- RISK-AUTH Credential-store outage blocks sign-in.

# Traceability Matrix
FR-AUTH-10 -> COMP-AUTH -> IFACE-AUTH -> DEC-AUTH.
""",
        encoding="utf-8",
    )


def write_valid_plan(path: Path) -> None:
    path.write_text(
        """# Overview
Work Scope: Slice/change
Plan Type: Implementation
Implementation Readiness: Code-ready

# Strategy
Use Red/Green TDD and one small PR.

# Milestones
- MILE-AUTH-10 Deliver login.

# Pull Requests / Child Work Items
- PR-AUTH-10 Scope: implement login. LOC 120. Red: failing AT-AUTH-10 test.
  Green: implement COMP-AUTH. Delivers FR-AUTH-10, UC-AUTH-10, NFR-PERF-10,
  AT-AUTH-10, and COMP-AUTH.

# Coverage Map
FR-AUTH-10, UC-AUTH-10, NFR-PERF-10, AT-AUTH-10, and COMP-AUTH map to PR-AUTH-10.

# Sequencing & Risks
PR-AUTH-10 has no dependency.
""",
        encoding="utf-8",
    )


def test_check_spec_accepts_complete_structural_spec(tmp_path, monkeypatch, capsys):
    spec_path = tmp_path / "spec.md"
    write_valid_spec(spec_path)
    module = load_checker("check_spec")

    rc, report = run_main(
        module, [str(spec_path), "--json"], monkeypatch, capsys, tmp_path
    )

    assert rc == 0
    assert report["uc_at_coverage_pct"] == 100.0
    assert report["fr_at_coverage_pct"] == 100.0


def test_check_spec_rejects_nfr_without_units(tmp_path, monkeypatch, capsys):
    spec_path = tmp_path / "spec.md"
    write_valid_spec(spec_path)
    text = spec_path.read_text(encoding="utf-8").replace("200 ms", "soon")
    spec_path.write_text(text, encoding="utf-8")
    module = load_checker("check_spec")

    rc, report = run_main(
        module, [str(spec_path), "--json"], monkeypatch, capsys, tmp_path
    )

    assert rc == 1
    assert report["nfr_missing_units"] == ["NFR-PERF-10"]


def test_check_spec_rejects_latency_nfr_with_wrong_unit(tmp_path, monkeypatch, capsys):
    spec_path = tmp_path / "spec.md"
    write_valid_spec(spec_path)
    text = spec_path.read_text(encoding="utf-8").replace(
        "Sign-in shall complete within 200 ms.",
        "Sign-in latency shall support up to 5 users.",
    )
    spec_path.write_text(text, encoding="utf-8")
    module = load_checker("check_spec")

    rc, report = run_main(
        module, [str(spec_path), "--json"], monkeypatch, capsys, tmp_path
    )

    assert rc == 1
    assert report["nfr_unit_mismatches"] == ["NFR-PERF-10"]


def test_check_spec_rejects_acceptance_test_that_only_namedrops_ids(
    tmp_path, monkeypatch, capsys
):
    spec_path = tmp_path / "spec.md"
    write_valid_spec(spec_path)
    text = spec_path.read_text(encoding="utf-8").replace(
        "- AT-AUTH-10 Given a valid user, when they sign in, then access is granted.\n"
        "  Verifies UC-AUTH-10, FR-AUTH-10, and NFR-PERF-10.",
        "- AT-AUTH-10 Covers UC-AUTH-10, FR-AUTH-10, and NFR-PERF-10.",
    )
    spec_path.write_text(text, encoding="utf-8")
    module = load_checker("check_spec")

    rc, report = run_main(
        module, [str(spec_path), "--json"], monkeypatch, capsys, tmp_path
    )

    assert rc == 1
    assert report["ats_missing_scenario_shape"] == ["AT-AUTH-10"]


def test_check_design_accepts_complete_structural_design(tmp_path, monkeypatch, capsys):
    spec_path = tmp_path / "spec.md"
    design_path = tmp_path / "design.md"
    write_valid_spec(spec_path)
    write_valid_design(design_path)
    module = load_checker("check_design")

    rc, report = run_main(
        module,
        [str(design_path), "--spec", str(spec_path), "--json"],
        monkeypatch,
        capsys,
        tmp_path,
    )

    assert rc == 0
    assert report["comp_req_coverage_pct"] == 100.0
    assert report["comp_test_coverage_pct"] == 100.0


def test_check_design_accepts_equivalent_core_shell_section(
    tmp_path, monkeypatch, capsys
):
    spec_path = tmp_path / "spec.md"
    design_path = tmp_path / "design.md"
    write_valid_spec(spec_path)
    write_valid_design(design_path)
    text = design_path.read_text(encoding="utf-8").replace(
        "# Core vs. Shell",
        "# Core vs. Shell / Equivalent Separation",
    )
    design_path.write_text(text, encoding="utf-8")
    module = load_checker("check_design")

    rc, report = run_main(
        module,
        [str(design_path), "--spec", str(spec_path), "--json"],
        monkeypatch,
        capsys,
        tmp_path,
    )

    assert rc == 0
    assert report["gates"]["sections_present"] is True


def test_check_design_detects_missing_interface_owner(tmp_path, monkeypatch, capsys):
    spec_path = tmp_path / "spec.md"
    design_path = tmp_path / "design.md"
    write_valid_spec(spec_path)
    write_valid_design(design_path)
    text = design_path.read_text(encoding="utf-8").replace("owner: COMP-AUTH", "owner:")
    design_path.write_text(text, encoding="utf-8")
    module = load_checker("check_design")

    rc, report = run_main(
        module,
        [str(design_path), "--spec", str(spec_path), "--json"],
        monkeypatch,
        capsys,
        tmp_path,
    )

    assert rc == 1
    assert report["iface_owner_issues"] == ["IFACE-AUTH"]


def test_check_plan_accepts_complete_implementation_plan(tmp_path, monkeypatch, capsys):
    spec_path = tmp_path / "spec.md"
    design_path = tmp_path / "design.md"
    plan_path = tmp_path / "plan.md"
    write_valid_spec(spec_path)
    write_valid_design(design_path)
    write_valid_plan(plan_path)
    module = load_checker("check_plan")

    rc, report = run_main(
        module,
        [
            str(plan_path),
            "--spec",
            str(spec_path),
            "--design",
            str(design_path),
            "--json",
        ],
        monkeypatch,
        capsys,
        tmp_path,
    )

    assert rc == 0
    assert report["plan_kind"] == "implementation"
    assert report["at_coverage_pct"] == 100.0


def test_check_plan_rejects_declared_pr_over_300_loc(tmp_path, monkeypatch, capsys):
    spec_path = tmp_path / "spec.md"
    design_path = tmp_path / "design.md"
    plan_path = tmp_path / "plan.md"
    write_valid_spec(spec_path)
    write_valid_design(design_path)
    write_valid_plan(plan_path)
    text = plan_path.read_text(encoding="utf-8").replace("LOC 120", "LOC 301")
    plan_path.write_text(text, encoding="utf-8")
    module = load_checker("check_plan")

    rc, report = run_main(
        module,
        [
            str(plan_path),
            "--spec",
            str(spec_path),
            "--design",
            str(design_path),
            "--json",
        ],
        monkeypatch,
        capsys,
        tmp_path,
    )

    assert rc == 1
    assert report["oversized_prs"] == ["PR-AUTH-10"]
