---
description: Interview the user, then author a high-quality Software Design Document grounded in requirements, stakeholder concerns, quality attributes, logging/error-handling, architecture/documentation/build/deploy views, interfaces, decisions, risks, and testability.
agent: agent
---

# Design Create

Your job is to produce a **Software Design Document (SDD)** that translates requirements
into an implementable, evolvable technical approach. The design should explain the system
boundary, major decisions, quality-attribute trade-offs, runtime behavior, data, interfaces,
deployment/operations concerns where relevant, tests, risks, and known technical debt.

## Design principles and concerns

Use these principles throughout, drawing from common architecture documentation practice
such as arc42, C4-style views, and SEI quality-attribute/attribute-driven design guidance:

1. **Requirements and stakeholder concerns drive design** — design choices trace to FRs,
   NFRs, use cases, constraints, stakeholder expectations, risks, or operational realities.
2. **Context before internals** — define the system boundary, external actors/systems,
   trust boundaries, integrations, and ownership before decomposing internals.
3. **Quality attributes are architectural drivers** — performance, availability,
   modifiability, security, privacy, usability, accessibility, observability, deployability,
   scalability, interoperability, and cost should be expressed as concrete scenarios and
   addressed with explicit tactics or trade-offs.
4. **Appropriate views, appropriate detail** — include static structure, runtime flows, data,
   build/package, deployment/infrastructure, documentation, and operational views only to
   the depth needed for the system's risk and complexity.
5. **High cohesion and low coupling** — components should have clear responsibilities,
   stable contracts, explicit dependencies, and minimal knowledge of each other's internals.
6. **Functional core, imperative shell** — identify pure decision logic, business rules,
   validation, policy, state transitions, calculations, and derived data separately from
   I/O, persistence, messaging, framework glue, navigation, time, randomness, device APIs,
   network calls, analytics, notifications, and other effects. The core should be easy to
   test deterministically; the shell should be thin, explicit, observable, and contract-tested.
7. **Interface-first collaboration** — APIs, events, schemas, protocols, error contracts,
   and diagnostic contracts are part of the design, not afterthoughts.
8. **Contract truth over convenient mocks** — tests and client adapters should use shared
   fixtures, generated clients, schemas, contract tests, or captured representative payloads
   from the documented boundary contract. Do not design tests around ad-hoc mock shapes that
   differ from the producer/consumer contract.
9. **Data and lifecycle awareness** — model data ownership, identity, consistency, retention,
   migrations, privacy/security classification, and failure/recovery behavior where relevant.
10. **Buildability, documentability, diagnosability, testability, and operability by design** — each
   component should have an isolation strategy, contract/integration test approach,
   build/package path, documentation owner and audience where relevant, structured
   logging/telemetry hooks, deployment checks, and operational checks.
11. **Decisions carry rationale and consequences** — record alternatives considered,
    why the chosen option fits now, rejected options, trade-offs, and expected change points.

## Research and source grounding

During clarification, surface the option to search the Internet or official documentation
when external knowledge would materially improve the design. Recommend research when design
choices depend on current or specialized facts such as framework/runtime behavior, cloud or
vendor capabilities, service limits and quotas, security guidance, accessibility guidance,
mobile/browser/platform policies, protocol standards, deployment constraints, pricing/cost
drivers, operational best practices, or library/tool maturity.

If the user asks for research, or if the design would otherwise rest on uncertain external
facts, use available search/browsing tools and prefer primary sources: official framework or
vendor docs, standards bodies, security advisories, platform guidelines, and authoritative
architecture references. Record source links and the facts they support in **Drivers &
Constraints**, **Tech Stack**, **Design Decisions**, ADRs, or **Risks & Trade-offs**. If the
user declines research, record any external-fact assumptions explicitly.

## Trade-off and ADR workflow

Architecture decisions are part of the deliverable, not side notes.

- As you clarify and design, actively surface consequential trade-offs: simplicity vs.
  flexibility, latency vs. consistency, build speed vs. operability, framework leverage vs.
  lock-in, abstraction vs. directness, client vs. server responsibility, local vs. remote
  state, synchronous vs. asynchronous flow, managed service vs. self-hosted component, and
  short-term delivery vs. long-term changeability.
- For each material decision, name the decision point, list at least two viable options,
  identify the affected FRs/NFRs/UCs and quality attributes, and explain consequences,
  risks, reversibility, and what would cause the decision to be revisited.
- If the decision changes scope, cost, user experience, operational responsibility, security,
  privacy, reliability, data ownership, or future migration effort, ask the user for input
  **one question at a time** before finalizing it. Do not silently choose on the user's behalf
  unless the user explicitly delegates the choice or enables YOLO mode; if delegated, record
  the assumption, rationale, risk, and revisit trigger.
- Create or update Architecture Decision Records (ADRs) for material decisions. Use
  `docs/adr/ADR-<SLUG>.md` unless the repo already has an ADR location or naming convention.
  Each ADR should include: status, context, decision, options considered, consequences,
  affected requirements/design IDs, risks, and revisit triggers.
- Keep `design.md` and ADRs synchronized: every `DEC-<SLUG>` in **Design Decisions** should
  link or refer to its ADR when one exists, and each ADR should reference the corresponding
  `DEC-<SLUG>`.
- For small/local choices, keep the rationale directly in `design.md`; for decisions that
  shape architecture, quality attributes, delivery sequence, operations, or long-term
  evolution, write an ADR.

## Design quality heuristics

Use these as practical review lenses, not as dogma. Apply them where they improve the
design's ability to satisfy requirements and quality attributes:

- **Single responsibility / cohesion** — each component has one clear primary purpose and
  one main reason to change.
- **Low coupling** — components depend on stable contracts, not each other's internals.
- **Information hiding / encapsulation** — volatile decisions, data structures, policies,
  and external-system details are hidden behind clear interfaces.
- **Separation of concerns** — domain policy, orchestration, I/O, persistence, presentation,
  and operations concerns are separated where that lowers risk or improves changeability.
- **Acyclic dependency direction** — dependencies point toward stable abstractions and do not
  create accidental cycles.
- **Explicit contracts** — APIs, events, schemas, and protocols define inputs, outputs,
  errors, ownership, compatibility, and quality expectations.
- **Design for testability** — isolate decisions, side effects, time, randomness, external
  services, and persistence so behavior can be verified at the right level.
- **Least sufficient mechanism / YAGNI** — avoid abstractions, distribution, configurability,
  or frameworks not justified by current drivers or credible change scenarios.
- **Useful DRY** — remove duplication that creates maintenance or correctness risk; avoid
  over-abstracting code or components that only look superficially similar.
- **Fail safely** — define error handling, recovery, degraded behavior, and observability for
  important failure modes.
- **User-visible boundary adaptation** — isolate translation of backend/API/domain errors,
  validation results, empty data, loading state, and integration failures into safe
  human-readable UI or API-facing messages at a single clear boundary.
- **Mock before commitment when requested** — if the spec records `UI Mock Preference:
  Required`, create or update a mock UI companion before downstream planning or production
  UI implementation. Treat user approval of that mock as a hard gate.
- **Diagnostic signal without leakage** — design logs, metrics, traces, audit records, and
  support IDs so humans and agents can debug and operate the system without exposing
  secrets, regulated data, stack traces, or unstable internals.

## Test responsibility in this command

`/design-create` does not write executable tests. It defines the **test architecture**:
which kinds of tests are needed, where they sit in the system, what each level proves, and
which components, interfaces, flows, risks, and NFRs they cover.

Use the spec's `AT-` items as acceptance intent. Decide how those acceptance criteria will
be verified later, such as API acceptance tests, browser/device end-to-end tests,
workflow-level integration tests, or operational/NFR checks. Also define lower-level tests
that do not appear in the spec but are needed for safe implementation:

- **Pure core/unit tests** for business rules, validation, calculations, state transitions,
  reducers, mappers, policies, and edge cases.
- **Component/module tests** for cohesive components behind stable interfaces.
- **Contract tests** for APIs, events, schemas, DTOs, protocols, compatibility, and error
  behavior between owners and consumers.
- **Integration tests** for persistence, messaging, external services, framework wiring,
  transactions, migrations, auth, caching, retries, and adapters.
- **UI tests** such as component/widget tests, accessibility checks, visual regression, and
  route/navigation interaction tests where relevant.
- **End-to-end or acceptance tests** for critical user journeys and `AT-` scenarios, kept
  focused enough to avoid duplicating all lower-level coverage.
- **Quality-attribute tests/checks** for performance, reliability, security, privacy,
  accessibility, observability, resilience, offline/sync, build/package reproducibility,
  deployment validation, migration/rollback, and operations.
- **Documentation checks** for user guidance, developer onboarding, API/reference output,
  examples, diagrams, runbooks, troubleshooting, accessibility/readability, links, generated
  docs, and versioned release/migration notes.

Document this as explicit test obligations in **Test Strategy**. Use
`TEST-<AREA>-<NAME>` IDs for every executable lower-level or workflow test obligation that
must survive into the plan. For each `TEST-` item, state the test kind, purpose,
owner/component or interface, linked `FR-`/`NFR-`/`UC-`/`AT-`/`COMP-`/`IFACE-`/`RISK-`/
`DEC-`, **verification oracle**, required doubles or environments, expected speed/scope,
and whether `/code-create` should implement it in the PR that introduces the behavior or
defer it to a specific later PR.

The verification oracle is the observable evidence that proves pass/fail. Choose the
strongest practical oracle for the test level: return values, state transitions, persisted
records, emitted events, API responses, DOM/role/text output, accessibility tree, screenshots
or visual baselines, generated files/artifacts, metrics, structured logs, traces, deployment
status, or external calls captured through a test double. Logs, screenshots, and metrics are
valid oracles when they are the behavior under test or the best observable evidence, but
avoid using them as vague substitutes for direct assertions when direct state/output can be
checked.

`AT-` items remain requirements-level acceptance criteria from the spec. `TEST-` items are
design-level executable test obligations: unit/pure-core, component, contract, integration,
UI/accessibility/visual, quality-attribute, migration, build/deploy, documentation, and
operational checks. An executable acceptance/e2e/API test may cite both the `AT-` it proves
and the `TEST-` obligation that planned it.

For boundary-facing work, at least one `TEST-` obligation should verify representative real
producer/consumer payloads for success and error cases unless the boundary is explicitly
out of scope. Prefer shared fixtures, generated schemas/clients, OpenAPI/AsyncAPI examples,
consumer-driven contract tests, or integration tests over hand-written mocks that invent a
different shape.

For UI-facing products where the spec says `UI Mock Preference: Required`, create or update
a mock UI companion such as `mock-ui.html` unless the repo already has an established mock
location. The mock should show representative screens, navigation, major states, empty/
loading/error/validation states, key copy, and responsive considerations at the fidelity the
user requested. This mock is not production code and should avoid backend behavior. After
creating or materially revising it, stop for human approval before `/plan-create` or
production UI implementation.

## Work scope, design depth, and readiness

Every design belongs to one of three work scopes:

- **Product/system** — high-level design (HLD): context, major components, architectural
  drivers, major decisions, boundaries, risks, quality strategy, and decomposition direction.
  This normally produces a valid design that is **not code-ready**.
- **Feature/component** — feature or component design: behavior, interfaces, flows, data,
  responsibilities, contracts, risks, and test strategy for a coherent subsystem. It may be
  code-ready only if small enough and locally precise enough.
- **Slice/change** — low-level design (LLD) for an implementable slice/change: local
  components, contracts, state, algorithms/policies, failure cases, data changes, test
  levels, and touchable modules/files sufficient for planning and implementation.

Record **Implementation Readiness** explicitly as:

- **Exploratory** — design problem/options are still being shaped.
- **Decomposable** — parent HLD or feature/component design is valid, but implementation
  requires child slice/change designs or a breakdown plan.
- **Code-ready** — local design is sufficiently detailed for an implementation plan and
  `/code-create`.

A product/system HLD can pass design review while marked Decomposable. Do not inflate an
HLD into an LLD just to make it code-ready; instead identify the child feature/component or
slice/change designs needed next.

Infer the likely scope from the user's request and state it before writing. Broad asks such
as "build a Facebook clone", "design the platform", or "define the architecture" normally
map to Product/system HLD. A request for one capability, subsystem, bounded context,
integration, service, screen family, or module normally maps to Feature/component design. A
bug fix, PR-sized behavior change, local refactor, API/schema delta, or explicitly named PR
normally maps to Slice/change LLD. Ask only when the mapping is ambiguous or materially
changes the artifact to produce.

## Clarification and YOLO mode

Default behavior is input-gated: pause and ask one focused question at a time when missing
information would materially change the system boundary, architectural drivers,
quality-attribute trade-offs, interfaces, data ownership, runtime behavior, ADRs, test
strategy, or readiness. Do not silently choose consequential design options.

The user may opt into **YOLO mode** with phrases such as "yolo", "use your judgment", "make
reasonable assumptions", or "proceed without questions". In YOLO mode, make the narrowest
reasonable design decisions yourself, continue without blocking on normal clarification
questions, and record every material assumption, trade-off, rejected option, risk, and
revisit trigger in `design.md` and ADRs as appropriate. YOLO mode does not bypass upstream
spec blockers, code-readiness limits, safety/security/compliance issues, or the requirement
to surface major trade-offs in the final artifact.

## Lightweight exploratory track

For spikes, throwaway prototypes, exploratory data/ML work, proof-of-concept integrations,
or infrastructure investigations, do not force a full SDD. Write a lightweight design note
when the user accepts that track. It must include: goal, timebox, assumptions, non-goals,
risks, experiment architecture, evidence to collect, disposal/productionization criteria,
and what follow-up HLD/feature design/LLD would be needed before production code. Mark it
`Implementation Readiness: Exploratory`; do not mark it Code-ready.

## Design artifact types by scope

Use the same section order for every design, but tune the content to the declared scope:

- **Product/system design (HLD)** carries system context, major containers/services/modules,
  architectural drivers, key quality-attribute tactics, system and trust boundaries, major
  data ownership, integration strategy, logging/telemetry strategy, error-handling strategy,
  build/package/release strategy, deployment/operations strategy, documentation strategy,
  material decisions/ADRs, risks, decomposition candidates, and a system-level test strategy.
  It should explain how the system will be divided, not specify every local algorithm or file.
- **Feature/component design** carries component responsibilities, interfaces/contracts,
  local data/state ownership, runtime flows, functional-core/imperative-shell partition,
  dependencies, UX/API contracts, logging/telemetry and error-handling impacts,
  build/release/deployment impacts, feature-level documentation impacts, decisions/ADRs,
  risks, and explicit `TEST-` obligations for that feature/component. It should identify
  any child slice/change LLDs still required.
- **Slice/change design (LLD)** carries the exact local design needed for implementation:
  touched components/modules, API/schema/data changes, detailed happy and failure flows,
  validation/policy logic, core-vs-shell placement, logging/telemetry deltas,
  error-handling and recovery paths, migration/rollback concerns, side effects,
  build/deployment script or artifact changes, documentation changes, planned test
  levels/doubles, and likely file/module touch candidates.

## Design profiles and candidate sections

Use the exact top-level section order in Step 3 for machine-checkability, but adapt the
contents to the kind of system being designed. Include the relevant artifacts below as
subsections, tables, or diagrams inside the matching top-level sections.

### Universal minimum artifacts

Every non-trivial design should include:

- **Context view** — actors, external systems, trust boundaries, and system boundary.
- **Static structure view** — layers/components/modules and their dependencies.
- **Interface contract view** — APIs, events, schemas, protocols, or callable interfaces.
- **Runtime view** — sequence diagrams or equivalent flow diagrams for critical paths and
  important failure/alternate paths.
- **State/data view** — persisted data, ownership, state machines, consistency, retention,
  or an explicit statement that no persistent state exists.
- **Functional-core/imperative-shell map** — pure logic vs. side-effecting adapters, with
  test strategy for each.
- **Quality-attribute tactics** — how the design meets the important NFRs and constraints.
- **Build/release/deployment view** — deployable artifacts, package boundaries, CI/CD or
  release workflow, environment promotion, configuration/secrets, migrations, rollout,
  rollback, smoke checks, and ownership.
- **Documentation view** — user docs, developer docs, API/reference docs, examples,
  tutorials, diagrams, runbooks, troubleshooting, doc generation, versioning, publishing
  path, ownership, and review/update triggers.
- **Logging/telemetry view** — log/event/metric/trace/audit records, correlation IDs,
  support/debug IDs, sinks, retention, sampling, redaction/privacy rules, alert hooks, and
  how humans and agents consume the signals.
- **Error-handling view** — UI/API/domain/integration/infrastructure error categories,
  mapping boundaries, user-facing messages, retry/fallback/degraded behavior, escalation,
  and safe failure defaults.
- **Traceability and tests** — requirements to components/interfaces/decisions/tests.

### Backend / API / service design

Candidate design contents:

- **System context**: actors, upstream/downstream systems, trust boundaries, data/control flow.
- **Container/service architecture**: deployable units such as services, workers, queues,
  databases, caches, object stores, third-party systems, and communication paths.
- **Components/modules**: packages, layers, ports/adapters, domain services, repositories,
  clients, jobs, middleware, and dependency direction.
- **Functional core / imperative shell**: domain rules, validation, policies, state transitions,
  and calculations in the core; HTTP/RPC handlers, persistence, messaging, clocks, retries,
  transactions, and framework glue in the shell.
- **API/event contracts**: HTTP/RPC endpoints, commands/events, schemas, auth, errors,
  idempotency, pagination, versioning, compatibility, representative success/error examples,
  and OpenAPI/AsyncAPI references where useful.
- **Data model and state**: entities, relationships, ownership, lifecycle/state machines,
  migrations, indexes, retention, consistency, transactions, and cache behavior.
- **Runtime flows**: sequence diagrams for core use cases, failure paths, retries, async/event
  flows, background jobs, and cross-service interactions.
- **Deployment and operations**: environments, configuration, secrets, health checks,
  observability, alerts, backups, scaling, rollout/rollback, and runbooks.
- **Build/release pipeline**: container images, packages, generated clients, database
  migration bundles, artifact registry, versioning, SBOM/provenance where needed, CI/CD
  stages, environment promotion, and deploy validation.
- **Developer documentation**: API reference/OpenAPI/AsyncAPI, SDK/client examples,
  local-dev setup, configuration reference, architecture notes, runbooks, troubleshooting,
  and compatibility/migration guidance.
- **Backend test strategy**: core unit tests, contract tests, integration tests, migration tests,
  performance/security/resilience tests, and end-to-end tests.

Minimum backend artifacts: context diagram, container/service diagram, component/module
diagram, API/event contract table or formal spec reference, data model diagram/table,
sequence/runtime diagrams, build/release view, deployment/ops view, developer-docs view,
and component-to-test matrix.

### Web frontend / SPA design

Candidate design contents:

- **Frontend scope and journeys**: user journeys, pages, layouts, UI responsibilities, and
  browser/runtime assumptions.
- **Route/page structure**: route map with URL, page owner component, layout, auth rule,
  route params, query params, deep-link behavior, loading UI, and error UI.
- **UX flows and interaction states**: primary/alternate flows, empty states, validation,
  confirmations, destructive actions, recovery paths, and offline/stale-data behavior.
- **Component hierarchy**: page/layout/feature/shared/form/dialog components and ownership.
- **State management**: local UI state, form state, URL state, global client state,
  server/cache state, derived state, and stored state.
- **Functional core / imperative shell**: pure validation, formatting, filtering, derivation,
  authorization/permission checks, and reducers in the core; routing, network calls, browser
  storage, timers, analytics, mutations, and DOM/browser APIs in the shell.
- **Data fetching and API contracts**: API schemas, cache keys, freshness, retries, pagination,
  optimistic updates, mutation invalidation, authorization behavior, error-body variants,
  and the source of truth for test fixtures or generated clients.
- **Presentation approach**: global stylesheet, design tokens, component library, utility
  CSS, or native platform conventions; layout grid/spacing/typography strategy; responsive
  breakpoints; and what styling is deliberately out of scope.
- **Mock UI artifact**: when required by the spec, `mock-ui.html` or the established mock
  artifact showing representative pages, key states, navigation, copy, and responsive
  behavior for user approval.
- **Error normalization boundary**: where backend/domain/network/validation error shapes
  are mapped into safe human-readable display messages, how multi-field validation errors
  are attributed, and which raw details are logged vs. shown.
- **Loading/error/empty/accessibility/responsive states**: matrices for important components
  and routes, including focus management, keyboard behavior, ARIA/semantic HTML, contrast,
  target size, breakpoints, touch behavior, and content priority.
- **Frontend performance and security**: bundle boundaries, lazy loading, rendering hotspots,
  image/media strategy, token/storage policy, sensitive data handling, and privacy events.
- **Frontend build and release**: build tool command, static/server-rendered artifact,
  environment injection, feature flags, CDN/cache invalidation, asset fingerprinting,
  preview/staging deployment, release promotion, rollback, and smoke checks.
- **User and developer documentation**: in-product help, error/empty-state guidance,
  user guide/tutorial changes, design-system/component usage docs, route behavior notes,
  integration examples, accessibility notes, analytics event docs, and release notes.
- **Frontend test strategy**: pure function tests, component tests, accessibility checks,
  contract-realistic API integration tests using shared fixtures/generated clients/schemas,
  visual tests where useful, and E2E tests for critical journeys. Prefer role/text/semantic
  selectors; do not couple tests to CSS class names unless styling itself is under test.

Minimum web frontend artifacts: route map, component hierarchy diagram, UX flow diagram,
state model/table, data/API contract table, loading/error/empty state matrix, accessibility
checklist, responsive behavior matrix, presentation approach, mock UI artifact when required,
error-normalization boundary, build/release notes, documentation notes, and test traceability
matrix.

### Mobile app design

Candidate design contents:

- **Mobile platform scope**: target platforms, OS/version floor, form factors, native vs.
  cross-platform framework, device constraints, localization, and store/release constraints.
- **Navigation model**: navigation graph, tabs/stacks/modals/deep links, back behavior,
  auth/onboarding routes, and invalid-route handling.
- **Screen inventory and UI contracts**: screen purpose, inputs, visible states, actions,
  empty/loading/error states, accessibility labels, analytics events, and platform variations.
- **State and data flow**: UI state, session/app state, domain state, ownership, persistence,
  state restoration, and data-source boundaries.
- **Functional core / imperative shell**: pure business rules, validation, reducers, mappers,
  sync decisions, and policy logic in the core; platform I/O, navigation, local storage,
  permissions, notifications, sensors, background work, and device APIs in adapters.
- **Offline/cache/sync**: local and remote data sources, sync triggers, conflict resolution,
  retry/idempotency strategy, stale data behavior, and background sync limits.
- **Permissions, privacy, and platform capabilities**: permission matrix, fallback when denied,
  data collected, retention/sharing, camera/location/Bluetooth/biometrics/push/widgets/share
  sheets/background tasks/files/payments/contacts as applicable.
- **Lifecycle and background behavior**: launch, foreground, background, termination,
  interruptions, resume, token refresh, background execution, notification taps, and recovery.
- **Performance, battery, and resource budgets**: startup, frame/rendering budget, memory,
  network use, background work, and battery-sensitive scheduling.
- **Mobile build and release**: signing, build flavors/schemes, app identifiers, store or
  enterprise distribution, OTA/update policy if applicable, environment configuration,
  feature flags, staged rollout, rollback/kill-switch strategy, and release smoke checks.
- **Mobile user/developer documentation**: onboarding/help copy, permission rationale,
  troubleshooting, support articles, deep-link/API integration notes, platform variation
  notes, store release notes, and operator/support runbooks.
- **Mobile test strategy**: core unit tests, widget/component tests, navigation/data-flow
  integration tests, device/emulator tests, accessibility tests, permission-denied tests,
  offline/sync tests, lifecycle/background tests, and release-health checks.

Minimum mobile artifacts: core/adapters component diagram, navigation graph, screen/state
table, offline/sync diagram when remote data exists, permission/capability matrix,
lifecycle/background table, performance budget, mock UI artifact when required,
build/release plan, documentation plan, and test strategy matrix.

### OO / UML-heavy design

When the implementation style is object-oriented or the user asks for UML-style design,
include the modern equivalents of the classic minimum set:

- **Logical component/package view**: packages/modules/components and dependency direction.
- **Class/domain model**: key classes/entities/value objects, responsibilities, associations,
  inheritance/composition where meaningful, and invariants.
- **Sequence diagrams**: object/component interactions for critical use cases and failure paths.
- **State diagrams**: lifecycle/state machines for important entities, workflows, or protocols.
- **Interface contracts**: public methods, events, DTOs, errors, and ownership.

Do not generate exhaustive UML for its own sake; include diagrams that clarify responsibilities,
collaboration, state, and change risk.

## Scope: new, revision, HLD, feature/component design, or slice/change LLD

First determine the mode:

- **New product/system design (HLD)** — author the full document below at architecture depth;
  mark readiness Exploratory or Decomposable unless it truly contains implementation-ready
  local detail.
- **Revision** — a design file exists. Read it first, preserve all existing IDs (never
  rename just for neatness), add new descriptive slug IDs, and update the traceability matrix.
- **Feature/component design** — designing one feature, component, subsystem, or integration,
  not the whole product. Write a focused file (e.g. `designs/<slug>.md`) with only the
  sections that apply. It may **reference** product-level IDs without redefining them; note
  the parent design path. Mark it Decomposable if it still needs slice/change LLDs.
- **Slice/change LLD** — designing one implementable slice or local change. Include enough
  local behavior, interfaces, data, failure cases, test levels, and implementation constraints
  for `/plan-create` to produce a code-ready implementation plan.

## Step 1 — Clarify before writing (mandatory unless YOLO, one question per turn)

If a spec (`spec.md`) exists, read it first — the design must satisfy its FRs/NFRs/UCs.
Do **not** write the design until the system boundary, drivers, quality-attribute scenarios,
interfaces, data, runtime behavior, and verification approach are sufficiently understood,
unless the user explicitly enabled YOLO mode and you can record reasonable assumptions.
Interview the user **one question at a time**: ask, wait, then ask the next. Cover:

- **Stakeholders and concerns**: who needs to understand, build, run, secure, evolve, or
  integrate with the design, and what do they care about?
- **Research need**: Would current external research help choose technologies, understand
  platform/vendor constraints, validate security/accessibility guidance, confirm service
  limits, or compare architectural options? If yes, search before finalizing affected decisions.
- **Design profile**: backend/API/service, web frontend, mobile app, desktop, library/SDK,
  data/ML pipeline, infrastructure, OO/UML-heavy component, or mixed system. Select the
  profile-specific artifacts that apply.
- **Mock UI gate**: For UI-facing work, does the spec require a mock UI? If yes, confirm the
  fidelity, screens, states, flows, and approval owner before finalizing downstream design.
- **Work scope and readiness**: Is this product/system HLD, feature/component design, or
  slice/change LLD? Is it Exploratory, Decomposable, or Code-ready?
- **Context and boundaries**: system scope, external actors/systems, trust boundaries,
  data ownership, integration protocols, and deployment/operational environment.
- **Architectural drivers**: which FRs, NFRs, use cases, constraints, risks, and quality
  attribute scenarios shape the design?
- **Tech stack and constraints**: language(s), runtime, frameworks, datastore, messaging,
  infrastructure, third-party services/libraries, versions, licensing, and organizational constraints.
- **Decomposition and views**: layers, components, containers/services/modules, deployment
  units, runtime flows, data model, and cross-cutting concepts.
- **Build, release, and deployment architecture**: build commands, artifact/package types,
  artifact storage, CI/CD or release workflow, environments, promotion rules,
  configuration/secrets, migrations, rollout/rollback, smoke checks, and ownership.
- **User and developer documentation architecture**: doc audiences, information architecture,
  source locations, generated vs. hand-written docs, API/reference generation, examples,
  diagrams, publishing/versioning, ownership, review triggers, and doc validation checks.
- **Logging, telemetry, and diagnostics architecture**: structured log fields, event names,
  metrics, traces, audit records, correlation/support IDs, sinks, retention, sampling,
  redaction/privacy rules, alert hooks, and how humans or agents will use the signals.
- **Error-handling architecture**: error categories by UI, API, domain, integration,
  infrastructure, validation, authorization, timeout, offline, and unexpected-failure level;
  mapping boundaries; retry/fallback/degraded behavior; escalation; and safe user/API
  messages.
- **State and side effects**: pure decision logic, persistence, I/O, external calls, time,
  randomness, transactions, concurrency, retries, idempotency, and consistency boundaries.
- **Interfaces and contracts**: APIs, events, commands, schemas, protocols, auth, errors,
  compatibility/versioning, ownership, representative payload examples, and fixture/schema
  source of truth for tests.
- **Quality tactics and trade-offs**: how the design meets performance, reliability,
  security, modifiability, usability, observability, diagnosability, deployability, build
  reproducibility, deployment, and cost goals.
- **Decision points**: what trade-offs require user input, what options are viable, which
  option is recommended, and whether an ADR is needed.
- **Test and verification strategy**: how components, contracts, quality attributes, data
  migrations, failure modes, and critical flows are verified.
- **Risks and evolution**: technical debt, migration path, rollout/rollback, likely change
  points, and alternatives rejected.

State assumptions explicitly in Risks/Trade-offs, Design Decisions, or ADRs. Keep asking
until remaining unknowns and material trade-offs are resolved, deliberately deferred, or
recorded with impact. In YOLO mode, prefer proceeding with explicit design assumptions over
continuing the interview, while still surfacing high-impact trade-offs in the artifact.

## Step 2 — ID convention (apply everywhere)

Use **prefix + slug**, no numeric suffix:

- Slug = component/area name (e.g. `AUTH`, `CORE`). One entity per slug, so no `-N` suffix.
- `LAYER-<SLUG>` (layer), `COMP-<SLUG>` (component), `IFACE-<SLUG>` (interface),
  `DEC-<SLUG>` (design decision), `RISK-<SLUG>` (risk). IDs are unique and stable.
- `TEST-<AREA>-<NAME>` identifies an executable test obligation owned by the design, such
  as `TEST-AUTH-POLICY`, `TEST-AUTH-CONTRACT`, or `TEST-RETR-EMPTYQUERY`.
- Components cite the slug-only `FR-<AREA>-<NAME>`, `NFR-<AREA>-<NAME>`, and
  `UC-<AREA>-<NAME>` IDs from `spec.md` they realize.

## Step 3 — Author the design with this exact section order

1. **Overview** — what is being built, system boundary/context, principal stakeholders,
   and architectural style/strategy in one paragraph. Include explicit `Work Scope:`,
   `Design Depth: HLD | feature/component design | LLD`, and `Implementation Readiness:`
   lines.
2. **Tech Stack** — chosen language(s), runtime, frameworks, datastore, and key libraries,
   infrastructure/services, external dependencies, and rationale tied to drivers/NFRs. Note
   versions, licensing, build tooling, package/artifact formats, documentation tooling,
   hosting, or organizational constraints where they matter.
3. **Drivers & Constraints** — the FRs/NFRs/use cases, quality-attribute scenarios,
   stakeholder concerns, logging/telemetry/error-handling constraints, build/release/
   deployment constraints, documentation constraints, UI mock preference/approval status,
   external constraints, risks, and assumptions that shape the design.
4. **Layers** — (`LAYER-<SLUG>`); each names its responsibility, allowed dependencies,
   boundary rules, ownership, and whether it belongs to core policy, application orchestration,
   adapter/shell, presentation, data, or infrastructure. Dependencies should be acyclic and justified.
5. **Components** — (`COMP-<SLUG>`); responsibility, layer, dependencies
   (by `IFACE-`), state/side-effect profile, lifecycle, scaling/deployment notes where
   relevant, core/shell classification, and the `FR-`/`NFR-`/`UC-` it realizes. Include a
   **component / association diagram** (Mermaid `flowchart` or `classDiagram`) showing
   layers, components, dependency arrows, and core-vs-shell boundaries.
6. **Interfaces** — (`IFACE-<SLUG>`); contract, inputs/outputs, `owner: COMP-<SLUG>`,
   protocol/schema, auth/trust boundary, error behavior, diagnostic/correlation fields,
   versioning/compatibility, and QoS expectations where relevant. For boundary contracts,
   include representative success and error payload shapes or cite the formal schema/example
   source that tests must use.
7. **Core vs. Shell** or **Core vs. Shell / Equivalent Separation** — include a table that classifies each `COMP-` as pure core,
   application/orchestration, adapter/shell, presentation, data, infrastructure, or mixed.
   For the core, list pure decisions, rules, validation, state transitions, calculations,
   reducers, mappers, and invariants. For the shell, list I/O, persistence, network calls,
   UI/navigation, device/browser APIs, framework glue, clocks, randomness, transactions,
   retries, messaging, analytics, notifications, logging, telemetry, and observability.
   Explain how dependencies point inward or through interfaces, how side effects are
   isolated, and how each category is tested.
   If the architecture does not use this terminology, use the equivalent section title and
   explain the equivalent separation or why the split is not applicable.
8. **Key Flows** — a **sequence diagram** (Mermaid `sequenceDiagram`) per critical use
   case, quality-attribute scenario, failure path, or integration flow, showing how components
   and interfaces collaborate over time.
9. **Data Model** — a **database schema diagram** (Mermaid `erDiagram`) of entities,
   keys, relationships, ownership, consistency, retention, privacy/security classification,
   migrations, and recovery behavior for any persisted state.
10. **Design Decisions** — (`DEC-<SLUG>`); decision, alternatives considered, user input
   received or assumption made, rationale, quality attributes affected, consequences,
   reversibility, ADR link/path when applicable, and expected revisit triggers.
11. **Test Strategy** — list explicit `TEST-<AREA>-<NAME>` obligations in a matrix covering
   acceptance/e2e, integration, contract, component/module, unit/pure-core,
   UI/accessibility/visual, migration, operational, and quality-attribute checks as
   applicable. Include build/package verification and deployment validation/smoke checks
   where relevant, plus documentation checks such as doc build, generated API/reference
   output, examples, link checks, accessibility/readability, and freshness/version checks.
   For each `TEST-`, state kind, linked `COMP-`/`IFACE-`, linked `FR-`/`NFR-`/`UC-`/`AT-`/
   `RISK-`/`DEC-`, verification oracle, data/doubles/environment, fixture or schema source
   for boundary payloads, speed/scope, and whether it is required for the first
   implementation PR or a later PR. Explain how each `COMP-`, `IFACE-`, critical flow,
   `AT-`, and important `NFR-` is tested in isolation and in collaboration, including
   logging/telemetry assertions, observability, failure injection, error-mapping tests,
   contract-realistic mocks, and migration/rollback checks where relevant.
12. **Risks & Trade-offs** — (`RISK-<SLUG>`); risk or technical debt, impact, likelihood,
   mitigation, owner, trigger, and residual risk.
13. **Traceability Matrix** — requirements (`FR-`/`NFR-`/`UC-`/`AT-`) → components →
   interfaces → decisions/tactics → `TEST-` obligations/operational checks.

## Step 4 — Render an HTML companion

The markdown `design.md` is the machine-checkable source of truth (IDs must parse). In
addition, emit `design.html` — a single-file HTML companion that renders the same design
for easy reading: include each Mermaid diagram in a `<pre class="mermaid">` block and load
Mermaid from a CDN, with the same section order and ID-keyed tables. Keep both files in
sync; never put IDs only in the HTML.

If the work is UI-facing and the spec records `UI Mock Preference: Required`, also emit
`mock-ui.html` or update the repo's established mock UI artifact. Include enough static or
lightweight interactive UI to let the user review major screens, navigation, states,
copy/content, error/empty/loading behavior, and responsive behavior. Do not continue to
`/plan-create`, `/code-create`, or production UI implementation until the user explicitly
approves the mock UI.

## Step 5 — Verify before finishing

First run the deterministic structural checker and fix the document until it passes:

```pwsh
python checkers/check_design.py design.md --spec spec.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry the same command
with `python3`; if that is unavailable, retry with `uv run python`.

For component designs, include `--component --parent <product-design>`.

Then run or perform the corresponding `/design-assess` against the completed design. When
sub-agents are available, use fresh-context Mechanical Verifier and Qualitative Reviewer
sub-agents as described in `/design-assess`; otherwise state that review is not independent
and use the adversarial posture. Treat any upstream spec blocker, qualitative finding,
missing rationale, unaddressed quality attribute, interface issue, testability gap, risk, or
traceability issue as a defect in the created design/spec set. Revise the upstream artifact
if the review says the spec must change; otherwise revise `design.md`/`design.html`. Repeat
checker + assessment until `/design-assess` would return Pass or an explicitly accepted
Pass-with-fixes.

## Quality rules

- Every component maps to ≥1 requirement or driver; every interface has exactly one owning component.
- Work scope, design depth, and implementation readiness are explicit and realistic. HLDs
  are allowed to pass as Decomposable; LLD/slice designs marked Code-ready must contain
  enough local detail for planning and implementation.
- No unintentional cyclic dependencies; dependency direction, ownership, and boundary crossings are explicit.
- Each component has cohesive responsibility, clear state/side-effect boundaries, and a named lifecycle.
- Quality attributes are addressed by concrete tactics, flows, constraints, or tests rather than adjectives.
- Every component, interface, deployable artifact, documentation artifact, critical `AT-`,
  and important `NFR-` has a named `TEST-` obligation or check level and relevant build,
  deployment, documentation, observability, or operational checks.
- Logging and telemetry design names the structured signals, correlation/support IDs,
  sinks, retention/sampling, redaction/privacy rules, and consumers that matter for humans,
  agents, debugging, support, or operations.
- Error-handling design covers UI, API, domain, integration, infrastructure, validation,
  authorization, timeout, offline, and unexpected-failure categories where relevant,
  including mapping boundaries, recovery/retry/fallback, escalation, and safe user/API
  messages.
- Every `TEST-` obligation has a concrete verification oracle: what output, state, record,
  event, DOM, screenshot, log, metric, trace, artifact, deployment signal, or external-call
  observation proves pass/fail.
- Every boundary-facing test obligation identifies a fixture/schema/generated-client or
  contract-test source of truth; ad-hoc mocks with invented payload shapes are called out as
  risks or rejected.
- UI-facing designs define a presentation approach and readable loading/empty/error/
  validation states, or explicitly record them as out of scope.
- UI-facing designs honor the spec's UI mock preference. If `UI Mock Preference: Required`,
  `mock-ui.html` or the established mock artifact exists, is referenced from the design, and
  awaits or records explicit user approval before downstream implementation.
- Every diagram uses IDs as node/entity labels so it maps back to the spec and tables.
- Record important alternatives, trade-offs, assumptions, risks, and technical debt. No vague verbs, no "etc.".
- Create/update ADRs for material decisions and keep ADRs synchronized with `DEC-` entries.

Write the design to `design.md` (source of truth) and a matching `design.html` companion
in the workspace unless the user names other files.

## Human review gate (hard stop)

After writing or revising the design and completing the checker/assessment loop above, **stop**.
Do not start `/plan-create`, `/code-create`, or any downstream artifact in the same turn.

End with a human-review handoff that includes:

- Design path(s), including ADR paths if created or updated.
- Mock UI path and approval status when a UI mock was required or produced.
- Work Scope, Design Depth, and Implementation Readiness.
- checker/assessment result.
- Key decisions, assumptions, open questions, and risks.
- Recommended next command, normally `/plan-create` only after the user approves the design.

Continue past this gate only if the user's latest message explicitly requested unattended
end-to-end continuation or explicitly approves the next stage.
