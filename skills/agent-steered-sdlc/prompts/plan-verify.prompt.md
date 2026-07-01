---
description: Run deterministic structural verification for a work plan and report evidence without qualitative judgment.
agent: agent
---

# Plan Verify

Run mechanical verification for a work plan. This command collects evidence only; it does
not judge whether the plan slices work well. Use `/plan-review` for qualitative judgment
and `/plan-assess` for verify + review.

Target the plan file the user provides, defaulting to `plan.md`. Do not edit it unless
explicitly asked.

## Mechanical Verification

When upstream artifacts exist, first run:

```pwsh
python checkers/check_spec.py spec.md --json
python checkers/check_design.py design.md --spec spec.md --json
```

Then run:

```pwsh
python checkers/check_plan.py plan.md --spec spec.md --design design.md --json
```

For focused feature/component or slice/change plans, add `--feature` and `--parent` when
applicable.

If `python` is unavailable or fails because the launcher is missing, retry with `python3`;
if that is unavailable, retry with `uv run python`.

Report:

- Exact commands executed.
- Raw checker JSON.
- Exit codes.
- `passed/total`.
- Any upstream spec/design failures.
- Any bad IDs, duplicates, orphan refs, uncovered FR/AT/COMP/TEST refs, oversize declared
  PRs, missing Red/Green text, forward dependencies, or vague hits.

## Output

End with:

- **Verification result**: Pass / Fail / Unable to run.
- **Evidence limits**: structural verification only; qualitative review still required for
  slicing, sequencing, TDD usefulness, touch-set fidelity, and risk.
- **Recommended next command**: `/plan-review` or `/plan-assess`.
