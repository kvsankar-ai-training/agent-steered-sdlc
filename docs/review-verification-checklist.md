# Review Verification Checklist

Every review command must pair structural/mechanical evidence with qualitative judgment.
Checker JSON is never the whole review.

Run the two parts with fresh context whenever the agent platform supports it:

1. **Mechanical Reviewer sub-agent** — runs deterministic checkers and reports raw evidence,
   IDs, metrics, and command failures without making the final judgment.
2. **Qualitative Reviewer sub-agent** — starts from the artifact plus mechanical evidence,
   uses an adversarial posture, and judges correctness, completeness, risks, upstream
   blockers, and the verdict.

If sub-agents are unavailable, the main agent must explicitly say so and still separate the
mechanical and qualitative passes in the report.

## Required Review Verifications

| Review command | Mechanical Reviewer sub-agent | Qualitative Reviewer sub-agent |
| --- | --- | --- |
| `/spec-review` | Run `check_spec.py` on the target spec. | Score the spec for problem framing, stakeholder needs, non-goals, scope/readiness, use cases, requirements, NFRs, acceptance quality, and traceability. |
| `/design-review` | Run `check_spec.py` on the upstream spec when present. | Before design review, judge whether the spec is fit to design from; stop with an upstream spec blocker if ambiguity, missing acceptance criteria, bad NFRs, or scope issues block review. |
| `/design-review` | Run `check_design.py` on the target design. | Score the design for requirement fit, context, quality attributes, views, profile completeness, depth/readiness, cohesion/coupling, contracts, data/side effects, core/shell or equivalent separation, testability, decisions, and risks. |
| `/plan-review` | Run `check_spec.py` and `check_design.py` on upstream artifacts when present. | Before plan review, judge whether the spec and design are fit to plan from; stop with an upstream blocker if requirements, acceptance criteria, component boundaries, interfaces, dependencies, or slicing constraints are defective. |
| `/plan-review` | Run `check_plan.py` on the target plan. | Score the plan for PR sizing, plan type/readiness, scope-specific completeness, TDD discipline, coverage, test-level allocation, Planned Touch Sets, sequencing, parallelism/worktrees, and production quality. |
| `/code-review` | Run `check_spec.py`, `check_design.py`, and `check_plan.py` on upstream artifacts when present. | Before code review, judge whether upstream artifacts are code-ready and still fit the implemented behavior; stop with an upstream blocker if spec/design/plan changes are required. |
| `/code-review` | Run `check_code.py` with the test command, coverage threshold, and default git diff/TDD evidence. Use allow-missing evidence flags only when the limitation is reported. | Score implementation correctness, test quality, TDD authenticity, design fidelity, planned-scope fidelity, readability, production quality, and unverified evidence such as missing Red history or missing diff-size proof. |
| `/code-review` | Run pre-commit or the repository's equivalent local quality gate. | Judge whether the quality gate is language-appropriate, thresholded, aligned with CI, and not trivially bypassed. |

## Blocking Rule

If an upstream mechanical checker fails, or if qualitative review reveals that an upstream
artifact must change before the downstream artifact can be judged fairly, stop the downstream
review and report the upstream blocker. Do not continue to the downstream mechanical or
qualitative verdict until the upstream issue is resolved.

## Reporting Rule

Every non-blocked review report must include:

1. Mechanical/structural scorecard.
2. Qualitative scorecard.
3. Top fixes ranked by impact.
4. Verdict.

`/code-review` additionally includes a pre-commit/local quality-gate scorecard.

Also state whether the mechanical and qualitative passes were run by fresh-context
sub-agents. If not, state the limitation.
