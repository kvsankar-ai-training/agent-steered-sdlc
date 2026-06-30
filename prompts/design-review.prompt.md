---
description: Critically review a Software Design Document with a deterministic mechanical pass and a qualitative pass against requirements, stakeholder concerns, quality attributes, architecture/documentation/build/deploy views, interfaces, decisions, risks, and testability.
agent: agent
---

# Design Review

Review a Software Design Document against broad software design practice: requirements and
stakeholder concerns, context and boundaries, quality attributes and trade-offs, appropriate
architecture views, cohesive components, explicit interfaces, data/state/side effects,
testability, operability, decisions, risks, and technical debt. Produce the verification
sequence below.

Do not stop after checker JSON. This review must include:

1. Verification 0: upstream spec structural evidence plus qualitative upstream fitness.
2. Verification A: structural `check_design.py` evidence.
3. Verification B: qualitative design assessment.

When the platform supports sub-agents, run these as two fresh-context passes:

- **Mechanical Reviewer sub-agent**: run the upstream spec checker and design checker,
  returning raw evidence, metrics, IDs, and command failures.
- **Qualitative Reviewer sub-agent**: read the design, upstream spec, and mechanical
  evidence, then judge upstream fitness and design quality adversarially.

If sub-agents are unavailable, state that limitation and keep the mechanical and qualitative
sections separate.

Use design principles such as single responsibility, cohesion, low coupling, encapsulation,
separation of concerns, acyclic dependencies, explicit contracts, testability, least
sufficient mechanism/YAGNI, useful DRY, and fail-safe behavior as review heuristics. Do not
apply them mechanically; judge whether they improve the design against its requirements,
quality attributes, and likely change scenarios.

Also judge whether the design uses the right profile-specific artifacts. Backend/API/service
designs should include context, service/container, component/module, API/event contract,
data/state, runtime flow, build/release, deployment/operations, developer documentation,
and test views. Web frontend designs should
include route/page structure, component hierarchy, UX interaction states, state management,
data-fetch/API contracts, accessibility, responsive behavior, performance/security,
build/release, user/developer documentation, and tests.
Mobile designs should include platform scope, navigation, screen contracts, state/data flow,
offline/sync where applicable, permissions/capabilities, lifecycle/background behavior,
performance/battery budgets, build/release, user/developer documentation,
release/observability, and tests. OO/UML-heavy designs should
include logical components/packages, class/domain model, sequence diagrams, state diagrams
where relevant, and interface contracts.

Target the design file the user provides (default `design.md`). Do not edit it unless
asked; report findings only.

Use an adversarial review posture: try to refute the design, find missing upstream spec
changes, unaddressed quality attributes, hidden coupling, weak test strategy, and
traceability theater. Prefer a fresh context, separate reviewer, or different model/tool
when available. If the same agent that created the design is reviewing it, state that the
review is not independent.

If reviewing a **component design** (a subset referencing a parent product design), add
`--component` and point `--parent` at the product design so its IDs are not orphans. If a
spec exists, pass `--spec spec.md` so `FR-`/`UC-` references resolve. Otherwise review whole.

## Verification 0 — Upstream Consistency Gate

Before reviewing the design itself, check whether the upstream spec is fit to design from.
If `spec.md` exists, run:

```pwsh
python checkers/check_spec.py spec.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry checker commands
with `python3`; if that is unavailable, retry with `uv run python`.

Then read the spec enough to detect latent upstream issues exposed by the design, including
ambiguous requirements, contradictory requirements, missing acceptance criteria, missing or
unmeasurable NFRs, missing build/release/deployment requirements, missing documentation
requirements, unclear actors/use cases, unresolved scope boundaries, or requirements that
already dictate implementation without justification.

If the spec checker fails, or if design review reveals that the spec must change before the
design can be judged fairly, **stop the design review**. Report an **Upstream spec blocker**
with the exact spec IDs/sections affected, why the design cannot be reliably reviewed, and
the recommended spec revision. Do not continue to Verification A or B for the design until
the upstream issue is resolved.

## Verification A — Mechanical / Deterministic (run the tool)

Run the bundled checker and report its output verbatim. This is a deterministic
**structural** check: it catches section, ID, orphan-reference, component coverage,
interface-owner, dependency-cycle, and banned-word issues. It does not prove the design is
correct, sufficient, or substantively testable; Verification B must judge that.

```pwsh
python checkers/check_design.py <design.md> --json
```

For a component design: `python checkers/check_design.py <comp.md> --component --parent <product.md> --spec spec.md --json`

It exits `0` only if every structural gate passes (non-zero otherwise) and emits metrics:

- **counts** per ID kind (LAYER/COMP/IFACE/DEC/RISK).
- **comp_req_coverage_pct** — must be **100%** (every component block references ≥1
  `FR-`/`UC-`).
- **comp_test_coverage_pct** — must be **100%** (every component ID appears in Test Strategy).
- **uncovered_components / untested_components** — must be empty.
- **iface_owner_count** — each interface declares exactly one real `owner: COMP-...` (no orphans, no dupes).
- **dependency_cycles** — must be empty (component dependencies through interfaces have no cycles).
- **orphan_refs** — IDs referenced but never defined.
- **duplicates** — IDs defined more than once.
- **suffixed_ids** — design IDs must have no numeric suffix (use `COMP-RULES`, not `COMP-RULES-10`).
- **vague_hits** — count of "etc.", "and/or", "tbd", "as appropriate", "simple", "robust".
- **gates** + `passed/total`.

If `python` is unavailable or fails because the launcher is missing, retry the same command
with `python3`; if that is unavailable, retry with `uv run python`. Only fall back to manual
checks after all three runners fail, and report the runner failures.
Present the JSON, then `passed/total` and both coverage percentages. List every
uncovered/untested/orphan/duplicate ID, owner issue, and cycle explicitly.

## Verification B — Qualitative

Reasoned judgment, scored 1–5 with one concrete fix each:

- **Requirements and stakeholder fit** — design choices trace to FRs/NFRs/UCs, stakeholder
  concerns, constraints, risks, or operational realities.
- **Context and scope** — system boundary, external systems, actors, trust boundaries,
  build/release boundary, deployment environment, and ownership are understandable before internals.
- **Quality attribute design** — performance, availability, modifiability, security, privacy,
  usability, accessibility, observability, deployability, interoperability, scalability, and
  cost are addressed with concrete scenarios, tactics, or explicit trade-offs.
- **Architecture views** — static structure, runtime behavior, data, build/release,
  deployment/operations, documentation, and cross-cutting concepts are documented at the
  right level of detail.
- **Profile-specific completeness** — the selected design kind has the expected minimum
  artifacts, such as backend service/API views, frontend route/component/state views, mobile
  navigation/screen/offline/permission/lifecycle views, or OO/UML logical/class/sequence views.
- **Scope, depth, and readiness fit** — the design declares product/system HLD,
  feature/component design, or slice/change LLD scope and a realistic Implementation
  Readiness. HLDs may pass as Decomposable; only sufficiently local LLD/slice designs should
  be marked Code-ready.
- **Scope-specific content completeness** — product/system HLDs carry context, major
  containers/services/modules, drivers, boundaries, data ownership, quality tactics,
  build/package/release strategy, deployment/operations strategy, ADRs, risks,
  documentation strategy, decomposition candidates, and system test strategy;
  feature/component designs carry responsibilities, contracts, local state, flows,
  core/shell partition, dependencies, build/deployment impacts, documentation impacts,
  decisions, risks, and test matrix; slice/change LLDs carry exact local changes,
  API/schema/data deltas, failure paths, validation/policy logic, build/deployment script or
  artifact changes, documentation changes, migration/rollback, side effects, test
  doubles/levels, and likely touch candidates.
- **Cohesion and coupling** — components have focused responsibilities, stable interfaces,
  explicit dependencies, and no unintentional cycles or boundary leaks.
- **Design heuristics** — single responsibility, information hiding, separation of concerns,
  least sufficient mechanism/YAGNI, useful DRY, and fail-safe behavior are applied where
  they reduce real risk without adding speculative abstraction.
- **Interfaces and contracts** — APIs/events/schemas/protocols define ownership, inputs,
  outputs, errors, auth/trust, compatibility, and quality expectations.
- **State, data, and side effects** — mutable state, persistence, consistency, transactions,
  concurrency, time, external calls, retries, migrations, and recovery are deliberate.
- **Functional core / imperative shell** — pure decision logic, rules, validation, state
  transitions, calculations, reducers, mappers, and invariants are separated from I/O,
  persistence, UI/navigation, framework glue, network/device/browser APIs, time, randomness,
  messaging, retries, analytics, and observability, with test strategy matching each side.
  If the design uses an equivalent separation or says the split is not applicable, the
  explanation is specific, justified by the architecture style, and still protects testability.
- **Testability and operability** — components and contracts are testable in isolation and
  collaboration; the design distinguishes acceptance/e2e, unit/pure-core, component,
  contract, integration, UI/accessibility/visual, quality-attribute, migration, and
  operational checks as applicable; observability, failure handling, rollout/rollback, and
  operational checks exist.
- **Build and deployment design** — deployable artifacts, package boundaries, build commands,
  CI/CD or release workflow, artifact storage, environment promotion, configuration/secrets,
  migrations, rollout/rollback, dry-run/validation, smoke checks, and ownership are explicit
  where relevant.
- **User and developer documentation design** — documentation audiences, information
  architecture, source locations, generated/reference docs, examples, diagrams, runbooks,
  publishing/versioning, ownership, review triggers, and doc validation checks are explicit
  where relevant.
- **Decision quality** — decisions include alternatives, rationale, consequences, quality
  attributes affected, user input or recorded assumptions, reversibility, ADR links for
  material decisions, and revisit triggers.
- **Risks and evolution** — technical debt, residual risk, likely change points, migration
  strategy, and mitigation ownership are explicit.

## Report format

If blocked by Verification 0:

1. **Upstream spec blocker** (IDs/sections + why it blocks design review).
2. Required spec changes.
3. **Verdict**: Blocked-upstream.

Otherwise:

1. Mechanical scorecard (✅/❌ + IDs + totals).
2. Qualitative scorecard (1–5 + fixes).
3. **Top fixes** ranked by impact.
4. **Verdict**: Pass / Pass-with-fixes / Needs rework.

## Human review gate (hard stop)

After reporting the design review verdict, **stop**. Do not start `/plan-create` or any
downstream artifact in the same turn. The next stage requires explicit user approval or an
explicit unattended end-to-end instruction in the user's latest message.
