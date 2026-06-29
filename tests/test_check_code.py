import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHECK_CODE = ROOT / "checkers" / "check_code.py"


def load_check_code():
    spec = importlib.util.spec_from_file_location("check_code", CHECK_CODE)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def git(cwd: Path, *args: str) -> None:
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True)


def run_check_code(
    tmp_path: Path,
    test_argv: list[str],
    monkeypatch,
    capsys,
    test_body: str | None = None,
):
    plan = tmp_path / "plan.md"
    spec = tmp_path / "spec.md"
    design = tmp_path / "design.md"
    tests = tmp_path / "tests"
    src = tmp_path / "src"
    tests.mkdir(exist_ok=True)
    src.mkdir(exist_ok=True)
    plan.write_text("- PR-AUTH-10\n", encoding="utf-8")
    spec.write_text("- FR-AUTH-10\n- AT-AUTH-10\n", encoding="utf-8")
    design.write_text("- COMP-AUTH\n", encoding="utf-8")
    (tests / "test_auth.py").write_text(
        test_body
        or (
            "def test_auth():\n"
            '    """Covers PR-AUTH-10, FR-AUTH-10, AT-AUTH-10, COMP-AUTH."""\n'
            "    assert 'granted' == 'granted'\n"
        ),
        encoding="utf-8",
    )
    module = load_check_code()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        sys,
        "argv",
        [
            str(CHECK_CODE),
            "--plan",
            str(plan),
            "--spec",
            str(spec),
            "--design",
            str(design),
            "--tests-dir",
            str(tests),
            "--src",
            str(src),
            "--tests-argv",
            json.dumps(test_argv),
            "--json",
        ],
    )
    rc = module.main()
    return rc, json.loads(capsys.readouterr().out)


def test_extract_coverage_prefers_labeled_coverage_over_stray_percent():
    check_code = load_check_code()
    output = "100% [=====]\ncoverage: 42%\n98% faster\n"
    assert check_code.extract_coverage(output) == 42.0


def test_extract_coverage_prefers_total_line_over_later_percent():
    check_code = load_check_code()
    output = "Name Stmts Miss Cover\nTOTAL 10 0 100%\n98% faster\n"
    assert check_code.extract_coverage(output) == 100.0


def test_check_code_default_coverage_threshold_is_80(tmp_path, monkeypatch, capsys):
    rc, report = run_check_code(
        tmp_path,
        [sys.executable, "-c", "print('coverage: 80%')"],
        monkeypatch,
        capsys,
    )
    assert rc == 0
    assert report["cov_min"] == 80.0
    assert report["coverage_pct"] == 80.0


def test_check_code_rejects_unlabeled_percent_as_coverage(
    tmp_path, monkeypatch, capsys
):
    rc, report = run_check_code(
        tmp_path,
        [sys.executable, "-c", "print('100% [progress]')"],
        monkeypatch,
        capsys,
    )
    assert rc == 1
    assert report["coverage_pct"] is None
    assert report["gates"]["coverage_ok"] is False


def test_check_code_rejects_id_only_weak_assertion(tmp_path, monkeypatch, capsys):
    weak_test = (
        "def test_auth():\n"
        '    """Covers PR-AUTH-10, FR-AUTH-10, AT-AUTH-10, COMP-AUTH."""\n'
        "    assert True\n"
    )

    rc, report = run_check_code(
        tmp_path,
        [sys.executable, "-c", "print('coverage: 80%')"],
        monkeypatch,
        capsys,
        weak_test,
    )

    assert rc == 1
    assert report["gates"]["id_assertion_traceability_100"] is False
    assert report["ids_without_nearby_assertion"] == [
        "AT-AUTH-10",
        "COMP-AUTH",
        "FR-AUTH-10",
    ]


def test_git_diff_loc_measures_actual_changed_lines(tmp_path):
    check_code = load_check_code()
    git(tmp_path, "init")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test User")
    source = tmp_path / "app.py"
    source.write_text("one\n", encoding="utf-8")
    git(tmp_path, "add", "app.py")
    git(tmp_path, "commit", "-m", "baseline")

    source.write_text("one\ntwo\nthree\n", encoding="utf-8")

    diff_loc, evidence = check_code.git_diff_loc(tmp_path, "HEAD")
    assert diff_loc == 2
    assert evidence == "git_diff_HEAD"


def test_git_tdd_evidence_reads_red_and_green_markers(tmp_path):
    check_code = load_check_code()
    git(tmp_path, "init")
    git(tmp_path, "config", "user.email", "test@example.com")
    git(tmp_path, "config", "user.name", "Test User")
    source = tmp_path / "app.py"
    source.write_text("one\n", encoding="utf-8")
    git(tmp_path, "add", "app.py")
    git(tmp_path, "commit", "-m", "baseline")
    source.write_text("one\ntest\n", encoding="utf-8")
    git(tmp_path, "add", "app.py")
    git(tmp_path, "commit", "-m", "red: failing test for auth")
    source.write_text("one\ntest\nimpl\n", encoding="utf-8")
    git(tmp_path, "add", "app.py")
    git(tmp_path, "commit", "-m", "green: implementation passes")

    evidence = check_code.git_tdd_evidence(tmp_path, "HEAD~2")
    assert evidence == {
        "available": True,
        "red_marker": True,
        "green_marker": True,
    }
