---
description: Interview the user, then author a high-quality Software Design Document grounded in requirements, stakeholder concerns, quality attributes, architecture views, interfaces, decisions, risks, and testability.
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
   deployment/infrastructure, and operational views only to the depth needed for the system's
   risk and complexity.
5. **High cohesion and low coupling** — components should have clear responsibilities,
   stable contracts, explicit dependencies, and minimal knowledge of each other's internals.
6. **Functional core, imperative shell** — identify pure decision logic, business rules,
   validation, policy, state transitions, calculations, and derived data separately from
   I/O, persistence, messaging, framework glue, navigation, time, randomness, device APIs,
   network calls, analytics, notifications, and other effects. The core should be easy to
   test deterministically; the shell should be thin, explicit, observable, and contract-tested.
7. **Interface-first collaboration** — APIs, events, schemas, protocols, and error contracts
   are part of the design, not afterthoughts.
8. **Data and lifecycle awareness** — model data ownership, identity, consistency, retention,
   migrations, privacy/security classification, and failure/recovery behavior where relevant.
9. **Testability and operability by design** — each component should have an isolation
   strategy, contract/integration test approach, observability hooks, and operational checks.
10. **Decisions carry rationale and consequences** — record alternatives considered,
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
  unless the user explicitly delegates the choice; if delegated, record the assumption.
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
  accessibility, observability, resilience, offline/sync, migration/rollback, and operations.

Document this as a test matrix in **Test Strategy**. For each test level, state purpose,
owner/component, linked `FR-`/`NFR-`/`UC-`/`AT-`/`COMP-`, required doubles or environments,
and whether `/code-create` should implement it in the PR that introduces the behavior or
defer it to a specific later PR.

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
  data ownership, integration and deployment/operations strategy, material decisions/ADRs,
  risks, decomposition candidates, and a system-level test strategy. It should explain how
  the system will be divided, not specify every local algorithm or file.
- **Feature/component design** carries component responsibilities, interfaces/contracts,
  local data/state ownership, runtime flows, functional-core/imperative-shell partition,
  dependencies, UX/API contracts, feature-level decisions/ADRs, risks, and a test matrix for
  that feature/component. It should identify any child slice/change LLDs still required.
- **Slice/change design (LLD)** carries the exact local design needed for implementation:
  touched components/modules, API/schema/data changes, detailed happy and failure flows,
  validation/policy logic, core-vs-shell placement, migration/rollback concerns, side
  effects, planned test levels/doubles, and likely file/module touch candidates.

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
  idempotency, pagination, versioning, compatibility, and OpenAPI/AsyncAPI references where useful.
- **Data model and state**: entities, relationships, ownership, lifecycle/state machines,
  migrations, indexes, retention, consistency, transactions, and cache behavior.
- **Runtime flows**: sequence diagrams for core use cases, failure paths, retries, async/event
  flows, background jobs, and cross-service interactions.
- **Deployment and operations**: environments, configuration, secrets, health checks,
  observability, alerts, backups, scaling, rollout/rollback, and runbooks.
- **Backend test strategy**: core unit tests, contract tests, integration tests, migration tests,
  performance/security/resilience tests, and end-to-end tests.

Minimum backend artifacts: context diagram, container/service diagram, component/module
diagram, API/event contract table or formal spec reference, data model diagram/table,
sequence/runtime diagrams, deployment/ops view, and component-to-test matrix.

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
  optimistic updates, mutation invalidation, and authorization behavior.
- **Loading/error/empty/accessibility/responsive states**: matrices for important components
  and routes, including focus management, keyboard behavior, ARIA/semantic HTML, contrast,
  target size, breakpoints, touch behavior, and content priority.
- **Frontend performance and security**: bundle boundaries, lazy loading, rendering hotspots,
  image/media strategy, token/storage policy, sensitive data handling, and privacy events.
- **Frontend test strategy**: pure function tests, component tests, accessibility checks,
  API-mocked integration tests, visual tests where useful, and E2E tests for critical journeys.

Minimum web frontend artifacts: route map, component hierarchy diagram, UX flow diagram,
state model/table, data/API contract table, loading/error/empty state matrix, accessibility
checklist, responsive behavior matrix, and test traceability matrix.

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
- **Mobile test strategy**: core unit tests, widget/component tests, navigation/data-flow
  integration tests, device/emulator tests, accessibility tests, permission-denied tests,
  offline/sync tests, lifecycle/background tests, and release-health checks.

Minimum mobile artifacts: core/adapters component diagram, navigation graph, screen/state
table, offline/sync diagram when remote data exists, permission/capability matrix,
lifecycle/background table, performance budget, and test strategy matrix.

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
  renumber), insert new items at the next gap number, and update the traceability matrix.
- **Feature/component design** — designing one feature, component, subsystem, or integration,
  not the whole product. Write a focused file (e.g. `designs/<slug>.md`) with only the
  sections that apply. It may **reference** product-level IDs without redefining them; note
  the parent design path. Mark it Decomposable if it still needs slice/change LLDs.
- **Slice/change LLD** — designing one implementable slice or local change. Include enough
  local behavior, interfaces, data, failure cases, test levels, and implementation constraints
  for `/plan-create` to produce a code-ready implementation plan.

## Step 1 — Clarify before writing (mandatory, one question per turn)

If a spec (`spec.md`) exists, read it first — the design must satisfy its FRs/NFRs/UCs.
Do **not** write the design until the system boundary, drivers, quality-attribute scenarios,
interfaces, data, runtime behavior, and verification approach are sufficiently understood. Interview
the user **one question at a time**: ask, wait, then ask the next. Cover:

- **Stakeholders and concerns**: who needs to understand, build, run, secure, evolve, or
  integrate with the design, and what do they care about?
- **Research need**: Would current external research help choose technologies, understand
  platform/vendor constraints, validate security/accessibility guidance, confirm service
  limits, or compare architectural options? If yes, search before finalizing affected decisions.
- **Design profile**: backend/API/service, web frontend, mobile app, desktop, library/SDK,
  data/ML pipeline, infrastructure, OO/UML-heavy component, or mixed system. Select the
  profile-specific artifacts that apply.
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
- **State and side effects**: pure decision logic, persistence, I/O, external calls, time,
  randomness, transactions, concurrency, retries, idempotency, and consistency boundaries.
- **Interfaces and contracts**: APIs, events, commands, schemas, protocols, auth, errors,
  compatibility/versioning, and ownership.
- **Quality tactics and trade-offs**: how the design meets performance, reliability,
  security, modifiability, usability, observability, deployment, and cost goals.
- **Decision points**: what trade-offs require user input, what options are viable, which
  option is recommended, and whether an ADR is needed.
- **Test and verification strategy**: how components, contracts, quality attributes, data
  migrations, failure modes, and critical flows are verified.
- **Risks and evolution**: technical debt, migration path, rollout/rollback, likely change
  points, and alternatives rejected.

State assumptions explicitly in Risks/Trade-offs, Design Decisions, or ADRs. Keep asking
until remaining unknowns and material trade-offs are resolved, deliberately deferred, or
recorded with impact.

## Step 2 — Numbering convention (apply everywhere)

Use **prefix + slug**, no numeric suffix — numbers belong to the spec, not the design:

- Slug = component/area name (e.g. `AUTH`, `CORE`). One entity per slug, so no `-N` suffix.
- `LAYER-<SLUG>` (layer), `COMP-<SLUG>` (component), `IFACE-<SLUG>` (interface),
  `DEC-<SLUG>` (design decision), `RISK-<SLUG>` (risk). IDs are unique and stable.
- Components cite the numbered `FR-`/`NFR-`/`UC-` from `spec.md` they realize.

## Step 3 — Author the design with this exact section order

1. **Overview** — what is being built, system boundary/context, principal stakeholders,
   and architectural style/strategy in one paragraph. Include explicit `Work Scope:`,
   `Design Depth: HLD | feature/component design | LLD`, and `Implementation Readiness:`
   lines.
2. **Tech Stack** — chosen language(s), runtime, frameworks, datastore, and key libraries,
   infrastructure/services, external dependencies, and rationale tied to drivers/NFRs. Note
   versions, licensing, hosting, or organizational constraints where they matter.
3. **Drivers & Constraints** — the FRs/NFRs/use cases, quality-attribute scenarios,
   stakeholder concerns, external constraints, risks, and assumptions that shape the design.
4. **Layers** — (`LAYER-<SLUG>`); each names its responsibility, allowed dependencies,
   boundary rules, ownership, and whether it belongs to core policy, application orchestration,
   adapter/shell, presentation, data, or infrastructure. Dependencies should be acyclic and justified.
5. **Components** — (`COMP-<SLUG>`); responsibility, layer, dependencies
   (by `IFACE-`), state/side-effect profile, lifecycle, scaling/deployment notes where
   relevant, core/shell classification, and the `FR-`/`NFR-`/`UC-` it realizes. Include a
   **component / association diagram** (Mermaid `flowchart` or `classDiagram`) showing
   layers, components, dependency arrows, and core-vs-shell boundaries.
6. **Interfaces** — (`IFACE-<SLUG>`); contract, inputs/outputs, `owner: COMP-<SLUG>`,
   protocol/schema, auth/trust boundary, error behavior, versioning/compatibility, and QoS
   expectations where relevant.
7. **Core vs. Shell** or **Core vs. Shell / Equivalent Separation** — include a table that classifies each `COMP-` as pure core,
   application/orchestration, adapter/shell, presentation, data, infrastructure, or mixed.
   For the core, list pure decisions, rules, validation, state transitions, calculations,
   reducers, mappers, and invariants. For the shell, list I/O, persistence, network calls,
   UI/navigation, device/browser APIs, framework glue, clocks, randomness, transactions,
   retries, messaging, analytics, notifications, and observability. Explain how dependencies
   point inward or through interfaces, how side effects are isolated, and how each category is tested.
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
11. **Test Strategy** — a test-level matrix covering acceptance/e2e, integration, contract,
   component/module, unit/pure-core, UI/accessibility/visual, migration, operational, and
   quality-attribute checks as applicable. Explain how each `COMP-`, `IFACE-`, critical flow,
   `AT-`, and important `NFR-` is tested in isolation and in collaboration, including test
   data, doubles, environments, observability, failure injection, and migration/rollback
   checks where relevant.
12. **Risks & Trade-offs** — (`RISK-<SLUG>`); risk or technical debt, impact, likelihood,
   mitigation, owner, trigger, and residual risk.
13. **Traceability Matrix** — requirements (`FR-`/`NFR-`/`UC-`) → components → interfaces →
   decisions/tactics → tests/operational checks.

## Step 4 — Render an HTML companion

The markdown `design.md` is the machine-checkable source of truth (IDs must parse). In
addition, emit `design.html` — a single-file HTML companion that renders the same design
for easy reading: include each Mermaid diagram in a `<pre class="mermaid">` block and load
Mermaid from a CDN, with the same section order and ID-keyed tables. Keep both files in
sync; never put IDs only in the HTML.

## Step 5 — Verify before finishing

First run the deterministic structural checker and fix the document until it passes:

```pwsh
python checkers/check_design.py design.md --spec spec.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry the same command
with `python3`; if that is unavailable, retry with `uv run python`.

For component designs, include `--component --parent <product-design>`.

Then run or perform the corresponding `/design-review` against the completed design. When
sub-agents are available, use fresh-context Mechanical Reviewer and Qualitative Reviewer
sub-agents as described in `/design-review`; otherwise state that review is not independent
and use the adversarial posture. Treat any upstream spec blocker, qualitative finding,
missing rationale, unaddressed quality attribute, interface issue, testability gap, risk, or
traceability issue as a defect in the created design/spec set. Revise the upstream artifact
if the review says the spec must change; otherwise revise `design.md`/`design.html`. Repeat
checker + review until `/design-review` would return Pass or an explicitly accepted
Pass-with-fixes.

## Quality rules

- Every component maps to ≥1 requirement or driver; every interface has exactly one owning component.
- Work scope, design depth, and implementation readiness are explicit and realistic. HLDs
  are allowed to pass as Decomposable; LLD/slice designs marked Code-ready must contain
  enough local detail for planning and implementation.
- No unintentional cyclic dependencies; dependency direction, ownership, and boundary crossings are explicit.
- Each component has cohesive responsibility, clear state/side-effect boundaries, and a named lifecycle.
- Quality attributes are addressed by concrete tactics, flows, constraints, or tests rather than adjectives.
- Every component, interface, critical `AT-`, and important `NFR-` has a named test level
  and relevant observability/operational checks.
- Every diagram uses IDs as node/entity labels so it maps back to the spec and tables.
- Record important alternatives, trade-offs, assumptions, risks, and technical debt. No vague verbs, no "etc.".
- Create/update ADRs for material decisions and keep ADRs synchronized with `DEC-` entries.

Write the design to `design.md` (source of truth) and a matching `design.html` companion
in the workspace unless the user names other files.
