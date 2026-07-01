---
name: agent-steered-sdlc
description: End-to-end SDLC workflow for agent-steered creation, review, verification, and reconciliation of requirements, designs, ADRs, plans, code, tests, quality gates, and upstream/downstream artifact consistency. Use when Codex needs to run or review an artifact-governed software delivery lifecycle.
---

# Agent-Steered SDLC

Use the installed stage command, prompt, or skill when the host supports one. If a stage is
not directly invokable, use this skill bundle's `prompts/*.prompt.md` files and follow the
matching prompt exactly. If bundled prompts are unavailable, locate this repository's
`prompts/*.prompt.md` as a fallback.

GitHub Copilot CLI note: prompt files do not become arbitrary built-in CLI slash commands.
The installer creates direct stage skill aliases such as `spec-create`, `code-review`, and
`code-assess` so Copilot CLI can invoke `/code-review` where skill slash invocation is
supported. If the CLI surface rejects a stage slash name, ask in natural language instead:
"Use the agent-steered-sdlc skill to run the code-review stage."

Command verbs have distinct meanings:

- `create`: author or revise the artifact.
- `verify`: collect deterministic/mechanical evidence only.
- `review`: make the qualitative adversarial judgment using available evidence.
- `assess`: run `verify` first, then `review`; this is the full gate.

## Workflow

Select the narrowest command that matches the user's current artifact:

- `/spec-create`: create or revise `spec.md`, including product/system,
  feature/component, and slice/change specs.
- `/spec-verify`: run structural spec checks and report evidence.
- `/spec-review`: qualitatively review requirements and stop if the spec has material issues.
- `/spec-assess`: run `/spec-verify` plus `/spec-review` as the full spec gate.
- `/design-create`: create or revise `design.md`, diagrams, and ADRs from the spec.
- `/design-verify`: run upstream spec and design structural checks.
- `/design-review`: qualitatively review design and stop if upstream spec ambiguity or design risk blocks safe progress.
- `/design-assess`: run `/design-verify` plus `/design-review` as the full design gate.
- `/plan-create`: create `plan.md`, planned touch sets, PR slices, TDD order, and worktree/parallel-work guidance.
- `/plan-verify`: run upstream artifact and plan structural checks.
- `/plan-review`: qualitatively review plan and stop if spec/design issues or planned scope issues block implementation.
- `/plan-assess`: run `/plan-verify` plus `/plan-review` as the full plan gate.
- `/code-create`: implement within the planned touch set using Red/Green/Refactor TDD,
  configured quality gates, planned logging/error-handling work, and planned
  documentation/build/deployment verification.
- `/code-verify`: run tests, coverage, structural code checks, pre-commit/equivalent gates,
  and planned logging/error-handling/build/docs/deployment verification.
- `/code-review`: qualitatively review implementation, tests, traceability, quality gates,
  logging/error-handling fitness, and upstream consistency.
- `/code-assess`: run `/code-verify` plus `/code-review` as the full code gate.

When the user invokes this skill generally instead of naming a specific stage,
operate in human-gated mode by default. Choose and run only the next appropriate SDLC stage.
For creation stages, generate or revise the artifact, run the corresponding `*-assess` gate
when practical, and then stop for human review. Report the artifact path, readiness/status,
key open questions, and the recommended next command. Do not continue automatically to the
next artifact type unless the user explicitly asks for an end-to-end, unattended, or
"continue through all stages" run.

## Hard Human Gates

These gates are mandatory execution stops, not suggestions.

- After creating, materially revising, or reviewing a spec, design, ADR, plan, or code
  slice, **end the turn immediately after the status report**. Do not start the next
  downstream command in the same turn.
- A completed spec gates `/design-create`. A completed design gates `/plan-create`. A
  completed plan gates `/code-create`. A completed code slice gates the next code slice or
  release/deployment activity.
- The stop report must include: artifact path(s), readiness/status, review/check result,
  open questions or assumptions, and the exact recommended next command.
- Continue past a gate only when the user's latest message explicitly approves the next
  stage, for example "continue to design", "run design-create", "approve spec", or
  "continue end-to-end unattended".
- YOLO mode only answers missing-input questions. It does **not** bypass human review gates.
- Even if the matching `*-assess` command passes, stop for human review before downstream work.
- For UI-facing products where the spec records `UI Mock Preference: Required`, creating or
  materially revising the mock UI is a hard human gate. Stop after producing the mock UI
  artifact, report its path, and do not proceed to planning, code, or production UI work
  until the user explicitly approves it.
- If a tool/runtime keeps planning downstream work after a gate, ignore that plan and
  produce the stop report instead.

Also operate in input-gated mode by default. If important information is missing before
creating or revising a spec, design, plan, or code slice, pause and ask one focused question
at a time rather than silently filling the gap. The user may opt into **YOLO mode** with
phrases such as "yolo", "use your judgment", "make reasonable assumptions", or "proceed
without questions". In YOLO mode, continue with the agent's best decisions, clearly record
assumptions and trade-offs in the artifact/report, and call out any assumptions that need
later confirmation. YOLO mode delegates input decisions; it does not bypass readiness gates,
planned touch sets, upstream-blocker stops, safety constraints, or the default human-review
pause after an artifact unless the user also explicitly asks for end-to-end continuation.

## Operating Rules

- Preserve the spec-first order: spec, spec assess, design, design assess, plan,
  plan assess, code, code assess.
- After creating or materially revising any spec, design, ADR, plan, code slice, or review
  report, pause for human review before starting the next downstream stage. The pause is a
  hard collaboration boundary, even when the generated artifact passes mechanical checks.
- Use the three-scope model: product/system, feature/component, slice/change. Every artifact
  should declare Implementation Readiness as Exploratory, Decomposable, or Code-ready.
  Parent artifacts may pass as Decomposable; `/code-create` must only proceed from a
  code-ready implementation plan for a slice/change or sufficiently small feature/component.
- Use slug-only IDs. Specs and plans use `KIND-AREA-NAME`, for example
  `FR-AUTH-SIGNIN`, `AT-AUTH-SIGNIN`, and `PR-AUTH-SIGNIN`. Design entities use
  `KIND-SLUG`, for example `COMP-AUTH` and `IFACE-AUTH`. Design test obligations use
  `TEST-AREA-NAME`, for example `TEST-AUTH-POLICY`. Numeric suffixes such as `FR-AUTH-10`
  are invalid.
- Infer the likely scope from the user's request and state it explicitly. Broad
  product/platform/app requests map to product/system, one capability/subsystem maps to
  feature/component, and bug fixes, PR-sized changes, or local behavior deltas map to
  slice/change. Ask only when the mapping is ambiguous or materially changes the artifact.
- Apply the artifact matrix:
  - Product/system spec carries mission, stakeholders, boundary, product needs, non-goals,
    major capabilities, representative use cases, major NFRs, logging/telemetry and
    error-handling expectations, UI mock preference for UI-facing products,
    build/release/deployment expectations, user/developer documentation expectations, broad
    acceptance intent, and child-artifact needs; design
    carries HLD context, major containers/services/modules, drivers, boundaries, data
    ownership, quality tactics, mock UI artifact/approval when required, logging/telemetry
    strategy, error-handling strategy, build/package/release strategy, deployment/
    operations, documentation strategy, ADRs, risks, and decomposition candidates; plan is
    normally a Breakdown plan with feature/component `WORK-` items, dependencies, child
    artifact needs, mock approval, logging/error-handling tracks, build/deployment tracks,
    documentation tracks, parallel tracks, and readiness targets.
  - Feature/component spec carries parent references, local behavior, FR/NFR/AT coverage,
    edge cases, UI mock preference, logging/telemetry and error-handling constraints,
    build/deployment constraints, documentation constraints, dependencies, and non-goals;
    design carries responsibilities, contracts, local state/data, runtime flows, core/shell
    split, dependencies, mock UI artifact/approval when required, logging/error-handling
    impacts, build/deployment impacts, documentation impacts, decisions, risks, and explicit
    `TEST-` obligations; plan carries child slice/change work or PRs, integration order,
    `AT-`/`TEST-` allocation, mock approval, logging/error-handling allocation,
    build/deployment allocation, documentation allocation, and touch-scope risks.
  - Slice/change spec carries the exact requirement delta, parent IDs refined/preserved,
    changed/unchanged behavior, UI mock preference/delta, logging/error-handling deltas,
    documentation deltas, and acceptance criteria; design carries LLD-level local changes,
    API/schema/data deltas, failure paths, validation/policy logic, mock UI artifact/
    approval when required, logging/telemetry changes, build/deployment script or artifact
    changes, documentation changes, migration/rollback, side effects, `TEST-` obligations/
    doubles, and likely touch candidates;
    plan carries concrete `PR-` items, Planned Touch Sets, Red/Green steps, `AT-`/`TEST-` allocation,
    LOC estimates, quality gates, mock approval, logging/error-handling verification,
    build/deployment verification, documentation checks, rollback, dependencies, and
    worktree guidance.
- Treat test ownership as part of artifact ownership: specs define `AT-` acceptance
  criteria at product/system, feature/component, and slice/change scope; designs define
  explicit `TEST-` executable test obligations for lower-level and workflow checks; plans
  assign each `AT-` and `TEST-` to PRs or child work; code writes acceptance tests plus the
  planned `TEST-` obligations using TDD. Code may also add implementation-local
  supplemental inner tests discovered during Red/Green/Refactor, such as helper, pure-core,
  parser, mapper, regression, characterization, table/property, adapter, or edge-case
  tests. These supplement, never replace, planned `AT-`/`TEST-` coverage. They must stay
  within the current `PR-` and Planned Touch Set, cite the nearest `PR-` plus relevant
  `FR-`/`AT-`/`TEST-`/`COMP-` when applicable, and use a concrete oracle. If a supplemental
  test implies new externally visible behavior, a changed contract, a UX/NFR expectation,
  or broader scope, stop and revise the spec/design/plan before coding it. Executable tests
  are implementation code: their verification oracles, assertions, fixtures, helpers,
  mocks, data, selectors, determinism, and maintainability must be reviewed in
  `/code-review` and `/code-assess`, not merely executed in `/code-verify`. Every test
  should have a concrete oracle for pass/fail: return value, state, persisted record,
  event, API response, DOM/accessibility output, screenshot/visual baseline, artifact,
  structured log, metric, trace, deployment signal, or captured external call as
  appropriate.
- Treat build and deployment ownership as part of artifact ownership: specs define
  externally relevant build/release/deployment needs or non-goals; designs define artifact,
  package, release, environment, deployment, validation, smoke, and rollback strategy; plans
  assign build/deployment files and checks to work items or PRs; code runs the planned build
  and deployment validation, without live production deployment unless explicitly requested.
- Treat user and developer documentation ownership as part of artifact ownership: specs
  define documentation audiences, needs, acceptance criteria, or non-goals; designs define
  documentation architecture, source locations, generated/reference docs, publishing,
  ownership, and validation checks; plans assign documentation files and checks to work
  items or PRs; code updates docs with implementation and validates them where practical.
- Treat UI mock ownership as part of artifact ownership for UI-facing products: specs ask
  the user whether a mock UI is required, optional, not needed, or deferred; designs create
  or update `mock-ui.html` or the repo's established mock location when required, covering
  representative screens, states, flows, and error/empty/loading behavior; plans assign
  mock-driven UI implementation and visual/accessibility checks to PRs; code must block if
  a required mock UI has not been approved by the user.
- Treat logging, telemetry, and error handling as part of artifact ownership: specs define
  externally relevant human/agent/operator diagnostics, privacy/redaction constraints,
  telemetry events/metrics/traces, error categories, user-facing error behavior, and
  support/debugging needs or non-goals; designs define structured logging, correlation
  IDs, event/metric/trace contracts, sinks/retention, redaction, alert hooks, and
  layer-specific error mapping/recovery/degradation strategy; plans assign that work and
  verification to PRs; code implements and tests it without leaking secrets, stack traces,
  raw objects, or unstable internals to users or logs.
- Treat downstream assessment/review as an upstream validation point. If design, plan, or
  code assessment/review reveals a latent issue in an earlier artifact, stop and tell the user which
  upstream artifact needs revision.
- For defect remediation, reconcile artifacts before treating the work as code-only. If a
  defect exposes missing requirements, unclear boundary contracts, omitted UX quality,
  missing logging/telemetry/error-handling intent, unrealistic tests, or mock drift, update
  the spec/design/plan and record the prevention lesson in the review report, ADR, decision
  log, or retrospective note used by the target repo.
- Use an adversarial review posture. Prefer a fresh context, separate reviewer, or different
  model/tool when available. If the same agent performs creation and review, say review was
  not independent and actively seek counterexamples, traceability theater, and unverified
  claims before passing.
- When the platform supports sub-agents, split every assessment into two fresh-context
  sub-agent passes. The Mechanical Verifier runs deterministic/structural checkers and
  returns raw command evidence, metrics, IDs, and failures. The Qualitative Reviewer starts
  from the artifact plus mechanical evidence and produces the adversarial judgment,
  upstream blockers, top fixes, and verdict. If sub-agents are unavailable, disclose that
  limitation and keep the verification and review sections separate.
- Never stop an assessment at checker JSON. Apply the verification/review checklist:
  - `/spec-verify`: run `check_spec.py`; `/spec-review`: qualitatively review spec quality;
    `/spec-assess`: do both.
  - `/design-verify`: run upstream `check_spec.py` and `check_design.py`; `/design-review`:
    qualitatively review upstream spec fitness and design quality; `/design-assess`: do both.
  - `/plan-verify`: run upstream `check_spec.py`, `check_design.py`, and `check_plan.py`;
    `/plan-review`: qualitatively review upstream fitness and plan quality; `/plan-assess`:
    do both.
  - `/code-verify`: run upstream checkers, `check_code.py`, pre-commit/equivalent gates,
    and planned logging/error-handling/build/docs/deployment checks; `/code-review`:
    qualitatively review code-readiness, implementation quality, test implementation
    quality, verification-oracle rigor, logging/telemetry/error-handling fitness, TDD
    evidence, scope fidelity, and gate fitness; `/code-assess`: do both.
- Use the lightweight track for spikes, throwaway prototypes, exploratory data/ML work,
  proof-of-concept integrations, or infrastructure investigations. Mark these artifacts
  Exploratory, timebox them, record goal/non-goals/risks/evidence/disposal criteria, and do
  not treat prototype code as production without follow-up code-ready artifacts or explicit
  user acceptance.
- Ask one focused question at a time when required information is missing. In YOLO mode,
  make the narrowest reasonable assumption, proceed, and record the assumption and its risk.
- Offer internet research for spec and design creation when current standards,
  regulations, platform behavior, APIs, or domain facts may matter.
- Keep implementation inside the plan's planned touch set. If code work needs files
  outside that scope, stop and ask the user to update or approve the plan.
- Run deterministic structural checkers after creating, verifying, or assessing artifacts. Prefer the
  checkers bundled in this skill at `checkers/check_*.py`; otherwise use the target
  workspace's `checkers/check_*.py` or this repository's `checkers/check_*.py`. Try `python`
  first, then `python3`, then `uv run python`.
- Treat checker results as structural evidence, not proof of correctness. The checkers catch
  missing sections, malformed IDs, orphan references, missing trace links, declared oversize
  PRs, missing Red/Green step text, unlabeled coverage output, missing same-test-block
  assertion trace IDs, oversize git diffs against the resolved review base, and obvious
  skip/TODO markers. Git diff-size and TDD evidence are required by default in code verify/assess;
  use allow-missing flags only when the repo cannot provide that evidence and the report
  states the limitation. Red/Green text, AT scenario shape, and commit-message TDD evidence
  are presence checks; they do not prove semantic correctness, test implementation quality,
  or true TDD history. Qualitative review must judge those from artifact content, code,
  tests, and available review/git evidence.
- Configure and run language-appropriate local quality gates for code work. Prefer
  repository-native tooling and pre-commit hooks where practical. For code-ready work, also
  run planned build/package commands and deployment dry-run/lint/plan/smoke/rollback checks
  where available, plus planned documentation build/generation/link/readability checks.

## Checkers

Use the bundled or installed `checkers/check_*.py` scripts when present:

- `check_spec.py` for specs.
- `check_design.py` for designs.
- `check_plan.py` for plans.
- `check_code.py` for code/test traceability and quality gates.

If the scripts are missing, report that deterministic verification is unavailable
and continue with the qualitative review required by the matching prompt.
