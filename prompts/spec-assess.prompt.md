---
description: Assess a Software Requirements Specification with a deterministic mechanical pass and a qualitative pass grounded in stakeholder needs, use cases, supplementary requirements, logging/error-handling, documentation/build/deploy needs, scope, and traceability.
agent: agent
---

# Spec Assess

Assess a Software Requirements Specification against the same principles used to write it:
problem-first requirements, stakeholder need fidelity, use-case behavior in context,
supplementary/non-functional requirements, deliberate scope management, and end-to-end
traceability. Produce **two distinct parts**: mechanical verification and qualitative review.

Do not stop after the checker JSON. This assessment must include:

1. Verification A: structural `check_spec.py` evidence.
2. Verification B: qualitative spec assessment.

When the platform supports sub-agents, run these as two fresh-context passes:

- **Mechanical Verifier sub-agent**: run Verification A and return raw checker evidence.
- **Qualitative Reviewer sub-agent**: read the spec and mechanical evidence, then run
  Verification B adversarially.

If sub-agents are unavailable, state that limitation and keep the two sections separate.

Target the spec file the user provides (default `spec.md`). Do not edit it unless asked;
report findings only.

Use an adversarial assessment posture: try to refute the spec, find missing stakeholder needs,
ambiguous behavior, weak acceptance criteria, and traceability theater. Prefer a fresh
context, separate reviewer, or different model/tool when available. If the same agent that
created the spec is assessing it, state that the review half of the assessment is not independent.

If the user is assessing a **feature/component spec** or **slice/change spec** (a subset,
possibly referencing a parent product spec), add `--feature` and point `--parent` at the product
spec so its IDs are not treated as orphans. Otherwise review the whole product spec.

## Verification A — Mechanical / Deterministic (run the tool)

Run the bundled checker and report its output verbatim. This is a deterministic
**structural** check: it catches section, ID format, orphan-reference, coverage-link,
unit, and banned-word issues. It does not prove requirements are correct, complete, or
semantically well tested; Verification B must judge that.

```pwsh
python checkers/check_spec.py <spec.md> --json
```

For a feature/component or slice/change spec, run: `python checkers/check_spec.py <feature-or-change.md> --feature --parent <product.md> --json`

It exits `0` only if every structural gate passes (non-zero otherwise) and emits metrics:

- **counts** per ID kind (UN/FEAT/UC/FR/NFR/AT).
- **uc_at_coverage_pct** — must be **100%** (every use case ID is referenced by ≥1 AT).
- **fr_at_coverage_pct** — must be **100%** (every functional req ID is referenced by ≥1 AT).
- **uncovered_use_cases / uncovered_frs** — must be empty.
- **orphan_refs** — IDs referenced but never defined.
- **duplicates** — IDs defined more than once.
- **bad_id_format** — IDs that are not slug-only `KIND-AREA-NAME`, including trailing
  numeric IDs such as `FR-AUTH-10`.
- **nfr_missing_units** — NFRs without a number+unit.
- **nfr_unit_mismatches** — NFRs whose obvious quality dimension does not match the unit.
- **ats_missing_scenario_shape** — ATs that do not contain Given/When/Then or an equivalent
  observable/measurable verification shape. This is a presence check; qualitative review
  must still judge whether the acceptance test is meaningful.
- **vague_hits** — count of "etc.", "and/or", "tbd", "as appropriate", "fast", "easy".
- **gates** + `passed/total`.

If `python` is unavailable or fails because the launcher is missing, retry the same command
with `python3`; if that is unavailable, retry with `uv run python`. Only fall back to manual
checks after all three runners fail, and report the runner failures.
Present the JSON, then the `passed/total` and both coverage percentages. List every
uncovered/orphan/duplicate ID explicitly.

## Verification B — Qualitative

Reasoned judgment, scored 1–5 with one concrete fix each:

- **Problem framing** — mission, system boundary, stakeholders, success criteria, and root
  problem are clear before solution behavior appears.
- **Stakeholder need fidelity** — needs describe stakeholder goals/pains, not features,
  implementation, or UI wishes disguised as needs.
- **Feature derivation and scope control** — features are externally visible, trace to needs,
  and are prioritized or scoped without silent gold-plating.
- **Non-goal quality** — explicit exclusions and deferred work prevent accidental scope creep
  and do not contradict user needs, requirements, or acceptance tests.
- **Change-sized scope control** — slice/change specs are limited to the requirement delta,
  reference parent IDs, and clearly state unchanged parent behavior when the change is internal.
- **Scope and readiness fit** — the spec declares product/system, feature/component, or
  slice/change scope and a realistic Implementation Readiness. Parent specs may pass as
  Decomposable; only slice/change or sufficiently detailed feature/component specs should be
  marked Code-ready.
- **Scope-specific content completeness** — product/system specs carry mission,
  stakeholders, boundaries, product needs, non-goals, capabilities, representative use
  cases, major NFRs, logging/telemetry and error-handling expectations,
  build/release/deployment expectations, broad acceptance intent, user/developer
  documentation expectations, and child-artifact needs; feature/component specs carry
  parent references, local behavior, FR/NFR/AT coverage, dependencies, edge cases,
  logging/error-handling constraints, build/deployment constraints, documentation
  constraints, and non-goals;
  slice/change specs carry the exact requirement delta, parent IDs, changed/unchanged
  behavior, logging/error-handling, build/deployment, and documentation deltas when
  relevant, and code-ready acceptance criteria.
- **Use-case quality** — actors, goals, preconditions, main flow, alternatives/exceptions,
  postconditions, and actor value are complete and behavior-focused.
- **Requirement quality** — FRs are necessary, atomic, feasible, verifiable, unambiguous,
  design-free, and use "shall" consistently.
- **Supplementary/NFR coverage** — performance, security, privacy, reliability, usability,
  accessibility, interoperability, compliance, data, platform, logging/telemetry, error
  handling, build/release/deployment, and operational constraints are considered and
  measurable where applicable.
- **UX/presentation quality** — UI-facing work captures baseline styling/layout,
  responsive behavior, accessibility, and readable loading/empty/error/validation states as
  measurable requirements or explicitly scopes them out.
- **Boundary contract quality** — externally visible APIs/events/files/SDKs/CLIs/webhooks
  define success and error shapes that consumers rely on, including validation vs. domain
  error variants when relevant.
- **Logging and telemetry acceptance** — externally relevant logs, events, metrics, traces,
  audit records, support IDs, correlation IDs, retention, redaction, and debugging signals
  are either expressed as requirements/acceptance criteria or explicitly scoped out.
- **Error-handling acceptance** — UI, API, domain, integration, infrastructure, validation,
  authorization, timeout, offline, and unexpected-failure behavior is either expressed as
  requirements/acceptance criteria or explicitly scoped out.
- **Release/deployment acceptance** — externally relevant artifact, environment, promotion,
  rollout, migration, rollback, smoke-check, operator-facing, or uptime constraints are
  either expressed as requirements/acceptance criteria or explicitly scoped out.
- **Documentation acceptance** — externally relevant user guidance, onboarding, help,
  API/developer reference, examples, runbooks, troubleshooting, release notes, migration
  notes, accessibility, freshness, or discoverability needs are either expressed as
  requirements/acceptance criteria or explicitly scoped out.
- **Acceptance quality** — tests are black-box, scenario-based, and verify the linked UC/FR/NFR
  rather than restating the requirement. They are requirements-level acceptance criteria,
  not unit/component/integration test designs.
- **Acceptance granularity by scope** — product/system `AT-` items are broad representative
  acceptance intent, feature/component `AT-` items refine bounded behavior, and
  slice/change `AT-` items are precise enough to map to executable acceptance/e2e/API tests
  or justified non-code verification.
- **Traceability and change readiness** — need → feature → use case → requirement → acceptance
  links support validation, impact analysis, and future revision.

## Report format

1. Mechanical scorecard (✅/❌ + IDs + totals).
2. Qualitative scorecard (1–5 + fixes).
3. **Top fixes** ranked by impact.
4. **Verdict**: Pass / Pass-with-fixes / Needs rework.

## Human review gate (hard stop)

After reporting the spec assessment verdict, **stop**. Do not start `/design-create` or any
downstream artifact in the same turn. The next stage requires explicit user approval or an
explicit unattended end-to-end instruction in the user's latest message.
