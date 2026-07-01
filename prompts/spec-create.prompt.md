---
description: Interview the user, then author a high-quality Software Requirements Specification grounded in stakeholder needs, use cases, supplementary requirements, logging/error-handling, documentation/build/deploy needs, scope, and traceability.
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
  reliability, usability, interoperability, compliance, data retention, logging, telemetry,
  error handling, build/release, deployment, operability, and other cross-cutting constraints
  belong in measurable NFRs unless they are specific to one use case.
- **Documentation is a requirement when people depend on it** — user guidance, onboarding,
  help content, API/developer docs, examples, runbooks, troubleshooting, migration notes,
  and release notes belong in the spec when they affect adoption, safe use, support,
  operation, or integration.
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

Write `AT-` items at every spec scope, but match their granularity to that scope:

- **Product/system specs** carry broad, representative `AT-` intent for major capabilities,
  cross-cutting NFRs, build/release/deployment outcomes, and documentation outcomes. These
  often decompose before they become executable tests.
- **Feature/component specs** carry concrete `AT-` criteria for that bounded capability or
  subsystem, refining parent `AT-` intent without duplicating it.
- **Slice/change specs** carry precise `AT-` criteria for the exact implementable behavior
  delta, bug fix, migration, docs/build/deploy delta, or justified non-code verification.
  These are the `AT-` items most directly mapped to executable acceptance/e2e/API tests.

Do not define unit tests, component tests, contract tests, integration tests, visual tests,
or other lower-level implementation tests here. Those belong downstream:

- `/design-create` creates explicit `TEST-<AREA>-<NAME>` executable test obligations for
  unit/pure-core, component, contract, integration, UI/accessibility/visual,
  quality-attribute, migration, build/deploy, documentation, and operational checks as
  needed.
- `/plan-create` schedules which PR writes each executable test obligation, including which
  `AT-` items become executable acceptance/e2e/API tests.
- `/code-create` writes the executable tests: acceptance/e2e tests for `AT-` coverage and
  lower-level tests such as unit, component, contract, integration, accessibility,
  performance, security, migration, or operational checks for the assigned `TEST-`
  obligations required by the design and plan. It may also add scoped implementation-local
  supplemental inner tests discovered during TDD. If those tests reveal missing externally
  visible behavior, contract, UX/NFR, or scope, revise this spec instead of treating the
  behavior as code-only.

## Build, release, and deployment responsibility in this command

`/spec-create` captures externally relevant build, release, and deployment requirements, but
does not design the pipeline or write scripts. Treat build/deployment needs as requirements
when stakeholders care about them or when they constrain the product:

- Product/system specs state expected deployable artifact types, target environments,
  release/promotion model, rollout constraints, operational acceptance, and high-level
  deployability NFRs.
- Feature/component specs state feature-specific deployability, compatibility, migration,
  rollout, enablement/flagging, data-backfill, or environment constraints.
- Slice/change specs state the exact build/release/deployment delta, including any changed
  artifact, migration, configuration, rollout, rollback, smoke-check, or operator-visible
  behavior.

If deployment is intentionally out of scope, record that in **Non-Goals** or
**Assumptions & Open Questions** rather than leaving it implicit.

## User and developer documentation responsibility in this command

`/spec-create` captures documentation needs from the audience's point of view, but does not
design the documentation system or write final docs. Treat documentation as product scope
when users, developers, operators, support, auditors, or integrators need it to succeed:

- Product/system specs state documentation audiences, journeys, formats/channels,
  discoverability, localization/accessibility needs, developer onboarding expectations,
  API/reference needs, support/operations needs, and documentation acceptance criteria.
- Feature/component specs state feature-specific user guidance, help/error copy,
  developer/API examples, integration notes, configuration docs, runbooks, and migration or
  compatibility notes.
- Slice/change specs state the exact documentation delta: changed user behavior to explain,
  developer/API contract changes, README/tutorial updates, examples, release notes, runbook
  changes, troubleshooting notes, or explicitly unchanged documentation.

If user or developer documentation is intentionally out of scope, record that in
**Non-Goals** or **Assumptions & Open Questions** rather than leaving it implicit.

## Logging, telemetry, and error handling responsibility in this command

`/spec-create` captures externally relevant diagnostics and failure behavior as
requirements, but does not choose logging libraries or implementation mechanics. Treat these
as requirements when humans, agents, operators, support teams, auditors, or downstream
systems depend on them:

- Product/system specs state diagnostic audiences, high-level telemetry/observability
  goals, support/debugging expectations, privacy/redaction constraints, error categories,
  user-facing error behavior, and operational acceptance signals.
- Feature/component specs state feature-specific events, metrics, traces, correlation needs,
  log/audit expectations, fallback/degraded behavior, retry/recovery expectations, and
  human-readable error behavior.
- Slice/change specs state the exact logging/telemetry/error-handling delta: new or changed
  events/fields, redaction rules, correlation propagation, error mapping, retry/fallback
  behavior, user/API messages, and acceptance criteria or justified non-code verification.

If logging, telemetry, or error handling is intentionally out of scope, record that in
**Non-Goals** or **Assumptions & Open Questions** rather than leaving it implicit.

## User experience and boundary contract responsibility in this command

For products with a user interface or external integration boundary, capture user-visible
quality and contract expectations as requirements, not as implicit implementation taste.
Do not prescribe a detailed visual design system unless stakeholders require one, but do
state the externally observable quality bar:

- **Presentation and interaction quality**: baseline visual styling, layout density,
  responsive behavior, loading/empty/error states, readability, accessibility, and affordance
  clarity. If styling is intentionally minimal or deferred, record that as a Non-Goal or
  open question.
- **Human-readable feedback**: validation, domain, authorization, connectivity, and
  unexpected failures shall surface useful, safe, user-understandable text without leaking
  raw objects, stack traces, or implementation internals.
- **Diagnostics for humans and agents**: logs, telemetry events, metrics, traces, audit
  records, and support IDs should be useful for debugging, support, operations, and agentic
  follow-up while avoiding sensitive data, secrets, and unstable implementation details.
- **Boundary contracts**: public APIs, events, files, CLI outputs, webhooks, SDK calls, and
  generated clients shall define externally visible success and error shapes when consumers
  depend on them. Include known variant shapes, such as validation errors vs. domain errors,
  when they affect users or downstream implementers.
- **Contract acceptance**: acceptance criteria should include representative success,
  validation/error, empty/loading, and responsive/accessibility scenarios when those states
  are user-visible or integration-critical.

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

## Clarification and YOLO mode

Default behavior is input-gated: pause and ask one focused question at a time when missing
information would materially change the spec, scope, stakeholder needs, non-goals,
acceptance basis, constraints, or readiness. Do not silently fill important gaps.

The user may opt into **YOLO mode** with phrases such as "yolo", "use your judgment", "make
reasonable assumptions", or "proceed without questions". In YOLO mode, make the narrowest
reasonable product/spec decisions yourself, continue without blocking on normal
clarification questions, and record every material assumption, deferred question, trade-off,
and risk in the SRS. YOLO mode does not remove the requirement to stop for safety,
compliance, irreversible-scope, or contradictory-input issues that cannot responsibly be
assumed.

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
  major NFRs and external constraints, logging/telemetry and error-handling expectations,
  build/release/deployment expectations, user/developer documentation expectations, broad
  acceptance intent, assumptions, risks, and a traceability map from needs to capabilities.
  It should usually be Exploratory or Decomposable and should identify child
  feature/component specs needed next.
- **Feature/component spec** carries the parent product references, feature/component goal,
  actors and users, concrete behavior/use cases, FRs/NFRs local to the feature/component,
  edge cases, integration or business rules, logging/telemetry and error-handling
  constraints, build/release/deployment constraints, documentation constraints, acceptance
  criteria, dependencies, non-goals, and traceability back to parent needs/features. It may
  be Decomposable or Code-ready depending on size and precision.
- **Slice/change spec** carries the precise requirement delta for one implementable change,
  parent IDs being refined or preserved, exact behavior and edge cases, changed FR/NFR/AT
  items, logging/error-handling deltas, build/release/deployment deltas and documentation
  deltas when relevant, externally visible acceptance criteria or justified non-code
  verification, and explicitly unchanged behavior. It should normally be Code-ready before
  planning/code.

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
  (never rename just for neatness), and add new descriptive slug IDs under the right area.
  Update the traceability matrix and Assumptions to reflect changes.
- **Feature/component spec** — the user is specifying one feature, component, subsystem, or
  integration, not the whole product. Write a
  focused file (e.g. `specs/<slug>.md`) containing only the sections that apply. It may
  **reference** product-level IDs (e.g. an existing `UN-AUTH-ACCESS`) without redefining
  them; note the parent product spec path. Full-section presence is not required, but every
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

## Step 1 — Clarify before writing (mandatory unless YOLO, one question per turn)

Do **not** write the spec until the problem, stakeholders, scope, behavior, constraints,
and acceptance basis are sufficiently understood, unless the user explicitly enabled YOLO
mode and you can record reasonable assumptions.
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
  accessibility, interoperability, compliance, data, platform, logging/telemetry,
  error handling, operational, and budget limits.
- **User experience quality**: For UI-facing work, what baseline styling, layout,
  responsiveness, loading/empty/error states, accessibility, and human-readable feedback are
  expected? What is explicitly out of scope?
- **External contract expectations**: Which API/event/file/SDK/CLI/webhook success and
  error shapes are externally visible or consumed across a boundary? Which variants must be
  human-readable or contract-tested?
- **Logging, telemetry, and diagnostics**: What events, metrics, traces, audit records,
  support IDs, correlation IDs, retention/redaction rules, and agent/human debugging signals
  are required or explicitly out of scope?
- **Error handling and recovery**: Which UI, API, domain, integration, infrastructure,
  validation, authorization, timeout, offline, and unexpected-failure cases need user-facing
  messages, retries, fallback/degraded behavior, escalation, or auditability?
- **Build, release, and deployment needs**: What deployable artifact is expected; where it
  runs; how environments, promotion, rollout, rollback, migrations, approvals, smoke checks,
  and operator/user-visible release behavior should work; and which of those are in scope now.
- **User and developer documentation needs**: Which audiences need docs; what tasks,
  concepts, API/reference material, examples, onboarding, troubleshooting, release notes,
  runbooks, or help content they need; where those docs live; and how correctness,
  accessibility, freshness, and discoverability will be judged.
- **Priorities and risks**: Which needs/features are must-have vs. optional, risky,
  architecturally significant, or likely to change?
- **Acceptance criteria**: How will each important behavior and quality be verified?

If the user says "you decide", enables YOLO mode, or leaves a low-risk gap after being
asked, state your assumption explicitly and list it in the Assumptions section. Keep asking
until the remaining unknowns are either resolved, explicitly deferred, or recorded as
assumptions/open questions, then summarize understanding and proceed. In YOLO mode, prefer
proceeding with explicit assumptions over continuing the interview.

## Step 2 — ID convention (apply everywhere)

Use **descriptive slug-only IDs**. Do not use numeric suffixes.

- Format: `KIND-AREA-NAME`.
- `AREA` and `NAME` are uppercase slug tokens, 2-32 characters each, using `A-Z` and
  digits only after the first character.
- Use exactly two slug tokens after the kind; do not use internal hyphens or trailing
  numbers.
- Examples: `UN-AUTH-ACCESS` (user need), `FEAT-AUTH-LOGIN` (feature),
  `UC-AUTH-SIGNIN` (use case), `FR-AUTH-SIGNIN` (functional),
  `NFR-PERF-SIGNIN` (non-functional), `AT-AUTH-SIGNIN` (acceptance test).
- Every ID is unique and stable. Cross-references use IDs only.

## Step 3 — Author the spec with this exact section order

1. **Mission Statement** — a brief paragraph covering problem, stakeholders, value, and
   system boundary. Include explicit `Work Scope:` and `Implementation Readiness:` lines.
2. **User Needs** — list (`UN-<AREA>-<NAME>`), each a single stakeholder outcome or
   pain, phrased without solution mechanics.
3. **Non-Goals** — bullet list of explicit out-of-scope outcomes, audiences, platforms,
   integrations, features, quality targets, constraints, or future work. Reference related
   `UN-`/`FEAT-`/`UC-`/`FR-` IDs when a non-goal narrows them.
4. **Features** — list (`FEAT-<AREA>-<NAME>`), each an externally visible capability
   that cites the `UN-` it satisfies.
5. **Use Cases** — list (`UC-<AREA>-<NAME>`), each expanding a feature with actor, goal,
   precondition, main success flow, alternates/exceptions, postcondition, and cited `FEAT-`.
6. **Functional Requirements** — list (`FR-<AREA>-<NAME>`), atomic, testable system
   obligations that cite `UC-`/`FEAT-` and avoid design decisions.
7. **Non-Functional Requirements** — list (`NFR-<AREA>-<NAME>`), measurable supplementary
   requirements and external constraints with thresholds, units, scope, and verification
   method, including usability/presentation, human-readable feedback, boundary contract,
   logging/telemetry, error handling, build/release/deployment, documentation, and
   operational constraints when externally relevant.
8. **Acceptance Tests** — list (`AT-<AREA>-<NAME>`), Given/When/Then or equivalent
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
- Build/release/deployment expectations are either captured as requirements/acceptance
  criteria or explicitly deferred as non-goals/open questions.
- User/developer documentation expectations are either captured as requirements/acceptance
  criteria or explicitly deferred as non-goals/open questions.
- UI/presentation quality, loading/empty/error states, accessibility, and responsive behavior
  are either captured as measurable requirements/acceptance criteria or explicitly deferred
  as non-goals/open questions when the product has a UI.
- External boundary contracts, including success/error body shapes that consumers depend on,
  are captured as requirements/acceptance criteria or explicitly deferred as non-goals/open
  questions.
- Logging, telemetry, diagnostic, and support/debugging expectations are either captured as
  measurable requirements/acceptance criteria or explicitly deferred as non-goals/open
  questions.
- Error-handling expectations across UI, API, domain, integration, infrastructure, and
  unexpected-failure levels are captured as requirements/acceptance criteria or explicitly
  deferred as non-goals/open questions.
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

Then run or perform the corresponding `/spec-assess` against the completed spec. When
sub-agents are available, use fresh-context Mechanical Verifier and Qualitative Reviewer
sub-agents as described in `/spec-assess`; otherwise state that review is not independent and
use the adversarial posture. Treat any qualitative finding about problem framing, stakeholder
needs, non-goals, scope, use cases, requirements, NFRs, acceptance tests, assumptions, or
traceability as a defect in the spec. Revise the spec and repeat checker + assessment until
`/spec-assess` would return Pass or an explicitly accepted Pass-with-fixes.

Write the spec to `spec.md` in the workspace unless the user names another file.

## Step 5 — Human review gate (hard stop)

After writing or revising the spec and completing the checker/assessment loop above, **stop**.
Do not start `/design-create`, `/plan-create`, `/code-create`, or any downstream artifact in
the same turn.

End with a human-review handoff that includes:

- Spec path.
- Work Scope and Implementation Readiness.
- checker/assessment result.
- Key assumptions, open questions, and risks.
- Recommended next command, normally `/design-create` only after the user approves the spec.

Continue past this gate only if the user's latest message explicitly requested unattended
end-to-end continuation or explicitly approves the next stage.
