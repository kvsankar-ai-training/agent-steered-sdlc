---
description: Run code verification gates, tests, quality checks, logging/error-handling checks, build/docs/deployment checks, and structural code evidence without qualitative review.
agent: agent
---

# Code Verify

Run verification gates for implemented code. This command is the confidence-run command:
tests, coverage, pre-commit/equivalent quality gates, logging/error-handling checks,
build/docs/deployment checks where planned, upstream structural checks, and `check_code.py`.
It collects evidence only; it does not perform a qualitative code review. Use `/code-review`
for judgment and `/code-assess` for verify + review.

Do not edit code unless explicitly asked.

## Upstream Structural Verification

When upstream artifacts exist, run:

```pwsh
python checkers/check_spec.py spec.md --json
python checkers/check_design.py design.md --spec spec.md --json
python checkers/check_plan.py plan.md --spec spec.md --design design.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry with `python3`;
if that is unavailable, retry with `uv run python`.

Report any upstream structural failure as evidence. Do not do qualitative upstream review in
this command.

## Code/Test Structural Verification

Run the planned test command through `check_code.py`:

```pwsh
python checkers/check_code.py --plan plan.md --tests-argv '<json-array>' --cov-min <n> --json
```

Prefer `--tests-argv`. Use `--tests-shell` only for trusted commands that genuinely need
shell behavior. Provide `--diff-base <base>` when the review target is known and automatic
merge-base resolution is not right.

Report:

- Exact command executed.
- Raw checker JSON.
- Exit code.
- `passed/total`.
- Test pass/fail.
- Coverage percentage.
- PR and FR/AT/COMP/TEST traceability percentages.
- Assertion-traceability percentage.
- Diff LOC and evidence source.
- TDD evidence source.
- Bad ID format, oversized modules/diffs, failing/skipped tests, TODO/FIXME/vague markers,
  and uncovered IDs.

## Local Quality Gates

Run the repository's configured one-command quality gate, normally:

```pwsh
uv run pre-commit run --all-files
```

If the project uses another documented equivalent, run that command instead. Report the
command, tools covered, thresholds, and pass/fail.

## Logging, Error, Build, Documentation, And Deployment Verification

Run planned commands where present:

- Logging/telemetry checks for structured events, metrics, traces, audit/support IDs,
  correlation propagation, redaction, alert hooks, and absence of sensitive data.
- Error-handling checks for UI/API/domain/integration/infrastructure error mapping,
  retry/fallback/degraded behavior, safe user/API messages, and representative failure
  paths.
- Build/package command and artifact existence/version check.
- Documentation build/generation/link/example checks.
- Deployment lint/dry-run/plan/template/smoke/rollback checks.

Do not perform a live production deployment unless the user explicitly asked for it.

## Output

End with:

- **Verification result**: Pass / Fail / Unable to run.
- Commands run and concise outcomes.
- Evidence gaps or commands that could not run.
- **Evidence limits**: verification evidence does not prove implementation quality, design
  fidelity, TDD authenticity, or test meaningfulness.
- **Recommended next command**: `/code-review` or `/code-assess`.
