---
description: Implement a work plan PR-by-PR with strict Red/Green/Refactor TDD, keeping every step shippable, tested, documented, and traceable to the spec, design, and plan.
agent: agent
---

# Code Create

Your job is to turn `plan.md` (grounded in `spec.md` and `design.md`) into working,
tested, documented, production code. Build **one PR at a time**, in plan order, using TDD.
Optimize so `/code-assess` finds nothing to fix.

## Core principles (the code is judged against these)

1. **TDD always** — for each PR: write a failing test (**Red**), minimal code to pass
   (**Green**), then **Refactor** with tests green. Never write prod code without a red test.
2. **One PR at a time** — implement the lowest unbuilt PR whose deps are met; keep ≤300 LOC.
3. **Always green** — the full suite passes before a PR is done; never leave red on trunk.
4. **Traceable** — tests name the FR/AT/COMP/TEST and PR they cover; nothing built off-plan.
5. **Production quality** — error handling, input validation, useful structured logging/
   telemetry where planned, reproducible build artifacts, deployable configuration/scripts
   when planned, accurate user/developer documentation when planned, no dead code, lint clean.
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
  Green steps, dependencies, quality gates, logging/error-handling work or an explicit
  rationale that no logging/error-handling change is required, build/deployment work or an
  explicit rationale that no build/deployment change is required, plus documentation work or
  an explicit rationale that no documentation change is required.

If any item is missing, **stop** and tell the user which artifact is not code-ready and what
is needed next: breakdown plan, child spec, HLD, LLD, ADR, interface contract, test
strategy, or implementation plan. This is a normal workflow outcome, not a coding failure.

## Clarification and YOLO mode

Default behavior is input-gated: pause and ask one focused question at a time when missing
information would materially change implementation behavior, test intent, logging/telemetry
signals, error-handling behavior, quality gates, build artifact shape, deployment scripts/
manifests, data migration, rollout/rollback, documentation content, security/privacy
posture, or planned touch scope. Do not silently invent behavior outside the spec/design/plan.

The user may opt into **YOLO mode** with phrases such as "yolo", "use your judgment", "make
reasonable assumptions", or "proceed without questions". In YOLO mode, make the narrowest
reasonable local implementation decisions yourself, continue without blocking on normal
clarification questions, and record assumptions in the code comments, tests, plan notes, or
final implementation report as appropriate. YOLO mode does not bypass the Code-ready scope
gate, Planned Touch Sets, upstream-blocker stops, TDD discipline, quality gates, safety
constraints, or a required spec/design/plan update.

## Test responsibility in this command

`/code-create` is where tests become executable code. For each PR, implement the planned
test levels before or alongside the production code using Red/Green/Refactor:

- Write executable **acceptance/e2e/API workflow tests** for the `AT-` items assigned to the
  PR. These should verify externally visible behavior or measurable NFR outcomes from the
  user's perspective or a public API boundary, and cite the relevant `TEST-` obligation when
  the design/plan named one.
- Write **unit/pure-core tests** for deterministic logic, validation, calculations, state
  transitions, reducers, mappers, policies, and edge cases.
- Write **component/module tests** for components behind stable local boundaries.
- Write **contract tests** for APIs, events, schemas, DTOs, protocols, compatibility, and
  error behavior. Use the design/plan's shared fixtures, schemas, generated clients,
  captured representative examples, or contract-test harness; do not invent mock payload
  shapes for convenience.
- Write **integration tests** for persistence, messaging, external-service adapters,
  framework wiring, migrations, transactions, auth, caching, retries, and configuration.
- Write **UI/accessibility/visual tests** for routes, screens, widgets/components, keyboard
  and focus behavior, semantics, contrast, responsive behavior, and visual regressions when
  planned. Prefer role, label, text, and semantic selectors; avoid coupling behavior tests
  to CSS class names unless the style contract itself is under test.
- Write **quality-attribute checks** for performance, reliability, security, privacy,
  resilience, observability, logging/telemetry, error handling, offline/sync,
  rollout/rollback, and operational behavior when planned.
- Write or run **build/deployment checks** when planned: reproducible package/image/static
  bundle/mobile build output, generated artifact validation, migration validation,
  deployment dry-run/plan/lint, manifest/IaC validation, smoke checks, and rollback checks.
- Write or run **documentation checks** when planned: user/developer docs, README/API docs,
  generated reference docs, examples, tutorials, diagrams, runbooks, troubleshooting,
  release/migration notes, doc build, link checks, accessibility/readability, and freshness
  or version checks.

Follow the plan's test mix. Treat each assigned `TEST-` as an executable obligation, not a
suggestion. If the planned tests are insufficient to prove the linked
`FR-`/`AT-`/`TEST-`/`COMP-`/`NFR-`, stop and request a plan/design/spec update rather than
silently changing the test strategy.

Also add **implementation-local supplemental inner tests** when Red/Green/Refactor exposes
useful behavior that was too small or code-shaped to name in the design/plan. Examples
include helper or pure-core edge cases, table/property cases, parser/mapper/reducer cases,
regression tests for a discovered bug, characterization tests around legacy boundaries, local
adapter/error-normalization tests, and boundary fixture variations. These tests supplement,
never replace, planned `AT-`/`TEST-` coverage. They must stay within the current `PR-` and
Planned Touch Set, cite the nearest `PR-` plus relevant `FR-`/`AT-`/`TEST-`/`COMP-` when
applicable, and state a concrete oracle. If a supplemental test implies new externally
visible behavior, a changed API/event/schema/error contract, a UX/NFR expectation, or
broader scope, stop and request the appropriate spec/design/plan update before coding it.

Treat test implementation as production-quality code. Keep assertions meaningful and
behavior-focused; make fixtures realistic and maintainable; keep helpers readable; avoid
over-mocking, sleeps, hidden network/time dependencies, order dependence, brittle selectors,
and tautological assertions. Prefer the narrowest test level that proves the behavior, then
add broader acceptance/e2e coverage only where planned.

Implement the planned verification oracle for every test. Each executable test must assert
at least one concrete observable that proves pass/fail: return value, state transition,
persisted record, emitted event, API response, DOM/role/text output, accessibility tree,
screenshot or visual baseline, generated file/artifact, structured log entry, metric, trace,
deployment status, or captured external call. Use logs, screenshots, and metrics deliberately
when they are the behavior under test or the strongest practical signal; otherwise prefer
direct state/output assertions. Do not accept a test whose only oracle is "no exception" or
"the mock was called" unless that is the specified externally meaningful behavior.

For boundary-facing tests, compare mocks/fixtures against the real producer/consumer
contract before writing the Red test. If the plan does not name a fixture/schema/generated
client/contract-test source and the boundary shape matters, stop for a plan/design update.
For UI-facing work, keep presentation changes decoupled from behavior tests; add visual,
accessibility, responsive, or role/text-based assertions only where planned.

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
- **Build/deployment validation**: repo-native build commands, Docker/BuildKit image builds
  or `docker compose config`, Kubernetes `kubectl --dry-run=server/client` or `kubeconform`,
  Helm lint/template, Terraform/OpenTofu plan/validate, Bicep/ARM validation, CloudFormation
  validate, serverless/SAM/CDK synth, package publish dry runs, mobile archive/export
  validation, and environment smoke-test commands where available.

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
- Build/deployment: planned build command succeeds, expected artifact path/name/version is
  produced or validated, deployment manifests/scripts pass lint/dry-run/plan checks, and
  no real production deployment is performed unless explicitly requested by the user.
- Documentation: planned doc build/generation/link/readability/accessibility checks pass;
  examples or snippets are runnable where practical; public API/reference docs match the
  implemented contract; no user/developer-facing behavior change ships undocumented unless
  the plan explicitly says docs are out of scope.

## Step 1 — Confirm context

Read `plan.md`, `design.md`, `spec.md`. Apply the Code-ready scope gate above. Then identify
the next PR (lowest number, deps merged, not yet built). State the PR, its Red tests, Green
scope, Planned Touch Set, the COMP/FR/AT/TEST it covers, the planned test levels, the
verification oracle for each planned test, any likely supplemental inner-test discovery
areas, and the quality-gate command(s) that must pass at the PR boundary. Also state any
planned logging/telemetry work: structured fields, events, metrics, traces, correlation/
support IDs, redaction, alert hooks, or `None` with the plan's rationale. State planned
error-handling work: UI/API/domain/integration/infrastructure mapping, retry/fallback/
degraded behavior, safe messages, or `None` with the plan's rationale. Also state any
planned build/deployment work: build command, expected artifact, deployment validation
command, smoke check, rollback check, or `None` with the plan's rationale. Also state
planned documentation work: user docs, developer docs, API/reference docs, examples,
runbooks, release/migration notes, doc validation command, or `None` with the plan's rationale.

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

If build/deployment files, generated artifacts, scripts, pipeline config, IaC, manifests,
or release documentation are required but absent from the Planned Touch Set, stop and ask
for a plan/design update before editing them.

If logging/telemetry config, logging adapters, event/metric/trace schemas, alert hooks,
correlation propagation, redaction logic, or error-handling modules are required but absent
from the Planned Touch Set, stop and ask for a plan/design/spec update before editing them.

If user/developer docs, README/API docs, examples, generated reference docs, runbooks,
troubleshooting, migration notes, or release notes are required but absent from the Planned
Touch Set, stop and ask for a plan/design/spec update before editing them.

## Step 2 — Red

Write the failing tests first. Run them; show they fail for the right reason. Test names
must be plain, readable behaviour (e.g. `test_win_detected_on_full_row`). Put the covered
IDs in a docstring or comment — never in the function name. One concise `Covers:` line is
enough (e.g. `"""Covers FR-GAME-WINROW, AT-GAME-WINROW, TEST-GAME-WINROW (PR-CORE-WINROW)."""`).
For supplemental inner tests without a direct `AT-`/`TEST-`, cite the owning `PR-` and
nearest `COMP-`/`FR-` and state why the test is supplemental.
Include a concise `Verifies:` note when it improves readability, naming the oracle being
asserted, such as returned value, persisted row, emitted event, DOM text, screenshot
baseline, structured log, metric, artifact, deployment dry-run result, or external call.

When a PR includes multiple test levels, write the smallest useful Red test first for the
logic or contract being introduced, then add the planned acceptance/e2e/API workflow test
for the assigned `AT-`. Keep slow acceptance/e2e coverage focused; do not duplicate every
unit edge case at the top level.

When testing boundary errors, include representative multi-field or multi-cause payloads
where the contract allows them, and assert the user/API-facing normalized result rather than
raw object stringification or framework internals.

When testing logging or telemetry, assert the stable structured signal: event name, level,
correlation/support ID, metric name/value/tags, trace span attributes, audit field, redaction
behavior, or absence of sensitive data. Do not assert volatile timestamps, stack traces, or
formatting details unless the format is the contract.

## Step 3 — Green

Write the minimum code to pass. Run the suite; show all green. No extra scope.

When the PR owns build/deployment work, implement only the planned build scripts,
package/config changes, deployment manifests, migration scripts, smoke checks, or rollback
hooks needed for the PR. Do not perform a live deployment unless the plan and the user
explicitly call for it; prefer dry-run, validate, synth, plan, lint, or local/staging smoke
commands.

When the PR owns documentation work, update only the planned user/developer docs, examples,
generated reference docs, runbooks, troubleshooting, release/migration notes, or help text.
Keep docs aligned with actual behavior and contracts; do not document unimplemented future
behavior as if it exists.

When the PR owns logging/telemetry or error-handling work, implement only the planned
structured signals, correlation/support IDs, redaction, alert hooks, error mapping,
retry/fallback/degraded behavior, and safe UI/API messages. Do not log secrets, raw tokens,
PII beyond the approved contract, stack traces to user-visible surfaces, raw framework
objects, or unstable internals meant only for local debugging.

## Step 4 — Refactor

Improve names/structure with tests staying green. Run formatters, linters, type checks,
complexity checks, security/dependency scans, coverage, and the suite again through the
configured local quality gate where possible. Re-run planned build/package and
deployment-validation commands after refactoring when touched files can affect them. Re-run
planned documentation build/generation/link/readability checks when touched files can affect
them. Re-run planned logging/telemetry/error-handling tests when touched files can affect
diagnostic signal shape, redaction, error mapping, retries, fallback, or user/API messages.

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

Then run the planned build/package command and verify the expected deployable artifact is
created or validated. If the PR touches deployment scripts, CI/CD, manifests, IaC,
migrations, environment config, or release docs, run the planned validation/dry-run/plan,
smoke, and rollback checks. Record any check that cannot run locally and why.

Then run the planned documentation checks. If the PR touches user/developer docs, API
contracts, examples, generated reference docs, runbooks, troubleshooting, release notes, or
migration notes, run the planned doc build/generation/link/readability/accessibility checks
and verify examples/snippets where practical. Record any check that cannot run locally and why.

Then run the planned logging/telemetry and error-handling checks. If the PR touches
diagnostic signal shape, redaction, correlation/support IDs, event/metric/trace schemas,
alert hooks, or error mapping/retry/fallback/degraded behavior, run the planned tests or
checks and record any that cannot run locally and why.

Then run or perform the corresponding `/code-assess` for the completed PR boundary. When
sub-agents are available, use fresh-context Mechanical Verifier and Qualitative Reviewer
sub-agents as described in `/code-assess`; otherwise state that review is not independent and
use the adversarial posture. Treat any upstream spec/design/plan blocker, failing
qualitative finding, TDD authenticity issue, design-fidelity issue, missing edge case, NFR
validation gap, traceability issue, or production-quality concern as a defect. Revise
upstream artifacts if the review says they must change; otherwise revise tests/code. Repeat
checker + assessment until `/code-assess` would return Pass or an explicitly accepted
Pass-with-fixes for that boundary.

## Step 6 — Human review gate (hard stop)

After completing one PR/code slice and its checker/assessment loop, **stop**. Do not move to the
next PR, perform release/deployment work, or continue downstream in the same turn unless the
user's latest message explicitly requested unattended continuation across PRs.

End with a human-review handoff that includes:

- Completed PR/code slice ID and touched files.
- Test, checker, pre-commit/local gate, build/deploy, and documentation results.
- Any assumptions, limitations, skipped checks, or follow-up risks.
- Recommended next command or next PR ID only after the user approves this slice.

If the user explicitly requested unattended implementation across all PRs, continue in plan
order and still produce a clear boundary report after each PR. Otherwise, stop after the
first completed PR boundary.

## Quality rules

- Every PR maps 1:1 to a plan `PR-`; tests cover its FR/AT/COMP/TEST. ≤300 LOC per PR.
- Each PR implements the test levels assigned in the plan, including executable acceptance
  coverage for assigned `AT-` items and executable `TEST-` obligations for the affected
  core, component, contract, integration, UI, quality, migration, or operational behavior.
- Supplemental inner tests discovered during implementation are allowed when they stay
  within the current `PR-` and Planned Touch Set, cite the nearest trace IDs, use concrete
  oracles, and do not introduce new externally visible behavior or scope without upstream
  artifact updates.
- Test code is reviewable: meaningful assertions, realistic fixtures, clear helpers,
  deterministic setup, no tautologies, no accidental network/time/order dependence, and no
  brittle selectors except where style itself is under test.
- Every test implements a concrete verification oracle aligned with the design/plan; weak
  tests that only prove execution, mock invocation, or absence of exceptions are rejected
  unless that is the explicitly planned behavior.
- Boundary-facing tests use the planned fixture/schema/generated-client/contract source of
  truth and do not drift into bespoke mock shapes.
- UI-facing implementation includes the planned presentation/layout/responsive/accessibility
  and readable state work without making behavior tests brittle.
- Each PR implements the logging/telemetry and error-handling work assigned in the plan,
  verifies stable structured signals and failure behavior, and avoids leaking secrets,
  stack traces, raw objects, or unstable internals to users, logs, telemetry, or agents.
- Each PR implements the build/deployment work assigned in the plan, verifies the expected
  artifact or deployment validation outcome, and avoids live deployment unless explicitly
  requested.
- Each PR implements the user/developer documentation work assigned in the plan, verifies doc
  build/generation/link/readability checks where practical, and keeps public docs aligned
  with implemented behavior and contracts.
- Every edit stays within the PR's Planned Touch Set. Out-of-scope needs stop work and trigger
  a user-visible plan/spec/design update request.
- No prod line lands without a prior failing test. Suite is green at each PR boundary.
- Pre-commit or an equivalent local quality gate is configured, documented, and green.
- Formatter, lint, type, complexity, dependency/security, coverage, and test thresholds are
  explicit and met, with documented exceptions only when the user accepts them.
- Test names stay readable; IDs live in docstrings/comments, not in function names.
- No vague TODOs, no skipped tests, no commented-out code.
