---
description: Qualitatively review implemented code, tests, logging/error-handling, docs, build/deploy work, and upstream consistency using existing verification evidence where available.
agent: agent
---

# Code Review

Perform the qualitative review of implemented code, tests, docs, build/deploy work, and
upstream consistency. This command judges the change; it does not replace `/code-verify`.
If verification evidence is absent, state that gap and either use the latest supplied
evidence or recommend `/code-verify`. Use `/code-assess` when the user wants verification
and review together.

Do not edit code unless explicitly asked.

Before judging the code itself, check whether the upstream spec, design, and plan are fit
for this implementation. If a latent upstream issue prevents fair code review, stop with an
upstream blocker and name the affected IDs/sections.

Use an adversarial posture: try to refute correctness, test implementation quality, TDD claims,
planned-scope fidelity, implementation/design fit, logging/telemetry and error-handling
fitness, deployment safety, documentation completeness, and quality-gate adequacy. Prefer
fresh context, a separate reviewer, or a different model/tool when available. If the same
agent implemented the code, state that the review is not independent.

## Qualitative Review

Score each item 1-5 and give one concrete fix for any score below 5:

- Upstream code-readiness: spec/design/plan are still fit for the implemented behavior.
- TDD authenticity: tests appear to have meaningful Red/Green history or the lack of
  independent evidence is clearly reported.
- Test implementation quality and level completeness: executable acceptance tests cover
  assigned `AT-` items, and planned `TEST-` obligations cover unit/pure-core, component,
  contract, integration, UI, migration, operational, and quality-attribute risks. Review the
  test code itself: assertions, fixtures, helpers, mocks, generated data, setup/teardown,
  selectors, determinism, speed, isolation, readability, maintainability, and
  false-positive/false-negative risk.
- Supplemental inner tests: code-discovered helper, pure-core, parser, mapper, regression,
  characterization, property/table, adapter, or edge-case tests are useful, traceable to the
  nearest `PR-` and relevant `FR-`/`AT-`/`TEST-`/`COMP-`, and stay inside the Planned Touch
  Set. Flag tests that replace required `AT-`/`TEST-` coverage, overfit implementation
  trivia, lack an oracle, or reveal product-visible behavior that should have updated
  upstream artifacts.
- Verification-oracle rigor: every test has a concrete pass/fail oracle aligned with the
  design/plan, such as return values, state changes, persisted records, emitted events, API
  responses, DOM/accessibility output, screenshots/visual baselines, generated artifacts,
  structured logs, metrics, traces, deployment signals, or captured external calls. Reject
  tests that only prove execution, mock invocation, or absence of exceptions unless that is
  the specified behavior.
- Contract realism: boundary-facing tests use shared fixtures, schemas, generated clients,
  captured representative examples, or contract tests that match the real producer/consumer
  contract, including error variants; ad-hoc convenient mocks are flagged.
- UI quality and selector resilience: planned styling/layout/responsive/accessibility and
  readable loading/empty/error/validation states are present, while behavior tests remain
  role/text/semantic rather than CSS-coupled unless style itself is under test.
- Mock UI fidelity: when a mock UI was required, production UI changes match the approved
  mock's screens, states, flows, copy intent, and responsive expectations, or clearly record
  an approved deviation.
- Logging and telemetry fitness: planned structured logs, events, metrics, traces,
  audit/support IDs, correlation propagation, redaction, alert hooks, and human/agent
  debugging signals are implemented, tested, stable, and free of secrets or excessive noise.
- Error-handling fitness: UI, API, domain, integration, infrastructure, validation,
  authorization, timeout, offline, and unexpected failures map to safe messages, typed/
  documented errors, retries/fallback/degraded behavior, escalation, and logs/telemetry at
  the right boundary.
- Correctness: implementation satisfies FR/AT behavior and relevant edge cases.
- Design fidelity: component boundaries, pure-core/imperative-shell separation, interfaces,
  data ownership, failure handling, and dependency direction match the design.
- Planned scope fidelity: changed files/sections stay within the Planned Touch Set; any
  drift is treated as a plan/design/spec revision need.
- Build/deployment completeness: assigned artifacts, deployment scripts/manifests,
  migrations, smoke checks, rollback checks, and release docs are credible and verified
  where planned.
- Documentation completeness: user/developer docs, examples, generated/reference docs,
  runbooks, troubleshooting, and release/migration notes match behavior where planned.
- Production quality: validation, error handling, logging/telemetry, security/privacy,
  observability, configuration/secrets handling, reliability, accessibility, and performance
  concerns are handled to the level required by the spec/design.
- Quality-gate fitness: pre-commit/equivalent gates are language-appropriate, thresholded,
  aligned with CI, and not trivially bypassed.
- Maintainability: code is readable, cohesive, appropriately factored, and avoids dead or
  speculative code. Test helpers and fixtures are factored enough to prevent drift without
  hiding the behavior being asserted.

## Output

1. Upstream blockers, if any.
2. Verification evidence considered, or a clear note that none was available.
3. Qualitative scorecard.
4. Top fixes ranked by impact.
5. **Review verdict**: Pass / Pass-with-fixes / Needs rework / Blocked-upstream.

After reporting the verdict, stop. Do not move to the next PR, release, deployment, or any
downstream artifact without explicit user approval.
