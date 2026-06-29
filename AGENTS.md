# AGENTS.md

Guidance for AI coding agents working in this repository. The workflow here is
**spec-first**: author a Software Requirements Specification, review it, then build.

## First-class source folders

This is a prompt, skill, and checker repository. Canonical source files live in:

- [docs](docs): user-facing overview pages, including
  [agent-steered-sdlc.html](docs/agent-steered-sdlc.html) and
  [review-verification-checklist.md](docs/review-verification-checklist.md).
- [prompts](prompts): reusable slash-command prompt definitions.
- [skills](skills): native skill bundles such as `agent-steered-sdlc`.
- [checkers](checkers): deterministic structural verification scripts used by the prompts.
  Shared checker section schemas live in [checkers/schemas.py](checkers/schemas.py).
- [scripts](scripts): installers for Windows, macOS, and WSL/Linux targets.

Do not treat `.github` as the source location in this repository. `.github/prompts`
is only an installation target for GitHub Copilot inside product workspaces.

## Slash commands

Eight source command prompts live in [prompts](prompts):

- **`/spec-create`** — [prompts/spec-create.prompt.md](prompts/spec-create.prompt.md)
  Interviews the user one question per turn, then writes a requirements-engineering
  grounded SRS. Supports product/system, feature/component, and slice/change specs.
  Writes `spec.md` in the target product workspace unless another file is named.
- **`/spec-review`** — [prompts/spec-review.prompt.md](prompts/spec-review.prompt.md)
  Critically reviews a spec in two passes: a deterministic mechanical check plus a
  qualitative 1–5 assessment, ending in a verdict.
- **`/design-create`** — [prompts/design-create.prompt.md](prompts/design-create.prompt.md)
  Interviews the user one question per turn, then writes a Software Design Document
  grounded in requirements, design profiles, functional-core/imperative-shell separation,
  trade-offs, ADRs, quality attributes, interfaces, tests, and risks. Writes `design.md`
  plus a `design.html` companion in the target product workspace. Supports HLD,
  feature/component design, and slice/change LLD.
- **`/design-review`** — [prompts/design-review.prompt.md](prompts/design-review.prompt.md)
  Critically reviews a design in two passes: a deterministic mechanical check plus a
  qualitative 1–5 assessment against the design criteria, ending in a verdict.
- **`/plan-create`** — [prompts/plan-create.prompt.md](prompts/plan-create.prompt.md)
  Interviews the user one question per turn, then writes a work plan that slices spec +
  design into reviewable, Red/Green TDD pull requests of ≤300 LOC each, including Planned
  Touch Sets and parallel/worktree guidance. Writes `plan.md` in the target product workspace.
- **`/plan-review`** — [prompts/plan-review.prompt.md](prompts/plan-review.prompt.md)
  Critically reviews a plan in two passes: a deterministic mechanical check plus a
  qualitative 1–5 assessment, ending in a verdict.
- **`/code-create`** — [prompts/code-create.prompt.md](prompts/code-create.prompt.md)
  Implements the plan PR-by-PR with strict Red/Green/Refactor TDD; tests reference the
  FR/AT/COMP and PR they cover, suite stays green at each PR boundary, and language-aware
  pre-commit/local quality gates are configured and run.
- **`/code-review`** — [prompts/code-review.prompt.md](prompts/code-review.prompt.md)
  Critically reviews the implementation with upstream checks, structural code gates,
  pre-commit/local quality-gate verification, and a qualitative 1–5 assessment.

## Test responsibility by command

- `/spec-create` writes `AT-` acceptance tests as requirements-level, black-box acceptance
  criteria in the spec. These are not executable unit/component/integration tests.
- `/design-create` defines the test architecture: acceptance/e2e, unit/pure-core,
  component, contract, integration, UI/accessibility/visual, quality-attribute, migration,
  and operational checks as applicable.
- `/plan-create` assigns those test levels to PRs. Each `AT-` must map to an executable
  acceptance/e2e/API workflow test PR or justified non-code verification, and lower-level
  tests should sit near the code they protect.
- `/code-create` writes executable tests using Red/Green/Refactor: acceptance tests for
  assigned `AT-` items plus the planned lower-level tests.
- Review commands verify the same ownership chain and stop if a downstream artifact exposes
  missing or incorrect upstream test intent.

## Work scope and readiness

Commands use a deliberately small work hierarchy:

- **Product/system**: broad problem, system boundary, major capabilities, HLD. Usually not
  code-ready.
- **Feature/component**: coherent user-facing feature, component, subsystem, or integration.
  May need child slices before implementation.
- **Slice/change**: smallest implementable unit, normally PR-sized or a small PR cluster.
  This is the usual code-ready scope.

Artifacts declare `Implementation Readiness: Exploratory | Decomposable | Code-ready`.
Parent specs/designs/plans may pass review while Decomposable; that means the next step is a
breakdown plan, child spec, LLD, ADR/interface contract, or implementation plan. `/code-create`
must block unless it has a code-ready implementation plan for a slice/change or sufficiently
small feature/component.

## Lightweight track

For spikes, throwaway prototypes, exploratory data/ML work, proof-of-concept integrations,
or infrastructure investigations where full SDLC ceremony would create more noise than
signal, use a documented lightweight track instead of bypassing the process silently:

- Record the work as `Implementation Readiness: Exploratory`.
- Write a short spike note or lightweight plan with goal, timebox, assumptions, non-goals,
  risks, experiment steps, disposal/productionization criteria, and what evidence would
  justify moving into the normal spec/design/plan/code flow.
- Do not mark lightweight artifacts Code-ready and do not treat prototype code as production
  implementation unless a follow-up slice/change spec, design/LLD, and implementation plan
  are created or explicitly accepted by the user.

## Review independence

Review prompts should be run with an adversarial posture. Prefer a fresh context, separate
reviewer, or different model/tool when available. If the same agent performs creation and
review, it must say that review was not independent and actively look for counterexamples,
missing upstream changes, traceability theater, and unverified claims before passing.

When the platform supports sub-agents, split every review into two fresh-context sub-agent
passes:

- **Mechanical Reviewer**: runs deterministic/structural checkers and returns raw command
  evidence, metrics, IDs, and failures.
- **Qualitative Reviewer**: starts from the artifact plus mechanical evidence and produces
  the adversarial judgment, upstream blockers, top fixes, and verdict.

If sub-agents are unavailable, disclose that limitation and still keep the mechanical and
qualitative sections separate.

## Review verification checklist

Every review must pair structural/mechanical evidence with qualitative assessment, ideally
using the two fresh-context sub-agent passes above. Do not stop after checker JSON. The
canonical checklist is
[docs/review-verification-checklist.md](docs/review-verification-checklist.md):

| Review | Mechanical/structural evidence | Qualitative assessment |
| --- | --- | --- |
| `/spec-review` | `check_spec.py` on the target spec. | Spec quality: problem framing, needs, non-goals, scope/readiness, use cases, requirements, NFRs, acceptance tests, traceability. |
| `/design-review` | `check_spec.py` on upstream spec, then `check_design.py` on design. | First judge upstream spec fitness; then judge design quality, decisions, risks, testability, and traceability. |
| `/plan-review` | `check_spec.py` + `check_design.py` on upstream artifacts, then `check_plan.py` on plan. | First judge upstream spec/design fitness; then judge plan slicing, TDD, touch sets, test allocation, sequencing, and worktrees. |
| `/code-review` | `check_spec.py` + `check_design.py` + `check_plan.py`, `check_code.py`, and pre-commit/equivalent gate. | First judge upstream code-readiness; then judge implementation correctness, test quality, TDD evidence, scope fidelity, production quality, and quality-gate fitness. |

Agents should infer the likely scope from the user's request and state it explicitly:
broad product/platform/app requests map to Product/system, one capability/subsystem maps to
Feature/component, and bug fixes, PR-sized changes, or local behavior deltas map to
Slice/change. Ask only when the mapping is ambiguous or materially changes the artifact.

## Artifact matrix

| Scope | Spec carries | Design carries | Plan carries |
| --- | --- | --- | --- |
| Product/system | Mission, stakeholders, boundary, product needs, non-goals, major capabilities, representative use cases, major NFRs, broad acceptance intent, child-artifact needs. | HLD: context, major containers/services/modules, drivers, boundaries, data ownership, quality tactics, deployment/operations strategy, ADRs, risks, decomposition candidates. | Breakdown plan: milestones, feature/component `WORK-` items, dependencies, required child specs/designs/ADRs, research/decision needs, parallel tracks, readiness targets. |
| Feature/component | Parent refs, local goal, actors, concrete behavior, FR/NFR/AT coverage, edge cases, integration/business rules, dependencies, non-goals. | Feature/component design: responsibilities, contracts, local state/data, runtime flows, core/shell split, dependencies, UX/API contracts, decisions, risks, test matrix. | Breakdown or implementation plan: child slice/change work or PRs, child artifact needs, integration order, test allocation, touch-scope risks. |
| Slice/change | Exact requirement delta, parent IDs refined/preserved, changed and unchanged behavior, edge cases, executable or justified non-code acceptance criteria. | LLD: touched components/modules, API/schema/data deltas, failure paths, validation/policy logic, migration/rollback, side effects, test levels/doubles, likely touch candidates. | Implementation plan: `PR-` items, Planned Touch Sets, Red/Green steps, test levels, LOC estimates, quality gates, rollback, dependencies, worktree guidance. |

## Local quality gates

This repository uses `uv` for tool and environment management. Do not install lint tools
through pre-commit remote hook repositories, npm, pipx, or global package managers.

Install the Git hook in a valid Git checkout with:

```pwsh
uv run pre-commit install
```

Run the configured hooks manually with:

```pwsh
uv run pre-commit run --all-files
```

The local hooks invoke:

- `uv run ruff check` for Python linting.
- `uv run ruff format --check` for Python format checks.
- `uv run pymarkdown --enable-extensions front-matter,markdown-tables -d md013 scan`
  for Markdown linting.

## Mechanical checkers

[checkers/check_spec.py](checkers/check_spec.py) enforces structural spec hygiene:
ID format, zero-gap numbering, duplicates, orphan refs, UC→AT and FR→AT reference coverage,
NFR unit presence, obvious NFR unit/quality mismatches, AT scenario shape, and banned vague
terms.

```pwsh
python checkers/check_spec.py spec.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry the same checker
command with `python3`; if that is unavailable, retry with `uv run python`.

Flags: `--json`, `--feature` (focused feature/component or slice/change mode), `--parent <file>`
(validate refs against a parent spec). Exits non-zero on any gate failure.

[checkers/check_design.py](checkers/check_design.py) enforces structural design hygiene:
ID format, duplicates, orphan refs, component→requirement references, component mentions in
test strategy, single interface ownership, interface-derived dependency cycles, and banned
vague terms.

```pwsh
python checkers/check_design.py design.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry the same checker
command with `python3`; if that is unavailable, retry with `uv run python`.

Flags: `--json`, `--component` (single-component mode), `--parent <file>` (parent
design), `--spec <file>` (resolve FR/UC refs). Exits non-zero on any gate failure.

[checkers/check_plan.py](checkers/check_plan.py) enforces structural plan hygiene:
ID format, zero-gap numbering, duplicates, orphan refs, FR/AT/COMP reference coverage,
declared 300-LOC PR estimates, Red/Green step text, no forward dependencies, and banned
vague terms.

```pwsh
python checkers/check_plan.py plan.md --spec spec.md --design design.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry the same checker
command with `python3`; if that is unavailable, retry with `uv run python`.

Flags: `--json`, `--feature` (focused feature/component or slice/change mode), `--parent <file>`,
`--spec <file>`, `--design <file>`. Exits non-zero on any gate failure.

[checkers/check_code.py](checkers/check_code.py) runs the test suite and enforces structural
code/test hygiene: tests pass, labeled coverage output ≥ threshold, PR-ID and FR/AT/COMP
test-text traceability, the per-module LOC ceiling, and no TODO/FIXME/skip markers.

```pwsh
python checkers/check_code.py --plan plan.md --tests-argv '["pytest","-q"]' --cov-min 80 --json
```

If `python` is unavailable or fails because the launcher is missing, retry the same checker
command with `python3`; if that is unavailable, retry with `uv run python`.

Flags: `--json`, `--tests-argv <json-array>`, `--tests <cmd>`, `--tests-shell`,
`--cov-min <n>`, `--tests-dir <dir>`, `--src <dir>`, `--max-loc <n>`,
`--max-diff-loc <n>`, `--diff-base <ref>`, `--require-git-evidence`,
`--require-tdd-evidence`, `--spec <file>`, `--design <file>`. Exits non-zero on any gate
failure.

Checker limits: these scripts are deterministic structural gates. They catch missing
sections, malformed IDs, orphan references, missing trace links, declared oversize PRs,
missing Red/Green step text, unlabeled coverage output, missing assertion-adjacent trace
IDs, oversize git diffs when a base is supplied, and obvious skip/TODO markers. They do not
prove semantic correctness, test quality, or true TDD history; the qualitative review prompts
must judge those concerns from the artifact content, code, tests, and available review/git
evidence.

## Installation

Canonical source prompts live in [prompts](prompts), skills live in [skills](skills),
and checker code lives in [checkers](checkers). Use the install scripts to copy/adapt
them into tool-specific locations for a product workspace:

```pwsh
.\scripts\install.ps1 -TargetRoot D:\path\to\product -Tool all -Scope project
```

```sh
scripts/install.sh --target /path/to/product --tools all --scope project
```

On Windows, `install.ps1` also installs the matching WSL targets when WSL is available.
Inside WSL, `install.sh` also installs the matching Windows targets when `powershell.exe`
is available. Use `-NoCrossInstall` or `--no-cross-install` to install only in the current
environment.

Install targets:

- Codex: `<target>/.codex/skills/agent-steered-sdlc` or
  `$CODEX_HOME/skills/agent-steered-sdlc` / `~/.codex/skills/agent-steered-sdlc`.
- GitHub Copilot: `<target>/.github/prompts/*.prompt.md`.
- Claude Code: `<target>/.claude/commands/*.md` or `~/.claude/commands/*.md`, plus
  the `agent-steered-sdlc` skill under `<target>/.claude/skills/` or `~/.claude/skills/`.
- Gemini CLI: `<target>/.gemini/commands/*.toml` or `~/.gemini/commands/*.toml`.
- Claude and Pi: exported prompt packs under `.ai-prompts/` because they do not expose a
  stable local slash-command folder. The export also includes the `agent-steered-sdlc`
  skill bundle for manual import/adaptation.
- Checkers: copied to `<target>/checkers` unless `--no-checkers` / `-NoCheckers` is used.

## Repository layout

This repository is for the prompt/checker command definitions themselves. Do not keep
product-specific specs, designs, plans, generated companion HTML, or implementation code at
the root of this command repository.

When using these commands for a real product, run them in that product workspace or create a
sibling workspace under `D:\stellantis\batch-1`. Product artifacts should live there as
`spec.md`, `design.md`, `design.html`, `plan.md`, `plan.html`, source code, tests, and
tooling config.

The previous sample tic-tac-toe product artifacts were moved to
`D:\stellantis\batch-1\ttt-python-from-commands`.
