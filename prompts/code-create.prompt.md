---
description: Implement a work plan PR-by-PR with strict Red/Green/Refactor TDD, keeping every step shippable, tested, and traceable to the spec, design, and plan.
agent: agent
---

# Code Create

Your job is to turn `plan.md` (grounded in `spec.md` and `design.md`) into working,
tested, production code. Build **one PR at a time**, in plan order, using TDD. Optimize so
`/code-review` finds nothing to fix.

## Core principles (the code is judged against these)

1. **TDD always** — for each PR: write a failing test (**Red**), minimal code to pass
   (**Green**), then **Refactor** with tests green. Never write prod code without a red test.
2. **One PR at a time** — implement the lowest unbuilt PR whose deps are met; keep ≤300 LOC.
3. **Always green** — the full suite passes before a PR is done; never leave red on trunk.
4. **Traceable** — tests name the FR/AT/COMP and PR they cover; nothing built off-plan.
5. **Production quality** — error handling, input validation, no dead code, lint clean.
6. **Planned scope only** — edit only the files, directories, modules, config, docs,
   generated artifacts, and spec/design/plan sections listed in the PR's Planned Touch Set.

## Code-ready scope gate

`/code-create` only implements **code-ready slice/change work** or a small
feature/component that already has a code-ready implementation plan. Do not code directly
from a product/system spec, HLD, feature/component design, or Breakdown plan marked
Exploratory or Decomposable.

Before writing tests or code, confirm all of the following:

- `spec.md` or the focused spec declares `Implementation Readiness: Code-ready`, or the
  relevant parent spec delegates the current slice/change to a code-ready child spec.
- `design.md` or the focused LLD declares `Implementation Readiness: Code-ready`, or the
  design explicitly says no additional LLD is needed for this slice/change.
- `plan.md` declares `Plan Type: Implementation` and `Implementation Readiness: Code-ready`.
- The plan contains concrete `PR-` items, Planned Touch Sets, Test Levels, Red steps,
  Green steps, dependencies, and quality gates.

If any item is missing, **stop** and tell the user which artifact is not code-ready and what
is needed next: breakdown plan, child spec, HLD, LLD, ADR, interface contract, test
strategy, or implementation plan. This is a normal workflow outcome, not a coding failure.

## Test responsibility in this command

`/code-create` is where tests become executable code. For each PR, implement the planned
test levels before or alongside the production code using Red/Green/Refactor:

- Write executable **acceptance/e2e/API workflow tests** for the `AT-` items assigned to the
  PR. These should verify externally visible behavior or measurable NFR outcomes from the
  user's perspective or a public API boundary.
- Write **unit/pure-core tests** for deterministic logic, validation, calculations, state
  transitions, reducers, mappers, policies, and edge cases.
- Write **component/module tests** for components behind stable local boundaries.
- Write **contract tests** for APIs, events, schemas, DTOs, protocols, compatibility, and
  error behavior.
- Write **integration tests** for persistence, messaging, external-service adapters,
  framework wiring, migrations, transactions, auth, caching, retries, and configuration.
- Write **UI/accessibility/visual tests** for routes, screens, widgets/components, keyboard
  and focus behavior, semantics, contrast, responsive behavior, and visual regressions when
  planned.
- Write **quality-attribute checks** for performance, reliability, security, privacy,
  resilience, observability, offline/sync, rollout/rollback, and operational behavior when
  planned.

Follow the plan's test mix. If the planned tests are insufficient to prove the linked
`FR-`/`AT-`/`COMP-`/`NFR-`, stop and request a plan/design/spec update rather than silently
changing the test strategy.

## Quality gates and pre-commit

Before implementing the first PR, inspect the repository language/tooling and existing CI.
Use existing project commands when they are present. If pre-commit or equivalent local
quality gates are missing, configure them as part of the first implementation PR so every
later PR uses the same checks.

Prefer a `.pre-commit-config.yaml` when the repo can support it. If the ecosystem already
uses an equivalent hook runner, such as Husky/lint-staged for JS/TS, Lefthook, Overcommit,
cargo hooks, Gradle tasks, or committed CI-only scripts, either integrate with that
convention or document why `.pre-commit-config.yaml` is not the right fit. The local gate
must be runnable by one command and should be mirrored in CI where possible.

Select tools by ecosystem, using the repo's established stack where available:

- **Python**: `ruff format`, `ruff check`, `ty`, `pyright` or `mypy`, `pytest`, `coverage`,
  `bandit`, `pip-audit`, `radon` or `xenon`, `interrogate` for doc coverage when useful.
- **JavaScript/TypeScript**: `prettier`, `eslint`, `tsc --noEmit`, `stylelint`, `vitest` or
  `jest` coverage, `playwright`, `npm audit`/`pnpm audit`, `knip`, `madge`, ESLint complexity rules.
- **Go**: `gofmt`, `go vet`, `staticcheck`, `golangci-lint`, `govulncheck`, `go test -cover`.
- **Rust**: `cargo fmt`, `cargo clippy -D warnings`, `cargo test`, `cargo llvm-cov` or
  `tarpaulin`, `cargo audit`.
- **Java/Kotlin**: Checkstyle, Spotless, PMD, SpotBugs, Error Prone, `detekt`, `ktlint`,
  Gradle/Maven test tasks, JaCoCo coverage.
- **.NET/C#**: `dotnet format`, Roslyn analyzers, StyleCop analyzers, `dotnet test`,
  Coverlet coverage.
- **Ruby**: `rubocop`, `brakeman`, `bundler-audit`, `rspec`/`minitest`, SimpleCov.
- **PHP**: PHP-CS-Fixer or PHPCS, PHPStan or Psalm, PHPUnit coverage, Infection where useful.
- **Swift/iOS**: SwiftFormat, SwiftLint, `xcodebuild test`, Xcode coverage.
- **Dart/Flutter**: `dart format`, `dart analyze`, `flutter test --coverage`.
- **Shell/SQL/IaC/config/docs**: `shellcheck`, `shfmt`, `sqlfluff`, `hadolint`, `yamllint`,
  `actionlint`, `markdownlint`, `prettier`, `tflint`, `terraform fmt/validate`, `checkov`.
- **Cross-language complexity/duplication/security**: `lizard`, Sonar-compatible reports,
  CodeQL where configured, dependency audit tools, secret scanning such as `gitleaks`.

Set explicit thresholds in the plan, pre-commit config, tool config, or test command. If the
repo lacks thresholds, use these defaults unless the user chooses different standards:

- Formatter, linter, type checker, dependency audit, and secret scan: zero errors.
- Unit/integration tests: pass with no skips or xfails unless each is explicitly justified.
- Coverage: use the plan's `--cov-min`; if absent, require at least 80% line coverage overall,
  70% branch coverage where available, and 90% line coverage for pure functional core modules.
- Complexity: cyclomatic complexity ≤10 per function/method and cognitive complexity ≤15
  where the tool supports it; document any exception with a reason and test coverage.
- Module size: stay within the checker's `--max-loc` or a stricter repo standard.
- Security/dependency scans: no critical/high findings; medium findings need documented
  acceptance, mitigation, or follow-up.

## Step 1 — Confirm context

Read `plan.md`, `design.md`, `spec.md`. Apply the Code-ready scope gate above. Then identify
the next PR (lowest number, deps merged, not yet built). State the PR, its Red tests, Green
scope, Planned Touch Set, the COMP/FR/AT it covers, the planned test levels, and the
quality-gate command(s) that must pass at the PR boundary.

Before editing, compare every intended file/section change against the PR's Planned Touch
Set. If the plan does not include a Planned Touch Set, or if the implementation requires
touching files/sections outside it, **stop before making the out-of-scope edit**. Tell the
user exactly what extra files/sections are needed, why the current plan is insufficient, and
whether the fix should be a plan revision, design revision, spec revision, or separate PR.
Do not expand scope silently.

If quality gates are not configured yet, make configuring/updating pre-commit hooks part of
the first relevant PR. Add only checks that can run reliably for the repo's stack; keep slow
or environment-heavy checks in CI if pre-commit would make local commits impractical, but
document the split.

If quality-gate configuration is not in the Planned Touch Set, stop and ask for a plan update
unless the current PR explicitly exists to configure quality gates.

## Step 2 — Red

Write the failing tests first. Run them; show they fail for the right reason. Test names
must be plain, readable behaviour (e.g. `test_win_detected_on_full_row`). Put the covered
IDs in a docstring or comment — never in the function name. One concise `Covers:` line is
enough (e.g. `"""Covers FR-GAME-30, AT-GAME-30 (PR-CORE-10)."""`).

When a PR includes multiple test levels, write the smallest useful Red test first for the
logic or contract being introduced, then add the planned acceptance/e2e/API workflow test
for the assigned `AT-`. Keep slow acceptance/e2e coverage focused; do not duplicate every
unit edge case at the top level.

## Step 3 — Green

Write the minimum code to pass. Run the suite; show all green. No extra scope.

## Step 4 — Refactor

Improve names/structure with tests staying green. Run formatters, linters, type checks,
complexity checks, security/dependency scans, coverage, and the suite again through the
configured local quality gate where possible.

## Step 5 — Verify the PR

First run `python checkers/check_code.py --plan plan.md --tests-argv '<json-array>' --cov-min <n> --json`.
If `python` is unavailable or fails because the launcher is missing, retry the same command
with `python3`; if that is unavailable, retry with `uv run python`.
Use `--tests-argv` (for example `["pytest","-q","--cov=src"]`) for safe command execution.
Use `--tests "<cmd>"` only for simple commands that split cleanly; use `--tests-shell` only
when the project genuinely requires shell syntax such as pipes or compound commands, and
document the trust boundary. Use the coverage threshold from `plan.md`/the done-definition.
Omit `--diff-base` when the checker can resolve a merge-base against the default branch;
provide `--diff-base <base>` when the review target is known and automatic resolution is not
right. Git diff-size and TDD evidence are required by default. Use
`--allow-missing-git-evidence` or `--allow-missing-tdd-evidence` only when the repository
cannot provide that evidence, and report the limitation explicitly. Fix until gates pass or
report which evidence is unavailable.

Then run the configured pre-commit/local quality gate, normally:

```pwsh
pre-commit run --all-files
```

If the project uses an equivalent command, run that command instead and name it in the
handoff. Fix formatter, lint, type, complexity, dependency/security, coverage, and test
failures until the local gate passes. Do not bypass hooks to finish a PR.

Then run or perform the corresponding `/code-review` for the completed PR boundary. When
sub-agents are available, use fresh-context Mechanical Reviewer and Qualitative Reviewer
sub-agents as described in `/code-review`; otherwise state that review is not independent and
use the adversarial posture. Treat any upstream spec/design/plan blocker, failing
qualitative finding, TDD authenticity issue, design-fidelity issue, missing edge case, NFR
validation gap, traceability issue, or production-quality concern as a defect. Revise
upstream artifacts if the review says they must change; otherwise revise tests/code. Repeat
checker + review until `/code-review` would return Pass or an explicitly accepted
Pass-with-fixes for that boundary.

Then move to the next PR. Stop when every plan PR is built, green, checker-clean, and
review-clean.

## Quality rules

- Every PR maps 1:1 to a plan `PR-`; tests cover its FR/AT/COMP. ≤300 LOC per PR.
- Each PR implements the test levels assigned in the plan, including executable acceptance
  coverage for assigned `AT-` items and lower-level tests for the affected core, component,
  contract, integration, UI, quality, migration, or operational behavior.
- Every edit stays within the PR's Planned Touch Set. Out-of-scope needs stop work and trigger
  a user-visible plan/spec/design update request.
- No prod line lands without a prior failing test. Suite is green at each PR boundary.
- Pre-commit or an equivalent local quality gate is configured, documented, and green.
- Formatter, lint, type, complexity, dependency/security, coverage, and test thresholds are
  explicit and met, with documented exceptions only when the user accepts them.
- Test names stay readable; IDs live in docstrings/comments, not in function names.
- No vague TODOs, no skipped tests, no commented-out code.
