# Agent-Steered SDLC

Agent-Steered SDLC is a set of reusable prompts, skills, and structural checkers for
spec-first software delivery with AI coding agents. It helps developers move from a product
request to requirements, design, planning, implementation, tests, and review without losing
traceability or skipping human review.

The workflow is intentionally artifact-driven:

```text
request -> spec -> design -> plan -> code/tests/docs/build/deploy -> review
```

Each stage can be created and reviewed independently. By default, the skill pauses for human
input when important information is missing and pauses again after generating an artifact.

## What You Get

- Slash-command prompts for specs, designs, plans, code, and reviews.
- A native `agent-steered-sdlc` skill for agents that support skills.
- Structural checkers for specs, designs, plans, and code/test traceability.
- Installers for Windows, macOS, Linux, and WSL.
- User-scoped installs by default, with project-scoped installs when needed.

## Install

Run from the cloned repository root.

Preview the install without writing files:

```powershell
.\scripts\install.ps1 -DryRun
```

```sh
scripts/install.sh --dry-run
```

Install for the current user:

```powershell
.\scripts\install.ps1
```

```sh
scripts/install.sh
```

Install into a specific project workspace instead:

```powershell
.\scripts\install.ps1 -TargetRoot D:\path\to\product -Scope project
```

```sh
scripts/install.sh --target /path/to/product --scope project
```

Install only selected tools:

```powershell
.\scripts\install.ps1 -Tool codex,claude-code
```

```sh
scripts/install.sh --tools codex,claude-code
```

By default, Windows installs also refresh WSL targets when WSL is available, and WSL installs
also refresh Windows targets when `powershell.exe` is available. Use `-NoCrossInstall` or
`--no-cross-install` to stay in the current environment.

## Supported Targets

- **Codex**: installs the `agent-steered-sdlc` skill and direct prompt commands under
  `~/.codex/prompts`. Invoke direct prompts as `/prompts:spec-create`,
  `/prompts:design-create`, etc. after restarting Codex.
- **GitHub Copilot**: installs prompt files for VS Code Copilot Chat and first-class agent
  skills for Copilot CLI/agent surfaces. User scope installs prompts under the VS Code user
  prompt folder and skills under `~/.copilot/skills/agent-steered-sdlc` plus
  `~/.agents/skills/agent-steered-sdlc`. Project scope installs prompts to
  `<project>/.github/prompts` and skills to `<project>/.github/skills/agent-steered-sdlc`
  plus `<project>/.agents/skills/agent-steered-sdlc`.
- **Claude Code**: installs slash commands and the skill.
- **Gemini CLI**: installs command TOML files.
- **Claude and Pi**: exports prompt packs under `.ai-prompts/` for manual import or use.
- **Checkers**: installs `checkers/` into the target workspace unless skipped with
  `-NoCheckers` or `--no-checkers`.

Every dry or real install prints the destination folders before doing work.

## Commands

The prompt set has eight core commands:

| Command | Purpose |
| --- | --- |
| `/spec-create` | Create or revise a Software Requirements Specification. |
| `/spec-review` | Review a spec with structural checks plus qualitative assessment. |
| `/design-create` | Create or revise a Software Design Document and ADRs as needed. |
| `/design-review` | Review design quality and upstream spec fitness. |
| `/plan-create` | Create a breakdown or implementation plan with PR slices and touch sets. |
| `/plan-review` | Review plan readiness, slicing, test/docs/build/deploy allocation, and sequencing. |
| `/code-create` | Implement a code-ready plan using Red/Green/Refactor TDD, including planned docs/build/deploy work. |
| `/code-review` | Review code, tests, docs, build/deploy work, traceability, quality gates, and upstream consistency. |

Exact invocation syntax depends on the host tool. For Codex direct prompts, use
`/prompts:<name>`. For Claude Code and Gemini, use their native command mechanisms.

## Workflow Model

Work is classified at three levels:

- **Product/system**: broad product or platform scope. Usually decomposable, not directly
  code-ready.
- **Feature/component**: one user-facing capability, subsystem, component, integration, or
  screen family.
- **Slice/change**: the smallest implementable unit, usually PR-sized.

Artifacts declare one readiness value:

- **Exploratory**: still being shaped.
- **Decomposable**: valid parent artifact, but needs child work before implementation.
- **Code-ready**: precise enough for implementation.

`/code-create` should only run from a code-ready implementation plan.

## Builds And Deployment

Builds and deployment are covered from the beginning:

- Specs capture externally relevant build, release, deployment, rollout, rollback,
  migration, smoke-check, and operational acceptance needs.
- Designs define deployable artifacts, build/package strategy, release workflow,
  environments, configuration/secrets, promotion, deployment topology, validation, and
  ownership.
- Plans assign build scripts, package manifests, generated outputs, CI/CD config, IaC or
  deployment manifests, migration scripts, smoke checks, rollback checks, and release docs
  to child work or PRs.
- Code creates and verifies the planned build/deployment pieces. It should run the build,
  verify the expected artifact, validate deployment scripts/manifests with dry-run or lint
  checks where possible, and avoid live production deployment unless explicitly requested.

Reviews stop with an upstream blocker when build or deployment intent is missing from the
artifact that should own it.

## User And Developer Documentation

Documentation is also covered from the beginning:

- Specs capture user and developer documentation audiences, tasks, onboarding, help,
  API/reference, examples, runbooks, troubleshooting, release notes, accessibility, and
  acceptance needs.
- Designs define the documentation architecture: source locations, generated vs. written
  docs, API/reference generation, examples, diagrams, publishing/versioning, ownership, and
  validation checks.
- Plans assign documentation work to PRs, including user guides, README/API docs, examples,
  runbooks, troubleshooting, migration notes, release notes, generated docs, and link/doc
  checks.
- Code updates and verifies the planned docs with the implementation. Public docs should
  match actual behavior and contracts, not describe unimplemented future behavior.

Reviews stop with an upstream blocker when documentation intent is missing from the artifact
that should own it.

## Human Gates And YOLO Mode

Default behavior is human-gated:

- If important input is missing, the agent asks one focused question at a time.
- After an artifact is generated or materially revised, the agent stops for human review.
- Downstream reviews stop when they discover upstream spec, design, or plan issues.

You can opt into **YOLO mode** with phrases like:

```text
yolo
use your judgment
make reasonable assumptions
proceed without questions
```

YOLO mode lets the agent make reasonable assumptions and continue, but it must record those
assumptions, risks, and trade-offs. YOLO does not bypass readiness gates, planned touch sets,
quality gates, safety constraints, or the default review pause unless you explicitly ask for
end-to-end unattended continuation.

## Tests And Verification

Test responsibility is split by artifact:

- Specs define `AT-` acceptance criteria.
- Designs define the test architecture and lower-level test mix.
- Plans assign executable tests to PRs.
- Code writes the executable tests and implementation.
- Documentation, build, and deployment checks are assigned through the same spec/design/plan
  chain and verified during code creation/review when planned.

The checkers provide deterministic structural evidence:

```powershell
python checkers/check_spec.py spec.md --json
python checkers/check_design.py design.md --json
python checkers/check_plan.py plan.md --spec spec.md --design design.md --json
python checkers/check_code.py --plan plan.md --tests-argv '["pytest","-q"]' --cov-min 80 --json
```

If `python` is unavailable, try `python3`, then `uv run python`.

The checkers do not prove semantic correctness. Reviews must pair checker output with a
qualitative assessment of requirements, design, plan quality, test quality, implementation
fitness, documentation/build/deployment completeness, and upstream/downstream consistency.

## Repository Layout

```text
docs/      user-facing documentation and review notes
prompts/   source slash-command prompt definitions
skills/    native skill bundles
checkers/  structural verification scripts
scripts/   installers for Windows, macOS, Linux, and WSL
tests/     checker tests
```

Do not treat `.github/prompts` as source in this repository. It is only an install target
for GitHub Copilot project-scoped prompts.

## More Detail

- Overview page: [docs/agent-steered-sdlc.html](docs/agent-steered-sdlc.html)
- Review checklist: [docs/review-verification-checklist.md](docs/review-verification-checklist.md)
- Agent-facing repository guidance: [AGENTS.md](AGENTS.md)
