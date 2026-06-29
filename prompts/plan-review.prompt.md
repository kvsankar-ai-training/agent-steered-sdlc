---
description: Critically review a work plan with a deterministic mechanical pass and a qualitative pass, checking PR size, TDD, and full spec/design coverage, then report findings.
agent: agent
---

# Plan Review

Review a Work Plan against its principles: small reviewable PRs (≤300 LOC), Red/Green TDD,
full coverage of spec and design, explicit Planned Touch Sets, and always-shippable ordering.
Produce the verification sequence below.

Do not stop after checker JSON. This review must include:

1. Verification 0: upstream spec/design structural evidence plus qualitative upstream fitness.
2. Verification A: structural `check_plan.py` evidence.
3. Verification B: qualitative plan assessment.

When the platform supports sub-agents, run these as two fresh-context passes:

- **Mechanical Reviewer sub-agent**: run upstream spec/design checkers and the plan checker,
  returning raw evidence, metrics, IDs, and command failures.
- **Qualitative Reviewer sub-agent**: read the plan, upstream artifacts, and mechanical
  evidence, then judge upstream fitness and plan quality adversarially.

If sub-agents are unavailable, state that limitation and keep the mechanical and qualitative
sections separate.

Target the plan file the user provides (default `plan.md`). Do not edit it unless asked;
report findings only. Pass `--spec spec.md` and `--design design.md` so FR/AT/COMP refs
resolve. For a feature/component or slice/change plan, add `--feature` and
`--parent <product-plan>`.

Use an adversarial review posture: try to refute the slicing, find missing upstream
spec/design changes, touch-set gaps, PRs that are too large in reality, weak Red steps,
dependency traps, and traceability theater. Prefer a fresh context, separate reviewer, or
different model/tool when available. If the same agent that created the plan is reviewing it,
state that the review is not independent.

## Verification 0 — Upstream Consistency Gate

Before reviewing the plan itself, check whether the upstream spec and design are fit to
plan from. If the files exist, run:

```pwsh
python checkers/check_spec.py spec.md --json
python checkers/check_design.py design.md --spec spec.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry checker commands
with `python3`; if that is unavailable, retry with `uv run python`.

Then read enough of `spec.md` and `design.md` to detect latent upstream issues exposed by
the plan, including ambiguous or conflicting requirements, missing acceptance criteria,
unmeasurable NFRs, component boundaries that do not realize requirements, missing interfaces,
untestable design choices, unresolved dependencies, unclear migration/rollout constraints,
or scope that cannot be sliced into reviewable PRs.

If either upstream checker fails, or if plan review reveals that the spec or design must
change before the plan can be judged fairly, **stop the plan review**. Report an
**Upstream blocker** with the exact spec/design IDs/sections affected, why the plan cannot
be reliably reviewed, and the recommended upstream revision. Do not continue to Verification
A or B for the plan until the upstream issue is resolved.

## Verification A — Mechanical / Deterministic (run the tool)

Run the bundled checker and report its output verbatim. This is a deterministic
**structural** check: it catches section, ID, orphan-reference, declared coverage, declared
LOC, Red/Green-step, dependency-order, and banned-word issues. It does not prove PR size from
the actual diff, prove TDD history, or prove the plan slices are substantively good;
Verification B must judge that.

```pwsh
python checkers/check_plan.py <plan.md> --spec spec.md --design design.md --json
```

If all Python runners fail (`python`, `python3`, and `uv run python`), report the runner
failures and fall back to manual checks.

It exits `0` only if every structural gate passes (non-zero otherwise) and emits metrics:

- **counts** per ID kind (MILE/WORK/PR) and **plan_kind** (`breakdown` or `implementation`).
- **fr_coverage_pct / uc_coverage_pct / nfr_coverage_pct / at_coverage_pct / comp_coverage_pct** — must each be **100%**, meaning each required ID is referenced by child `WORK-` items in a Breakdown plan or `PR-` items in an Implementation plan.
- **uncovered_frs / uncovered_ucs / uncovered_nfrs / uncovered_ats / uncovered_comps** — must be empty.
- **work_items** — child work items for a Breakdown plan.
- **oversized_prs** — implementation PRs declaring more than 300 LOC. This is a declared
  plan estimate, not measured diff size. Must be empty.
- **prs_missing_loc** — implementation PRs without an estimated LOC declaration. Must be empty.
- **prs_missing_tdd** — implementation PRs lacking a Red and a Green step. Must be empty.
- **forward_deps** — PRs depending on a later-numbered PR. Must be empty.
- **orphan_refs**, **duplicates**, **bad_id_numbers** — must be empty.
- **vague_hits** — count of "etc.", "and/or", "tbd", "as appropriate", "various".
- **gates** + `passed/total`.

Present the JSON, then `passed/total` and the five coverage percentages. List every
uncovered/oversized/missing-LOC/non-TDD/orphan ID explicitly.

## Verification B — Qualitative

Reasoned judgment, scored 1–5 with one concrete fix each:

- **PR sizing** — slices are coherent, ≤300 LOC, single-concern, reviewable.
- **Plan type and readiness fit** — the plan declares product/system, feature/component, or
  slice/change scope; declares Breakdown or Implementation plan type; and marks
  Implementation Readiness realistically. Breakdown plans may pass as Decomposable, but only
  Implementation plans with concrete `PR-` items may be Code-ready for `/code-create`.
- **Scope-specific content completeness** — product/system plans carry milestones, child
  feature/component `WORK-` items, dependencies, required child specs/designs/ADRs, research
  or decision needs, sequencing, parallel tracks, risks, and readiness targets;
  feature/component plans carry child slice/change work or code-ready PRs, child artifact
  needs, integration order, test allocation, and touch-scope risks; slice/change plans carry
  concrete `PR-` items, Planned Touch Sets, Red/Green steps, test levels, LOC estimates,
  quality gates, rollback, dependencies, and worktree guidance.
- **TDD discipline** — planned Red steps precede Green steps and are meaningful, not coverage
  theater. The structural checker only verifies Red/Green step text; use judgment here.
- **Coverage** — no requirement/component silently skipped; NFRs scheduled.
- **Test-level allocation** — each `AT-` maps to an executable acceptance/e2e/API workflow
  test PR or justified non-code verification, while unit/pure-core, component, contract,
  integration, UI/accessibility/visual, quality-attribute, migration, and operational tests
  from the design are scheduled near the code they protect.
- **Planned Touch Sets** — every PR names the files/directories/modules/config/docs/generated
  artifacts and spec/design/plan sections it may touch, with narrow enough scope for
  `/code-create` to detect out-of-scope edits.
- **Sequencing** — always-green, no forward deps, sensible flags/migrations, and clear
  integration order.
- **Parallelism and worktrees** — waves and critical path are correct; concurrent PRs avoid
  shared-file conflicts or identify them through touch-set overlaps; independent branches say
  whether separate Git worktrees are recommended and how they rejoin.
- **Production quality** — error handling, NFR validation, rollback per PR.

If a `plan.html` companion exists, confirm its dependency graph and wave/Gantt view match
`plan.md` (same PR-IDs, same depends-on edges); flag any divergence.

## Report format

If blocked by Verification 0:

1. **Upstream blocker** (spec/design IDs or sections + why it blocks plan review).
2. Required upstream changes.
3. **Verdict**: Blocked-upstream.

Otherwise:

1. Mechanical scorecard (✅/❌ + IDs + totals).
2. Qualitative scorecard (1–5 + fixes, including Planned Touch Set adequacy).
3. **Top fixes** ranked by impact.
4. **Verdict**: Pass / Pass-with-fixes / Needs rework.
