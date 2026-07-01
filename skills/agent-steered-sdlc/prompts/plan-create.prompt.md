---
description: Interview the user, then author a work plan that translates the spec and design into reviewable, test-first PRs (≤300 LOC each), including planned logging/error-handling/docs/build/deploy work.
agent: agent
---

# Plan Create

Your job is to produce a **Work Plan** that either decomposes broad work into smaller
code-ready work items or turns an already code-ready slice/change into tested,
production-quality code delivered as small pull requests. Optimize so `/plan-assess` finds
nothing to fix.

## Core principles (the plan is judged against these)

1. **Small reviewable PRs** — each PR changes **≤300 LOC** (prod + test), one focused concern.
2. **Red/Green TDD** — every PR writes failing tests first (Red), then minimal code to pass
   (Green), then refactor. The plan states both Red and Green steps per PR.
3. **Full coverage** — every `FR-`/`UC-`, every `NFR-`, every `AT-`, every design
   `COMP-`, every design `TEST-` obligation, and every required logging/error-handling/
   docs/build/deploy concern is delivered by at least one PR.
   Nothing in spec/design is left unbuilt, undocumented, or unverifiable.
4. **Always shippable** — order PRs so each merges green, behind a flag if needed; no PR
   depends on a later one, and build/deployment capability is introduced before code that
   depends on it.
5. **Production quality** — each PR includes tests, logging/telemetry where relevant, error
   handling, and meets its NFRs.
6. **Explicit touch scope** — each PR declares the files, directories, modules, config files,
   docs, generated artifacts, and spec/design/plan sections it is expected to touch.
7. **Build and deployment are planned work** — build scripts, package manifests, generated
   artifacts, CI/CD config, infrastructure/deployment manifests, migration scripts,
   release notes, smoke checks, and rollback steps are assigned to explicit work items or PRs.
8. **User and developer docs are planned work** — user guides, in-product help, README/API
   docs, examples, runbooks, troubleshooting, migration notes, release notes, generated
   reference docs, and doc validation checks are assigned to explicit work items or PRs.
9. **Logging and error handling are planned work** — structured logging, telemetry,
   correlation/support IDs, redaction, alert hooks, error mapping, retry/fallback, degraded
   behavior, and safe UI/API messages are assigned to explicit work items or PRs.

## Work scope, plan type, and readiness

Every plan belongs to one of three work scopes:

- **Product/system** — plan normally decomposes broad work into feature/component work. It
  should not pretend to be directly code-ready unless the system is trivially small.
- **Feature/component** — plan may decompose a coherent feature/subsystem into
  slice/change work, or may produce an implementation plan if the feature is already small
  and locally designed.
- **Slice/change** — plan should be an implementation plan with concrete PRs, Planned Touch
  Sets, test levels, quality gates, and Red/Green steps.

Choose one **Plan Type**:

- **Breakdown plan** — identifies child feature/component or slice/change work items, their
  dependencies, required child specs/designs, risks, and recommended order. It can pass
  review while **not code-ready**.
- **Implementation plan** — defines PR-sized work for a code-ready slice/change, or for a
  small feature/component already decomposed enough to implement safely.

Record **Implementation Readiness** explicitly:

- **Exploratory** — more analysis/spec/design is needed before reliable decomposition.
- **Decomposable** — parent work is valid and ready to break into child artifacts.
- **Code-ready** — plan contains enough PR detail for `/code-create`.

Do not force a broad product/system or feature/component into PRs prematurely. If the inputs
are too high-level, produce a Breakdown plan that lists required child specs, HLD/LLD,
contracts, research, or decisions before implementation.

Infer the likely scope from the user's request and state it before writing. Broad asks such
as "plan this product/platform/system" normally map to a Product/system Breakdown plan. A
request for one capability, subsystem, integration, or component normally maps to a
Feature/component Breakdown plan unless it is already small and locally designed. A bug fix,
PR-sized behavior change, local refactor, or explicitly named PR normally maps to a
Slice/change Implementation plan. Ask only when the mapping is ambiguous or materially
changes the artifact to produce.

## Clarification and YOLO mode

Default behavior is input-gated: pause and ask one focused question at a time when missing
information would materially change plan type, readiness, PR slicing, Planned Touch Sets,
test allocation, sequencing, dependencies, rollback, quality gates, or parallel/worktree
strategy. Do not silently invent consequential implementation scope.

The user may opt into **YOLO mode** with phrases such as "yolo", "use your judgment", "make
reasonable assumptions", or "proceed without questions". In YOLO mode, make the narrowest
reasonable planning decisions yourself, continue without blocking on normal clarification
questions, and record every material assumption, trade-off, risk, and deferred question in
`plan.md`. YOLO mode does not bypass upstream spec/design blockers, code-readiness limits,
the 300-LOC PR ceiling, Planned Touch Set discipline, or safety/security/compliance concerns.

## Lightweight exploratory track

For spikes, throwaway prototypes, exploratory data/ML work, proof-of-concept integrations,
or infrastructure investigations, do not force a full Breakdown or Implementation plan. Write
a lightweight plan when the user accepts that track. It must include: goal, timebox,
assumptions, non-goals, risks, experiment tasks, evidence to collect, cleanup/disposal
criteria, and the condition that would trigger normal specs/designs/plans. Mark it
`Implementation Readiness: Exploratory`; do not include production `PR-` items or mark it
Code-ready.

## Plan artifact types by scope

Use the same section order for every plan, but tune the content to the declared scope:

- **Product/system plan** is normally a Breakdown plan. It carries milestones, child
  feature/component `WORK-` items, dependencies, required child specs/designs/ADRs, research
  or decision needs, logging/error-handling tracks, build/release/deployment tracks,
  documentation tracks, sequencing, parallel tracks, major risks, and readiness targets. It
  should not list implementation PRs unless the system is trivially small.
- **Feature/component plan** carries either child slice/change `WORK-` items or concrete
  implementation PRs when the feature/component is already code-ready. It identifies child
  spec/LLD needs, dependencies, integration order, test strategy allocation, touch-scope
  risks, logging/error-handling impacts, build/deployment impacts, documentation impacts,
  and the point where work becomes PR-ready.
- **Slice/change plan** is an Implementation plan. It carries `PR-` items, Planned Touch
  Sets, Red/Green steps, test levels, LOC estimates, quality gates, rollback notes,
  logging/error-handling verification, build/deployment verification, documentation
  updates/checks, dependencies, parallel/worktree guidance, and traceability to the exact
  FR/AT/COMP/TEST items.

## Test responsibility in this command

`/plan-create` turns the spec's acceptance criteria and the design's `TEST-` obligations
into a PR-by-PR executable test plan. It decides **when** each test is written, **which
level** it belongs to, and **which PR** owns it.

For each PR, list the test levels it will add or update:

- **Acceptance/e2e tests** that execute one or more `AT-` scenarios and cite the relevant
  `TEST-` obligation when the design named one.
- **Unit/pure-core tests** for deterministic rules, calculations, validation, state
  transitions, reducers, mappers, and edge cases.
- **Component/module tests** for cohesive components behind stable boundaries.
- **Contract tests** for APIs, events, schemas, protocols, DTOs, and error compatibility.
- **Integration tests** for persistence, messaging, external services, adapters, framework
  wiring, migrations, transactions, auth, caching, retries, and configuration.
- **UI/accessibility/visual tests** for frontend/mobile routes, screens, components, focus,
  keyboard/touch behavior, semantics, contrast, and visual regressions.
- **Quality-attribute checks** for performance, reliability, security, privacy, resilience,
  observability, logging/telemetry, error handling, offline/sync, rollout/rollback, and
  operational behavior.
- **Build/deployment checks** for reproducible artifact creation, package metadata,
  container/image/static/mobile build output, migration validation, deployment dry runs,
  infrastructure/deployment manifest validation, smoke checks, and rollback verification.
- **Documentation checks** for user/developer docs, README/API/reference output, examples,
  tutorials, diagrams, runbooks, troubleshooting, release/migration notes, doc generation,
  link checks, accessibility/readability, and freshness/versioning.

Do not push all coverage to end-to-end tests. Prefer many fast lower-level tests for logic
and contracts, focused integration tests for wiring and infrastructure, and a smaller set of
acceptance/e2e tests for critical user journeys and externally visible `AT-` coverage.
Every `TEST-` obligation from the design must map to a PR or child work item unless the plan
explicitly justifies it as non-executable or out of scope for the current slice.
Every executable test assignment must preserve or refine the design's verification oracle:
the concrete evidence that proves pass/fail, such as return value, state change, persisted
record, emitted event, API response, DOM/role/text output, accessibility tree, screenshot or
visual baseline, generated artifact, structured log, metric, trace, deployment signal, or
captured external call.
The plan does not need to enumerate every implementation-local unit case in advance. It
should identify likely inner-test discovery zones, such as complex pure logic, parsers,
mappers, reducers, adapters, boundary normalizers, or migration helpers. `/code-create` may
add supplemental inner tests found during TDD inside the owning PR and Planned Touch Set.
Those tests supplement planned `AT-`/`TEST-` coverage; if they imply new externally visible
behavior, a changed contract, UX/NFR expectations, or broader scope, the agent must stop and
request a spec/design/plan update.
For boundary-facing work, identify the fixture/schema/generated-client/contract-test source
of truth each PR will use. Do not plan tests that rely on ad-hoc mock payloads that differ
from the producer/consumer contract.

## Scope: new, revision, breakdown, or implementation plan

- **New breakdown plan** — decompose product/system or feature/component work into child
  feature/component or slice/change items and state which child artifacts are required.
- **New implementation plan** — author the full PR-oriented document below for code-ready
  slice/change work or a small feature/component that already has enough local detail.
- **Revision** — a plan exists. Read it, preserve IDs, add new descriptive slug IDs, and
  refresh coverage.
- **Feature/component plan** — plan one feature/component; reference parent spec/design IDs;
  note parent paths and choose Breakdown or Implementation plan type.

## Step 1 — Clarify before writing (mandatory unless YOLO, one question per turn)

Read `spec.md` and `design.md` first. Then interview the user **one question at a time**:

- **Work scope and plan type**: Is this product/system, feature/component, or slice/change
  scope? Should this be a Breakdown plan or Implementation plan? Is the work Exploratory,
  Decomposable, or Code-ready?
- **Stack & tooling**: language, test framework, CI, branch/merge model.
- **Build/release/deployment tooling**: build command, artifact type/path, packaging or
  image strategy, artifact registry, deployment scripts/manifests/IaC, target environments,
  promotion model, dry-run/validation command, smoke checks, rollback, and who operates it.
- **Documentation tooling and ownership**: doc source locations, user/developer doc
  audiences, generated reference docs, doc build command, link checker, publishing path,
  owner/reviewer, and freshness/versioning expectations.
- **Logging, telemetry, and error-handling ownership**: which PRs own structured log fields,
  events, metrics, traces, audit/support IDs, correlation propagation, redaction, alert
  hooks, error mapping, retry/fallback/degraded behavior, and safe UI/API messages.
- **Done definition**: coverage bar, lint/format gates, review rules.
- **Test mix**: which acceptance, unit, component, contract, integration, UI/accessibility,
  quality-attribute, migration, and operational checks are required by the spec/design; for
  boundary-facing tests, which shared fixtures, schemas, generated clients, captured
  examples, or contract tests will prevent mock drift; for each planned test, what oracle
  proves pass/fail.
- **UX/presentation work**: For UI-facing work, which stylesheet/design-token/component
  library/layout/error-state/responsive/accessibility work is in scope, and which PR owns
  non-brittle checks for it?
- **Mock UI approval**: If the spec/design requires a mock UI, where is the mock artifact,
  has the user approved it, and which PRs are constrained by it?
- **Sequencing**: which capability ships first; flags vs. trunk; migration order.
- **Parallel execution**: which PRs can be built concurrently, whether Git worktrees should
  be used for independent branches, and which files/modules are likely to conflict.
- **Touch scope**: which files, directories, modules, generated artifacts, config files,
  migrations, logging/telemetry config, error-handling modules, build/deployment scripts,
  CI/CD/IaC/manifests, user/developer docs, examples, runbooks, release notes, generated
  reference docs, and spec/design/plan sections each PR is allowed or expected to touch.
- **Slicing limits**: anything that must not exceed the 300-LOC PR ceiling.

State assumptions explicitly and list them. Keep asking until slicing is unambiguous. In
YOLO mode, prefer proceeding with explicit planning assumptions over continuing the
interview, while preserving hard blockers for upstream artifact defects and non-code-ready
work.

## Step 2 — ID convention

- Use slug-only `KIND-AREA-NAME` IDs: `MILE-<AREA>-<NAME>` (milestone),
  `WORK-<AREA>-<NAME>` (child work item), and `PR-<AREA>-<NAME>` (pull request).
- `AREA` and `NAME` are uppercase slug tokens, 2-32 characters each, using `A-Z` and
  digits only after the first character. Do not use trailing numbers.
- Each PR cites the `FR-`/`UC-`/`AT-` it delivers, the `COMP-` it implements, and the
  `TEST-` obligations it writes or updates.

## Step 3 — Author the plan with this exact section order

1. **Overview** — goal, stack, branching/CI model, Git worktree policy if parallel work is
   useful, and done-definition in one paragraph. Include explicit `Work Scope:`,
   `Plan Type: Breakdown | Implementation`, and `Implementation Readiness:` lines.
2. **Strategy** — Red/Green TDD loop, the ≤300-LOC PR rule, flags, always-green ordering,
   branch/worktree isolation, integration cadence, logging/error-handling strategy, build
   artifact strategy, deployment strategy, documentation strategy, and whether this plan
   decomposes parent work or implements code-ready work.
3. **Milestones** — list (`MILE-<AREA>-<NAME>`); each groups child work or PRs toward a
   coherent delivery slice.
4. **Pull Requests / Child Work Items** — for a Breakdown plan, list
   `WORK-<AREA>-<NAME>` items with scope, parent IDs, required child spec/design/LLD/plan,
   dependencies, readiness target, risks, and done signal. For an Implementation plan, list
   `PR-<AREA>-<NAME>` items; for each: scope; **Planned Touch Set**
   (files/directories/modules/config/docs/generated artifacts plus any spec/design/plan
   sections allowed to change, including build/deployment/CI/IaC files when relevant);
   **Build/Deploy Work** (artifact, script, pipeline, manifest, migration, dry-run, smoke,
   or rollback work owned by this PR, or `None` with rationale); **Documentation Work**
   (user docs, developer docs, API/reference docs, examples, runbooks, troubleshooting,
   release/migration notes, generated docs, or `None` with rationale);
   **Logging/Telemetry Work** (structured logs, events, metrics, traces, audit/support IDs,
   correlation, redaction, alert hooks, or `None` with rationale); **Error Handling Work**
   (UI/API/domain/integration/infrastructure error mapping, retry/fallback/degraded
   behavior, safe messages, or `None` with rationale); **Mock UI Dependency** (approved
   mock path/status for UI-facing PRs, or `None` with rationale); **Test Levels**
   (acceptance/e2e, unit, component, contract, integration, UI/accessibility/visual,
   quality/NFR, build/deploy, docs, migration/ops as applicable); **Contract Fixtures**
   (shared fixture/schema/generated-client/contract-test source for boundary payloads, or
   `None` with rationale); **Verification Oracle** (return value/state/event/API/DOM/
   screenshot/log/metric/artifact/deployment/external-call evidence, as applicable); **Red** (failing tests,
   naming the level and linked `TEST-`/`AT-`/`FR-` IDs); **Green** (impl); est LOC (≤300);
   `COMP-` built; `FR-`/`AT-` delivered; `TEST-` obligations implemented; depends-on PRs.
5. **Coverage Map** — for a Breakdown plan, map each `FR-`/`UC-`/`NFR-`/`AT-`/`COMP-` to
   child `WORK-` items and required child artifacts, and map each design `TEST-` obligation
   to the child work that will make it executable. For an Implementation plan, map each
   `FR-`/`UC-`/`NFR-`/`AT-`/`COMP-` and each `TEST-` obligation to the PR delivering it.
6. **Sequencing & Risks** — merge order, parallelizable PRs, build before deployment
   dependencies, documentation before/with behavior dependencies, environment promotion
   order, rollback per PR, likely merge conflicts/shared files, planned touch-set overlaps,
   and worktree recommendations. State the parallel **waves** (sets of PRs runnable at
   once), which waves are suitable for separate Git worktrees, and the critical path
   explicitly.

## Step 4 — Render an HTML companion

The markdown `plan.md` is the machine-checkable source of truth (IDs must parse). In
addition, emit `plan.html` — a single-file HTML companion that renders the same plan and
makes task progression obvious. Load Mermaid from a CDN and include:

- A **dependency graph** (`flowchart LR`) of PRs, edges = depends-on, nodes labelled with
  the PR's human-readable scope name (PR-ID as the node key); colour-fill PRs on the
  critical path.
- A **wave / Gantt view** (Mermaid `gantt`) grouping PRs into parallel waves by scope name
  so concurrent work and the sequential spine are visible at a glance.
- Worktree notes for each parallel wave when independent PRs can safely be developed in
  separate Git worktrees.
- ID-keyed PR and coverage tables, same section order as the markdown.
- Planned touch-set tables so implementers and reviewers can see file/module ownership and
  allowed user-doc/developer-doc/config/build/deployment changes per PR.

Keep both files in sync; never put IDs only in the HTML. Each diagram node uses the scope
name for the label and the PR-ID as its key so it maps back to `plan.md`.

## Step 5 — Verify before finishing

First run the deterministic structural checker and fix the document until it passes:

```pwsh
python checkers/check_plan.py plan.md --spec spec.md --design design.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry the same command
with `python3`; if that is unavailable, retry with `uv run python`.

For feature/component or slice/change plans, include `--feature --parent <product-plan>`.

Then run or perform the corresponding `/plan-assess` against the completed plan. When
sub-agents are available, use fresh-context Mechanical Verifier and Qualitative Reviewer
sub-agents as described in `/plan-assess`; otherwise state that review is not independent and
use the adversarial posture. Treat any upstream spec/design blocker, qualitative finding,
missing coverage, weak PR slicing, TDD gap, build/deployment gap, documentation gap,
sequencing/worktree issue, rollback gap, or production-quality concern as a defect in the
created plan or its upstream inputs. Revise upstream artifacts if the review says they must
change; otherwise revise `plan.md`/`plan.html`.
Repeat checker + assessment until `/plan-assess` would return Pass or an explicitly accepted
Pass-with-fixes.

## Quality rules

- Work scope, plan type, and implementation readiness are explicit and realistic. Breakdown
  plans are allowed to pass as Decomposable; Implementation plans marked Code-ready must
  contain PR-level Planned Touch Sets, test levels, and Red/Green steps.
- Every implementation PR ≤300 LOC and states Test Levels, Red steps, and Green steps. No
  PR depends on a later one.
- Every FR, UC, NFR, AT, COMP, and TEST maps to ≥1 child work item or implementation PR. No
  orphan or duplicate IDs.
- Every `AT-` maps to an executable acceptance/e2e/API workflow test PR or to a justified
  non-code verification PR/check.
- Every design `TEST-` obligation maps to the PR or child work item that writes/runs that
  executable unit, component, contract, integration, UI, quality, logging/telemetry,
  error-handling, build/deploy, docs, migration, or operational check; lower-level tests
  from the design are scheduled near the code they protect.
- Every PR-level test assignment states a verification oracle concrete enough for
  `/code-create` to write a meaningful failing test and for `/code-review` to reject weak or
  indirect assertions.
- Boundary-facing PRs name the fixture/schema/generated-client/contract-test source of
  truth used by tests; invented mock payload shapes are treated as plan defects.
- UI-facing PRs include planned presentation/layout/responsive/accessibility/error-state
  work or explicitly state why that quality work is out of scope.
- If a mock UI is required, UI-facing PRs reference the approved mock artifact and must not
  start until that mock is explicitly approved by the user.
- Logging/telemetry and error-handling work is assigned to PRs whenever the spec/design
  calls for it; otherwise the plan states why it is out of scope.
- Build artifact creation, packaging, deployment scripts/manifests/IaC, deployment dry runs,
  smoke checks, and rollback verification are assigned to PRs whenever the spec/design calls
  for them; otherwise the plan states why they are out of scope.
- User/developer documentation updates, generated reference docs, examples, runbooks,
  troubleshooting, release/migration notes, and doc validation checks are assigned to PRs
  whenever the spec/design calls for them; otherwise the plan states why they are out of scope.
- Each PR is independently testable and shippable.
- Each PR has a Planned Touch Set precise enough for `/code-create` to know whether an
  intended edit is in scope. Use globs only when necessary and keep them narrow.
- Parallel waves identify file/module ownership, expected conflicts, integration order, and
  whether Git worktrees are recommended or unnecessary.
- No vague verbs, no "etc.".

Write the plan to `plan.md` (source of truth) and a matching `plan.html` companion in the
workspace unless the user names other files.

## Human review gate (hard stop)

After writing or revising the plan and completing the checker/assessment loop above, **stop**.
Do not start `/code-create`, implementation, build/deployment work, or any downstream
artifact in the same turn.

End with a human-review handoff that includes:

- Plan path(s).
- Work Scope, Plan Type, and Implementation Readiness.
- checker/assessment result.
- PR/work-item count, parallel waves, and known risks.
- Recommended next command, normally `/code-create` only after the user approves the plan.

Continue past this gate only if the user's latest message explicitly requested unattended
end-to-end continuation or explicitly approves the next stage.
