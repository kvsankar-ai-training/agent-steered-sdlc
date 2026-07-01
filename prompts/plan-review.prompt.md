---
description: Qualitatively review a work plan using existing verification evidence where available.
agent: agent
---

# Plan Review

Perform the qualitative review of a work plan. This command judges planning substance; it
does not replace `/plan-verify`. If verification evidence is absent, state that gap and
either use the latest supplied evidence or recommend `/plan-verify`. Use `/plan-assess`
when the user wants verification and review together.

Target the plan file the user provides, defaulting to `plan.md`. Do not edit it unless
explicitly asked.

Before judging the plan itself, check whether the upstream spec and design are fit to plan
from. If requirements, acceptance criteria, component boundaries, interfaces, dependencies,
logging/error-handling strategy, build/deployment strategy, documentation strategy, or
slicing constraints are defective, stop with an upstream blocker.

Use an adversarial posture: try to refute the slicing, find missing upstream changes,
oversized PRs, fake TDD steps, unsafe parallelism, touch-set drift, dependency traps, and
traceability theater. Prefer fresh context, a separate reviewer, or a different model/tool
when available. If the same agent created the plan, state that the review is not
independent.

## Qualitative Review

Score each item 1-5 and give one concrete fix for any score below 5:

- Upstream fitness: spec and design are ready enough for this plan.
- Plan type/readiness: breakdown, implementation, or lightweight plan matches the declared
  scope and readiness.
- PR slicing: PRs are coherent, reviewable, one focused concern, and normally <=300 LOC.
- Planned Touch Sets: files/sections are explicit enough to bound implementation and catch
  scope drift.
- TDD discipline: Red and Green steps would produce meaningful failing tests before code,
  not merely template words.
- Test allocation: `AT-` acceptance coverage and explicit design `TEST-` obligations for
  lower-level unit/component/contract/integration/UI/quality/operational tests are assigned
  to appropriate PRs.
- Inner-test discovery: the plan leaves room for code-discovered supplemental inner tests
  inside each PR without relying on them to cover missing `AT-`/`TEST-` obligations or
  permitting product-scope creep.
- Verification-oracle allocation: each planned executable test names the observable evidence
  that proves pass/fail, such as return value, state, event, API response, DOM/accessibility
  output, screenshot, artifact, log, metric, trace, deployment signal, or external call.
- Contract-fixture allocation: boundary-facing PRs use shared fixtures, schemas, generated
  clients, captured representative examples, or contract tests instead of ad-hoc mock
  payloads.
- UX/presentation allocation: UI-facing PRs assign baseline styling/layout,
  responsive/accessibility checks, and readable loading/empty/error/validation states, or
  explicitly scope them out.
- Mock UI approval: if the spec/design requires a mock UI, UI-facing PRs reference the
  approved mock artifact and block until approval is explicit.
- Logging/error-handling allocation: PRs assign structured logs, telemetry, correlation/
  support IDs, redaction, alert hooks, representative failure-path tests, error mapping,
  retry/fallback/degraded behavior, and safe UI/API messages where required.
- Build/deployment allocation: package, artifact, release, migration, deployment dry-run,
  smoke, and rollback work is assigned where relevant.
- Documentation allocation: user/developer docs, generated/reference docs, examples,
  runbooks, and release notes are assigned where relevant.
- Sequencing and dependencies: prerequisites are ordered, no forward dependency traps, and
  integration points are visible.
- Parallelism/worktrees: independent tracks are identified safely, with merge risks called
  out.
- Risk and rollback: high-risk changes have mitigation, validation, and rollback strategy.

## Output

1. Upstream blockers, if any.
2. Verification evidence considered, or a clear note that none was available.
3. Qualitative scorecard.
4. Top fixes ranked by impact.
5. **Review verdict**: Pass / Pass-with-fixes / Needs rework / Blocked-upstream.

After reporting the verdict, stop. Do not start `/code-create` or any downstream command
without explicit user approval.
