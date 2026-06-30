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
  Touch Sets, documentation/build/deployment work, and parallel/worktree guidance. Writes
  `plan.md` in the target product workspace.
- **`/plan-review`** — [prompts/plan-review.prompt.md](prompts/plan-review.prompt.md)
  Critically reviews a plan in two passes: a deterministic mechanical check plus a
  qualitative 1–5 assessment, ending in a verdict.
- **`/code-create`** — [prompts/code-create.prompt.md](prompts/code-create.prompt.md)
  Implements the plan PR-by-PR with strict Red/Green/Refactor TDD; tests reference the
  FR/AT/COMP and PR they cover, suite stays green at each PR boundary, and language-aware
  pre-commit/local quality gates plus planned documentation/build/deployment checks are
  configured and run.
- **`/code-review`** — [prompts/code-review.prompt.md](prompts/code-review.prompt.md)
  Critically reviews the implementation, documentation, build/deployment work, upstream
  checks, structural code gates, pre-commit/local quality-gate verification, and a
  qualitative 1–5 assessment.

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

## Build and deployment responsibility by command

Build artifacts and deployment are first-class SDLC concerns. Do not defer them to the end
unless the artifact explicitly scopes them out.

- `/spec-create` captures externally relevant build, release, deployment, environment,
  rollout, rollback, migration, smoke-check, and operational acceptance needs as requirements
  or non-goals.
- `/design-create` defines the build/package/release architecture: deployable artifacts,
  CI/CD or release workflow, artifact storage, environments, configuration/secrets,
  promotion, deployment topology, migrations, rollout/rollback, validation, smoke checks,
  and ownership.
- `/plan-create` assigns build/deployment work to child `WORK-` items or PRs: build scripts,
  package manifests, generated outputs, CI/CD config, IaC/manifests, migration scripts,
  deployment dry runs, smoke checks, rollback checks, and release docs.
- `/code-create` implements and verifies the planned build/deployment work. It runs the
  build/package command, verifies the expected artifact, validates deployment scripts or
  manifests with dry-run/plan/lint/smoke checks where possible, and avoids live production
  deployment unless explicitly requested.
- Review commands check the same chain and stop with an upstream blocker when build or
  deployment intent is missing from the artifact that should own it.

## User and developer documentation responsibility by command

User and developer documentation are also first-class SDLC concerns. Do not leave them as a
last-minute README cleanup when users, developers, operators, support, auditors, or
integrators depend on them.

- `/spec-create` captures documentation audiences, tasks, discoverability,
  localization/accessibility, onboarding, API/reference, support, runbook, release-note, and
  acceptance needs as requirements or non-goals.
- `/design-create` defines the documentation architecture: information architecture, source
  locations, generated vs. hand-written docs, API/reference generation, examples, diagrams,
  publishing/versioning, ownership, review triggers, and validation checks.
- `/plan-create` assigns documentation work to child `WORK-` items or PRs: user guides,
  in-product help, README/API docs, examples, runbooks, troubleshooting, migration notes,
  release notes, generated reference docs, and doc build/link/accessibility checks.
- `/code-create` implements and verifies planned documentation work. It updates docs with
  the code, validates generated/reference docs and examples where practical, and avoids
  documenting unimplemented future behavior as current behavior.
- Review commands check the same chain and stop with an upstream blocker when documentation
  intent is missing from the artifact that should own it.

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
| `/spec-review` | `check_spec.py` on the target spec. | Spec quality: problem framing, needs, non-goals, scope/readiness, use cases, requirements, NFRs, acceptance tests, build/deployment intent, documentation intent, traceability. |
| `/design-review` | `check_spec.py` on upstream spec, then `check_design.py` on design. | First judge upstream spec fitness; then judge design quality, build/deployment design, documentation design, decisions, risks, testability, and traceability. |
| `/plan-review` | `check_spec.py` + `check_design.py` on upstream artifacts, then `check_plan.py` on plan. | First judge upstream spec/design fitness; then judge plan slicing, TDD, touch sets, test allocation, build/deployment allocation, documentation allocation, sequencing, and worktrees. |
| `/code-review` | `check_spec.py` + `check_design.py` + `check_plan.py`, `check_code.py`, and pre-commit/equivalent gate. | First judge upstream code-readiness; then judge implementation correctness, test quality, build/deployment verification, documentation verification, TDD evidence, scope fidelity, production quality, and quality-gate fitness. |

Agents should infer the likely scope from the user's request and state it explicitly:
broad product/platform/app requests map to Product/system, one capability/subsystem maps to
Feature/component, and bug fixes, PR-sized changes, or local behavior deltas map to
Slice/change. Ask only when the mapping is ambiguous or materially changes the artifact.

## Human-gated skill flow

When the `agent-steered-sdlc` skill is invoked generally instead of a specific slash command,
agents should run only the next appropriate SDLC stage by default. After creating or
materially revising any spec, design, ADR, plan, code slice, or review report, stop for human
review before starting the next downstream stage, even if mechanical checks pass.

The stopping response should name the artifact path, readiness/status, key open questions,
and the recommended next command. Continue automatically across multiple artifact stages
only when the user explicitly asks for an end-to-end, unattended, or "continue through all
stages" run.

The skill and creation commands are also input-gated by default. If important information is
missing before a spec, design, plan, or code slice can be created or revised responsibly,
pause and ask one focused question at a time. The user may opt into **YOLO mode** with
phrases such as "yolo", "use your judgment", "make reasonable assumptions", or "proceed
without questions". In YOLO mode, agents may continue with their best decisions, but must
record assumptions, trade-offs, and risks in the artifact or report. YOLO mode does not
bypass readiness gates, Planned Touch Sets, upstream-blocker stops, safety constraints, or
the default human-review pause after each generated artifact unless the user separately asks
for end-to-end continuation.

## Artifact matrix

| Scope | Spec carries | Design carries | Plan carries |
| --- | --- | --- | --- |
| Product/system | Mission, stakeholders, boundary, product needs, non-goals, major capabilities, representative use cases, major NFRs, build/release/deployment expectations, user/developer documentation expectations, broad acceptance intent, child-artifact needs. | HLD: context, major containers/services/modules, drivers, boundaries, data ownership, quality tactics, build/package/release strategy, deployment/operations strategy, documentation strategy, ADRs, risks, decomposition candidates. | Breakdown plan: milestones, feature/component `WORK-` items, dependencies, required child specs/designs/ADRs, research/decision needs, build/deployment tracks, documentation tracks, parallel tracks, readiness targets. |
| Feature/component | Parent refs, local goal, actors, concrete behavior, FR/NFR/AT coverage, edge cases, integration/business rules, build/deployment constraints, documentation constraints, dependencies, non-goals. | Feature/component design: responsibilities, contracts, local state/data, runtime flows, core/shell split, dependencies, UX/API contracts, build/deployment impacts, documentation impacts, decisions, risks, test matrix. | Breakdown or implementation plan: child slice/change work or PRs, child artifact needs, integration order, test allocation, build/deployment allocation, documentation allocation, touch-scope risks. |
| Slice/change | Exact requirement delta, parent IDs refined/preserved, changed and unchanged behavior, edge cases, build/deployment delta, documentation delta, executable or justified non-code acceptance criteria. | LLD: touched components/modules, API/schema/data deltas, failure paths, validation/policy logic, build/deployment script or artifact changes, documentation changes, migration/rollback, side effects, test levels/doubles, likely touch candidates. | Implementation plan: `PR-` items, Planned Touch Sets, Red/Green steps, test levels, LOC estimates, quality gates, build/deployment verification, documentation checks, rollback, dependencies, worktree guidance. |

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
`--max-diff-loc <n>`, `--diff-base <ref>`, `--allow-missing-git-evidence`,
`--allow-missing-tdd-evidence`, `--spec <file>`, `--design <file>`. Git diff-size and TDD
evidence are required by default; use the allow flags only when the repository cannot
provide that evidence and the review report will state the limitation. Exits non-zero on any
gate failure.

Checker limits: these scripts are deterministic structural gates. They catch missing
sections, malformed IDs, orphan references, missing trace links, declared oversize PRs,
missing Red/Green step text, unlabeled coverage output, missing same-test-block assertion
trace IDs, oversize git diffs against the resolved review base, and obvious skip/TODO
markers. Red/Green text, AT scenario shape, and commit-message TDD evidence are presence
checks; they do not prove semantic correctness, test quality, or true TDD history. The
qualitative review prompts must judge those concerns from the artifact content, code, tests,
and available review/git evidence.

## Installation

Canonical source prompts live in [prompts](prompts), skills live in [skills](skills),
and checker code lives in [checkers](checkers). Use the install scripts to copy/adapt
them into tool-specific locations.

The default install is **user-scoped** for tools that support user/global commands, so it
applies across projects:

Both dry and real installs print the destination folders for each selected tool before
doing any work.

Preview the install without writing files:

```pwsh
.\scripts\install.ps1 -DryRun
```

```sh
scripts/install.sh --dry-run
```

Run the install:

```pwsh
.\scripts\install.ps1
```

```sh
scripts/install.sh
```

Use project scope when a product workspace should carry its own command copies:

```pwsh
.\scripts\install.ps1 -TargetRoot D:\path\to\product -Scope project
```

```sh
scripts/install.sh --target /path/to/product --scope project
```

On Windows, `install.ps1` also installs the matching WSL targets when WSL is available.
Inside WSL, `install.sh` also installs the matching Windows targets when `powershell.exe`
is available. Use `-NoCrossInstall` or `--no-cross-install` to install only in the current
environment.

Install targets:

- Codex: `<target>/.codex/skills/agent-steered-sdlc` or
  `$CODEX_HOME/skills/agent-steered-sdlc` / `~/.codex/skills/agent-steered-sdlc`, plus
  direct prompt commands in `<target>/.codex/prompts` or `$CODEX_HOME/prompts` /
  `~/.codex/prompts`. Restart Codex, then invoke them as `/prompts:spec-create`,
  `/prompts:design-create`, etc. Codex documents custom prompts as deprecated in favor of
  skills, but this installer writes both so commands are directly accessible.
- GitHub Copilot: user scope installs VS Code user prompt files under
  `%APPDATA%\Code\User\prompts` on Windows, `~/Library/Application Support/Code/User/prompts`
  on macOS, or `${XDG_CONFIG_HOME:-~/.config}/Code/User/prompts` on Linux. It also installs
  the `agent-steered-sdlc` skill under `~/.copilot/skills/agent-steered-sdlc` and
  `~/.agents/skills/agent-steered-sdlc` for Copilot CLI/agent skill loading. Project scope
  installs prompts to `<target>/.github/prompts/*.prompt.md` and skills to
  `<target>/.github/skills/agent-steered-sdlc` plus
  `<target>/.agents/skills/agent-steered-sdlc`. Set `AGENT_SDLC_COPILOT_PROMPTS_DIR` to
  override the user prompt folder for another VS Code profile or distribution. Copilot
  prompt exports are written with `mode: agent` and no `tools:` allowlist, so they are direct
  slash prompts without restricting tool availability. After skill install, restart Copilot
  CLI or run `/skills reload`, then verify with `/skills info agent-steered-sdlc`.
- Claude Code: `<target>/.claude/commands/*.md` or `~/.claude/commands/*.md`, plus
  the `agent-steered-sdlc` skill under `<target>/.claude/skills/` or `~/.claude/skills/`.
- Gemini CLI: `<target>/.gemini/commands/*.toml` or `~/.gemini/commands/*.toml`.
- Claude and Pi: exported prompt packs under `.ai-prompts/` because they do not expose a
  stable local slash-command folder. The export also includes the `agent-steered-sdlc`
  skill bundle for manual import/adaptation.
- Checkers: copied to `<target>/checkers` unless `--no-checkers` / `-NoCheckers` is used.

If the target is this commands repository itself, the installer warns because project-local
artifacts such as `.github/prompts` and `checkers` may be written into the source checkout;
that is acceptable for dogfooding, but product installs should pass `-TargetRoot` /
`--target`.

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
