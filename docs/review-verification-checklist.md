# Verification And Review Checklist

Every assessment command must pair structural/mechanical verification evidence with
qualitative judgment. Checker JSON is never the whole assessment.

Command verbs have distinct meanings:

- `verify`: run deterministic/mechanical checks and report evidence only.
- `review`: make the qualitative adversarial judgment using available evidence.
- `assess`: run `verify` first, then `review`; this is the full gate.

Run the two parts with fresh context whenever the agent platform supports it:

1. **Mechanical Verifier sub-agent** — runs deterministic checkers and reports raw evidence,
   IDs, metrics, and command failures without making the final judgment.
2. **Qualitative Reviewer sub-agent** — starts from the artifact plus mechanical evidence,
   uses an adversarial posture, and judges correctness, completeness, risks, upstream
   blockers, and the verdict.

If sub-agents are unavailable, the main agent must explicitly say so and still separate the
mechanical and qualitative passes in the report.

## Required Assessment Verifications

| Assessment command | Mechanical Verifier sub-agent | Qualitative Reviewer sub-agent |
| --- | --- | --- |
| `/spec-assess` | `/spec-verify`: run `check_spec.py` on the target spec. | `/spec-review`: score the spec for problem framing, stakeholder needs, non-goals, scope/readiness, use cases, requirements, NFRs, acceptance quality, UX/presentation expectations, UI mock preference, boundary contracts, logging/error-handling intent, build/release/deployment intent, user/developer documentation intent, and traceability. |
| `/design-assess` | `/design-verify`: run `check_spec.py` on the upstream spec when present, then `check_design.py` on the target design. | `/design-review`: judge upstream spec fitness first, then score requirement fit, context, quality attributes, views, mock UI artifact/approval when required, logging/telemetry and error-handling design, build/deployment design, documentation design, depth/readiness, cohesion/coupling, contracts, contract realism, UX/presentation states, data/side effects, core/shell separation, testability, verification-oracle design, decisions, and risks. |
| `/plan-assess` | `/plan-verify`: run `check_spec.py` and `check_design.py` on upstream artifacts when present, then `check_plan.py` on the target plan. | `/plan-review`: judge upstream spec/design fitness first, then score PR sizing, plan type/readiness, scope-specific completeness, TDD discipline, coverage, test-level allocation, verification-oracle allocation, contract-fixture allocation, UX/presentation allocation, mock UI approval allocation, logging/error-handling allocation, build/deployment allocation, documentation allocation, Planned Touch Sets, sequencing, parallelism/worktrees, and production quality. |
| `/code-assess` | `/code-verify`: run upstream checkers when present, `check_code.py` with the test command, coverage threshold, and default git diff/TDD evidence; run pre-commit or the repository's equivalent local quality gate; run planned logging/error-handling/build/docs/deployment verification. | `/code-review`: judge upstream code-readiness first, then score implementation correctness, planned and supplemental inner test quality, verification-oracle rigor, contract realism, mock UI fidelity when required, logging/telemetry and error-handling fitness, UI quality/selector resilience, build/deployment completeness, documentation completeness, TDD authenticity, design fidelity, planned-scope fidelity, readability, production quality, and quality-gate fitness. |

## Blocking Rule

If an upstream mechanical checker fails, or if qualitative review reveals that an upstream
artifact must change before the downstream artifact can be judged fairly, stop the downstream
review/assessment and report the upstream blocker. Do not continue to the downstream
mechanical or qualitative verdict until the upstream issue is resolved.

## Reporting Rule

Every non-blocked assessment report must include:

1. Mechanical verification scorecard.
2. Qualitative review scorecard.
3. Top fixes ranked by impact.
4. Verdict.

`/code-assess` additionally includes a pre-commit/local quality-gate scorecard.

Also state whether the mechanical and qualitative passes were run by fresh-context
sub-agents. If not, state the limitation.
