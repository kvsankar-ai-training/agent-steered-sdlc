---
description: Interview the user, then author a high-quality Software Requirements Specification grounded in stakeholder needs, use cases, supplementary requirements, scope, and traceability.
agent: agent
---

# Spec Create

Your job is to produce a **Software Requirements Specification (SRS)** grounded in
strong requirements-engineering practice: understand the problem first, capture real
stakeholder needs, derive features from those needs, express behavior through use cases,
capture cross-cutting qualities as supplementary/non-functional requirements, and maintain
traceability through acceptance tests. Produce a specification that can support validation,
design, planning, implementation, testing, and controlled change.

## Requirements principles

Use these principles throughout, inspired by Leffingwell/Widrig-style requirements
management and the requirements pyramid:

- **Problem before solution** — describe the business/user problem, stakeholders, and success
  conditions before proposing product behavior.
- **Stakeholder needs before features** — user needs express goals or pains in the problem
  domain; features are solution capabilities derived from those needs.
- **Non-goals prevent accidental scope creep** — explicitly state outcomes, features,
  audiences, platforms, qualities, or constraints that are intentionally out of scope.
- **Use cases for behavior in context** — use cases name actors, goals, preconditions, main
  success flow, alternatives/exceptions, and postconditions. They should describe observable
  interactions and value, not internal design.
- **Supplementary requirements for qualities and constraints** — performance, security,
  reliability, usability, interoperability, compliance, data retention, deployment, and other
  cross-cutting constraints belong in measurable NFRs unless they are specific to one use case.
- **Requirements state what, not how** — avoid architecture, UI layout, algorithms, database
  schema, and implementation choices unless they are true external constraints.
- **Manage scope deliberately** — record in-scope, out-of-scope, assumptions, open questions,
  priorities, and change-impact notes when revising.
- **Research current external facts when needed** — do not rely only on model memory for
  facts that may be current, specialized, regulated, market-dependent, standards-dependent,
  platform-specific, or vendor-specific.
- **Traceability enables validation and change control** — every item should connect from
  stakeholder need to feature, use case, requirement, and acceptance test.

## Test responsibility in this command

`/spec-create` defines **acceptance tests as requirements-level acceptance criteria**.
These `AT-` items are black-box, externally observable scenarios or quality checks that
state how stakeholders will know the requirement is satisfied. They are written in the spec,
not as executable test code.

Do not define unit tests, component tests, contract tests, integration tests, visual tests,
or other lower-level implementation tests here. Those belong downstream:

- `/design-create` chooses the appropriate test levels and testability strategy for each
  component, interface, quality attribute, and risk.
- `/plan-create` schedules which PR writes which executable tests, including which `AT-`
  items become executable acceptance tests.
- `/code-create` writes the executable tests: acceptance/e2e tests for `AT-` coverage and
  lower-level tests such as unit, component, contract, integration, accessibility,
  performance, security, migration, or operational checks as required by the design and plan.

## Work scope and readiness model

Every spec belongs to one of three work scopes. Do not invent deeper hierarchy unless the
repo already uses it:

- **Product/system** — broad problem, stakeholders, system boundary, major capabilities,
  major constraints, and broad acceptance intent. Usually **not code-ready**.
- **Feature/component** — coherent user-facing feature, technical component, subsystem, or
  integration. May be code-ready only when behavior is precise enough and downstream design
  and planning can identify implementable slices.
- **Slice/change** — the smallest implementable behavior change, bug fix, refactor with
  externally visible behavior, compliance update, or local technical change. This is the
  normal scope for code-ready work.

Record **Implementation Readiness** explicitly as one of:

- **Exploratory** — problem/scope is still being shaped; next step is more analysis/spec work.
- **Decomposable** — parent artifact is valid, but implementation requires child
  feature/component or slice/change artifacts before coding.
- **Code-ready** — requirements are precise enough for design/plan/code at the current scope.

A product/system or feature/component spec can pass review while marked **Decomposable**.
That is not a defect. It means the next step is breakdown, HLD/LLD, or child slice specs,
not direct implementation.

Infer the likely scope from the user's request and state it before writing. Broad asks such
as "build a Facebook clone" or "create an app/platform/system" normally map to
Product/system. A request for one capability, subsystem, integration, or UI area normally
maps to Feature/component. A bug fix, PR-sized change, compliance tweak, local refactor with
observable behavior, or explicitly named PR normally maps to Slice/change. Ask only when the
mapping is ambiguous or materially changes the artifact to produce.

## Lightweight exploratory track

For spikes, throwaway prototypes, exploratory data/ML work, proof-of-concept integrations,
or infrastructure investigations, do not force a full SRS. Write a lightweight exploratory
note instead when the user accepts that track. It must include: goal, timebox, assumptions,
non-goals, risks, experiment steps, expected evidence, disposal criteria, and the condition
that would trigger a normal product/system, feature/component, or slice/change spec. Mark it
`Implementation Readiness: Exploratory`; do not mark it Code-ready.

## Spec artifact types by scope

Use the same section order for every spec, but tune the content to the declared scope:

- **Product/system spec** carries the product mission, stakeholders, system boundary,
  product-level needs, non-goals, major capabilities/features, representative use cases,
  major NFRs and external constraints, broad acceptance intent, assumptions, risks, and a
  traceability map from needs to capabilities. It should usually be Exploratory or
  Decomposable and should identify child feature/component specs needed next.
- **Feature/component spec** carries the parent product references, feature/component goal,
  actors and users, concrete behavior/use cases, FRs/NFRs local to the feature/component,
  edge cases, integration or business rules, acceptance criteria, dependencies, non-goals,
  and traceability back to parent needs/features. It may be Decomposable or Code-ready
  depending on size and precision.
- **Slice/change spec** carries the precise requirement delta for one implementable change,
  parent IDs being refined or preserved, exact behavior and edge cases, changed FR/NFR/AT
  items, externally visible acceptance criteria or justified non-code verification, and
  explicitly unchanged behavior. It should normally be Code-ready before planning/code.

## Research and source grounding

During clarification, surface the option to search the Internet or official documentation
when external knowledge would materially improve the spec. Recommend research when the
requirements depend on current or niche facts such as laws/regulations, security standards,
accessibility standards, platform policies, API/vendor capabilities, pricing/quotas,
compliance obligations, device/browser support, industry workflows, competitor behavior, or
domain-specific terminology.

If the user asks for research, or if the spec would otherwise rest on uncertain external
facts, use available search/browsing tools and prefer primary sources: official docs,
standards bodies, laws/regulators, vendor documentation, or authoritative domain references.
Record source links and the facts they support in the relevant requirement text or in
**Assumptions & Open Questions**. If the user declines research, record any external-fact
assumptions explicitly.

## Scope: new, revision, product/system, feature/component, or slice/change spec

First determine the mode:

- **New product/system spec** — author the full document below, but keep readiness as
  Exploratory or Decomposable unless the work is genuinely small enough to implement from.
- **Revision** — a spec file already exists. Read it first, preserve all existing IDs
  (never renumber), and insert new items using the next gap number under the right slug.
  Update the traceability matrix and Assumptions to reflect changes.
- **Feature/component spec** — the user is specifying one feature, component, subsystem, or
  integration, not the whole product. Write a
  focused file (e.g. `specs/<slug>.md`) containing only the sections that apply. It may
  **reference** product-level IDs (e.g. an existing `UN-AUTH-10`) without redefining them;
  note the parent product spec path. Full-section presence is not required, but every
  use case and functional requirement you add must still have acceptance tests. Mark it
  Decomposable when it still needs child slices before implementation.
- **Slice/change spec** — the user is specifying a narrow code change, bug fix, refactor with
  externally visible behavior, compliance update, or implementation slice smaller than a
  full feature. Write a focused file (e.g. `specs/pr-<slug>.md` or
  `specs/change-<slug>.md`) that states the minimal requirement delta. Prefer referencing
  existing parent `UN-`/`FEAT-`/`UC-`/`FR-`/`NFR-` IDs instead of redefining them. Add only
  the new or changed requirements and acceptance tests needed to make the PR reviewable.
  If no requirement should change because the work is purely internal, say so explicitly
  and record the parent IDs whose behavior must remain unchanged.

## Step 1 — Clarify before writing (mandatory, one question per turn)

Do **not** write the spec until the problem, stakeholders, scope, behavior, constraints,
and acceptance basis are sufficiently understood.
Interview the user **one question at a time**: ask a single question, wait for the
answer, then ask the next. Never batch questions. Keep going until gaps close. Cover:

- **Problem analysis**: What problem is solved, what causes it, what happens if it remains
  unsolved, and what would count as success?
- **Research need**: Would current external research help define the domain, regulations,
  platform/vendor constraints, standards, or market expectations? If yes, search before
  finalizing the affected requirements.
- **Stakeholders and actors**: Who requests, uses, operates, supports, audits, or is affected
  by the system? What goals and concerns does each have?
- **Boundaries and scope**: What system or subsystem is being specified? What is explicitly
  in scope, out of scope, or deferred?
- **Work scope and readiness**: Is this product/system, feature/component, or slice/change
  scope? Is it Exploratory, Decomposable, or Code-ready? If it is slice/change-sized, what
  existing parent IDs does it refine or preserve?
- **User needs**: What outcomes do stakeholders need, independent of any proposed feature?
- **Non-goals**: What outcomes, audiences, platforms, integrations, qualities, features, or
  behaviors are intentionally not being solved now?
- **Features**: What externally visible capabilities satisfy those needs?
- **Use cases and scenarios**: What actor-goal flows, alternate paths, errors, and edge cases
  must be supported?
- **Supplementary/NFR constraints**: Performance, security, privacy, reliability, usability,
  accessibility, interoperability, compliance, data, platform, operational, and budget limits.
- **Priorities and risks**: Which needs/features are must-have vs. optional, risky,
  architecturally significant, or likely to change?
- **Acceptance criteria**: How will each important behavior and quality be verified?

If the user says "you decide" or leaves a gap, state your assumption explicitly and
list it in the Assumptions section. Keep asking until the remaining unknowns are either
resolved, explicitly deferred, or recorded as assumptions/open questions, then summarize
understanding and proceed.

## Step 2 — Numbering convention (apply everywhere)

Use **prefix slugs + zero-padded gap numbers** so items can be inserted later:

- Slug = feature/area name at a sensible level of abstraction (e.g. `AUTH`, `SEARCH`).
- Number in increments of 10: `10, 20, 30...`.
- Examples: `UN-AUTH-10` (user need), `FEAT-AUTH-10` (feature), `UC-AUTH-10` (use case),
  `FR-AUTH-10` (functional), `NFR-PERF-10` (non-functional), `AT-AUTH-10` (acceptance test).
- Every ID is unique and stable. Cross-references use IDs only.

## Step 3 — Author the spec with this exact section order

1. **Mission Statement** — a brief paragraph covering problem, stakeholders, value, and
   system boundary. Include explicit `Work Scope:` and `Implementation Readiness:` lines.
2. **User Needs** — numbered list (`UN-<SLUG>-<n>`), each a single stakeholder outcome or
   pain, phrased without solution mechanics.
3. **Non-Goals** — bullet list of explicit out-of-scope outcomes, audiences, platforms,
   integrations, features, quality targets, constraints, or future work. Reference related
   `UN-`/`FEAT-`/`UC-`/`FR-` IDs when a non-goal narrows them.
4. **Features** — numbered list (`FEAT-<SLUG>-<n>`), each an externally visible capability
   that cites the `UN-` it satisfies.
5. **Use Cases** — numbered (`UC-<SLUG>-<n>`), each expanding a feature with actor, goal,
   precondition, main success flow, alternates/exceptions, postcondition, and cited `FEAT-`.
6. **Functional Requirements** — numbered (`FR-<SLUG>-<n>`), atomic, testable system
   obligations that cite `UC-`/`FEAT-` and avoid design decisions.
7. **Non-Functional Requirements** — numbered (`NFR-<SLUG>-<n>`), measurable supplementary
   requirements and external constraints with thresholds, units, scope, and verification method.
8. **Acceptance Tests** — numbered (`AT-<SLUG>-<n>`), Given/When/Then or equivalent
   black-box acceptance criteria; each maps to a `UC-` and the `FR-`/`NFR-` it verifies.
   State the externally visible behavior or measurable quality to verify, not the internal
   unit/component/integration test mechanics.
9. **Traceability Matrix** — needs → non-goals/scope boundaries → features → use cases →
   requirements → acceptance tests, including priority/risk where known.
10. **Assumptions & Open Questions** — unconfirmed facts, source/research notes,
   out-of-scope/deferred items, priority trade-offs, and change-impact notes for revisions.

## Quality rules

- Every user need maps to ≥1 feature; every feature maps to ≥1 need.
- Work scope and implementation readiness are explicit and realistic. Broad parent specs
  are not mislabeled code-ready when they still require decomposition or child artifacts.
- Non-goals are explicit enough to prevent accidental implementation or acceptance-test scope.
- Every use case maps to ≥1 acceptance test; every requirement is testable.
- Each requirement is necessary, atomic, feasible, verifiable, unambiguous, and uses "shall".
- User needs and use cases stay in the problem/behavior domain; functional requirements state
  externally observable obligations; NFRs state measurable quality or constraint obligations.
- NFRs include numbers/units and a verification method where possible. No orphan or duplicate IDs.
- Avoid "etc.", "and/or", "TBD", "as appropriate", vague adjectives, hidden design decisions,
  unowned assumptions, and requirements that bundle multiple obligations.

## Step 4 — Verify before finishing

First run the deterministic structural checker and fix the document until it passes:

```pwsh
python checkers/check_spec.py spec.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry the same command
with `python3`; if that is unavailable, retry with `uv run python`.

For feature/component or slice/change specs, include `--feature --parent <product-spec>`.

Then run or perform the corresponding `/spec-review` against the completed spec. When
sub-agents are available, use fresh-context Mechanical Reviewer and Qualitative Reviewer
sub-agents as described in `/spec-review`; otherwise state that review is not independent and
use the adversarial posture. Treat any qualitative finding about problem framing, stakeholder
needs, non-goals, scope, use cases, requirements, NFRs, acceptance tests, assumptions, or
traceability as a defect in the spec. Revise the spec and repeat checker + review until
`/spec-review` would return Pass or an explicitly accepted Pass-with-fixes.

Write the spec to `spec.md` in the workspace unless the user names another file.
