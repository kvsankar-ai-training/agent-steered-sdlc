---
name: agent-steered-sdlc
description: End-to-end SDLC workflow for agent-steered creation, review, verification, and reconciliation of requirements, designs, ADRs, plans, code, tests, quality gates, and upstream/downstream artifact consistency. Use when Codex needs to run or review an artifact-governed software delivery lifecycle.
---

# Agent-Steered SDLC

Use the installed slash commands when they are available. If the commands are not
installed, locate this repository's `prompts/*.prompt.md` and follow the matching
prompt exactly.

## Workflow

Select the narrowest command that matches the user's current artifact:

- `/spec-create`: create or revise `spec.md`, including product/system,
  feature/component, and slice/change specs.
- `/spec-review`: review requirements and stop if the spec has material issues.
- `/design-create`: create or revise `design.md`, diagrams, and ADRs from the spec.
- `/design-review`: review design and stop if upstream spec ambiguity or design risk blocks safe progress.
- `/plan-create`: create `plan.md`, planned touch sets, PR slices, TDD order, and worktree/parallel-work guidance.
- `/plan-review`: review plan and stop if spec/design issues or planned scope issues block implementation.
- `/code-create`: implement within the planned touch set using Red/Green/Refactor TDD and configured quality gates.
- `/code-review`: review implementation, tests, traceability, pre-commit quality gates, and upstream consistency.

## Operating Rules

- Preserve the spec-first order: spec, spec review, design, design review, plan,
  plan review, code, code review.
- Use the three-scope model: product/system, feature/component, slice/change. Every artifact
  should declare Implementation Readiness as Exploratory, Decomposable, or Code-ready.
  Parent artifacts may pass as Decomposable; `/code-create` must only proceed from a
  code-ready implementation plan for a slice/change or sufficiently small feature/component.
- Infer the likely scope from the user's request and state it explicitly. Broad
  product/platform/app requests map to product/system, one capability/subsystem maps to
  feature/component, and bug fixes, PR-sized changes, or local behavior deltas map to
  slice/change. Ask only when the mapping is ambiguous or materially changes the artifact.
- Apply the artifact matrix:
  - Product/system spec carries mission, stakeholders, boundary, product needs, non-goals,
    major capabilities, representative use cases, major NFRs, broad acceptance intent, and
    child-artifact needs; design carries HLD context, major containers/services/modules,
    drivers, boundaries, data ownership, quality tactics, deployment/operations, ADRs,
    risks, and decomposition candidates; plan is normally a Breakdown plan with
    feature/component `WORK-` items, dependencies, child artifact needs, parallel tracks,
    and readiness targets.
  - Feature/component spec carries parent references, local behavior, FR/NFR/AT coverage,
    edge cases, dependencies, and non-goals; design carries responsibilities, contracts,
    local state/data, runtime flows, core/shell split, dependencies, decisions, risks, and
    test matrix; plan carries child slice/change work or PRs, integration order, test
    allocation, and touch-scope risks.
  - Slice/change spec carries the exact requirement delta, parent IDs refined/preserved,
    changed/unchanged behavior, and acceptance criteria; design carries LLD-level local
    changes, API/schema/data deltas, failure paths, validation/policy logic,
    migration/rollback, side effects, test levels/doubles, and likely touch candidates;
    plan carries concrete `PR-` items, Planned Touch Sets, Red/Green steps, test levels,
    LOC estimates, quality gates, rollback, dependencies, and worktree guidance.
- Treat test ownership as part of artifact ownership: specs define `AT-` acceptance
  criteria; designs define the test architecture and lower-level test mix; plans assign
  executable test levels to PRs; code writes acceptance tests plus the planned lower-level
  tests using TDD.
- Treat downstream review as an upstream validation point. If design, plan, or code
  review reveals a latent issue in an earlier artifact, stop and tell the user which
  upstream artifact needs revision.
- Use an adversarial review posture. Prefer a fresh context, separate reviewer, or different
  model/tool when available. If the same agent performs creation and review, say review was
  not independent and actively seek counterexamples, traceability theater, and unverified
  claims before passing.
- When the platform supports sub-agents, split every review into two fresh-context sub-agent
  passes. The Mechanical Reviewer runs deterministic/structural checkers and returns raw
  command evidence, metrics, IDs, and failures. The Qualitative Reviewer starts from the
  artifact plus mechanical evidence and produces the adversarial judgment, upstream blockers,
  top fixes, and verdict. If sub-agents are unavailable, disclose that limitation and keep
  the mechanical and qualitative sections separate.
- Never stop a review at checker JSON. Apply the review verification checklist:
  - `/spec-review`: run `check_spec.py`, then qualitatively assess spec quality.
  - `/design-review`: run upstream `check_spec.py` and qualitatively assess spec fitness;
    then run `check_design.py` and qualitatively assess design quality.
  - `/plan-review`: run upstream `check_spec.py` and `check_design.py`, qualitatively assess
    upstream fitness; then run `check_plan.py` and qualitatively assess plan quality.
  - `/code-review`: run upstream spec/design/plan checkers and qualitatively assess
    code-readiness; then run `check_code.py`, pre-commit/equivalent gates, and qualitatively
    assess implementation quality, test quality, TDD evidence, scope fidelity, and gate
    fitness.
- Use the lightweight track for spikes, throwaway prototypes, exploratory data/ML work,
  proof-of-concept integrations, or infrastructure investigations. Mark these artifacts
  Exploratory, timebox them, record goal/non-goals/risks/evidence/disposal criteria, and do
  not treat prototype code as production without follow-up code-ready artifacts or explicit
  user acceptance.
- Ask one focused question at a time when required information is missing.
- Offer internet research for spec and design creation when current standards,
  regulations, platform behavior, APIs, or domain facts may matter.
- Keep implementation inside the plan's planned touch set. If code work needs files
  outside that scope, stop and ask the user to update or approve the plan.
- Run deterministic structural checkers after creating or reviewing artifacts. Try
  `python` first, then `python3`, then `uv run python`.
- Treat checker results as structural evidence, not proof of correctness. The checkers catch
  missing sections, malformed IDs, orphan references, missing trace links, declared oversize
  PRs, missing Red/Green step text, unlabeled coverage output, missing assertion-adjacent
  trace IDs, oversize git diffs when a base is supplied, and obvious skip/TODO markers. They
  do not prove semantic correctness, test quality, or true TDD history; qualitative review
  must judge those from artifact content, code, tests, and available review/git evidence.
- Configure and run language-appropriate local quality gates for code work. Prefer
  repository-native tooling and pre-commit hooks where practical.

## Checkers

Use the installed `checkers/check_*.py` scripts when present:

- `check_spec.py` for specs.
- `check_design.py` for designs.
- `check_plan.py` for plans.
- `check_code.py` for code/test traceability and quality gates.

If the scripts are missing, report that deterministic verification is unavailable
and continue with the qualitative review required by the matching prompt.
