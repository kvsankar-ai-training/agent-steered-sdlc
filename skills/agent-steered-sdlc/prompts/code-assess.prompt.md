---
description: Assess implemented code/logging/error-handling/docs/build/deploy work against its plan with upstream checks, structural code gates, pre-commit/local quality gates, and a qualitative pass.
agent: agent
---

# Code Assess

Assess the implementation against `plan.md`, `design.md`, and `spec.md`. The code was built
TDD, one PR at a time. Produce the verification sequence below. Do not edit code unless
asked; report findings only.

Do not stop after checker JSON. This assessment must include:

1. Verification 0: upstream spec/design/plan structural evidence plus qualitative
   code-readiness and upstream-fitness assessment.
2. Verification A: structural `check_code.py` evidence.
3. Verification A2: pre-commit or equivalent quality-gate evidence.
4. Verification B: qualitative implementation, test implementation, TDD, scope,
   production-quality, and quality-gate fitness assessment.

When the platform supports sub-agents, run these as two fresh-context passes:

- **Mechanical Verifier sub-agent**: run upstream checkers, `check_code.py`, and
  pre-commit/equivalent gates; return raw evidence, metrics, IDs, git evidence, and command
  failures.
- **Qualitative Reviewer sub-agent**: read the code, upstream artifacts, and mechanical
  evidence, then judge upstream fitness, implementation quality, test implementation
  quality, logging/telemetry and error-handling fitness, TDD evidence, scope fidelity, and
  quality-gate fitness adversarially.

If sub-agents are unavailable, state that limitation and keep the mechanical and qualitative
sections separate.

Use an adversarial assessment posture: try to refute correctness, test implementation
quality, TDD claims, planned-scope fidelity, and upstream artifact fitness. Prefer a fresh
context, separate reviewer, or different model/tool when available. If the same agent that
implemented the code is assessing it, state that the review half of the assessment is not
independent.

## Verification 0 — Upstream Consistency Gate

Before assessing the code itself, check whether the upstream spec, design, and plan are fit
to implement from. If the files exist, run:

```pwsh
python checkers/check_spec.py spec.md --json
python checkers/check_design.py design.md --spec spec.md --json
python checkers/check_plan.py plan.md --spec spec.md --design design.md --json
```

If `python` is unavailable or fails because the launcher is missing, retry checker commands
with `python3`; if that is unavailable, retry with `uv run python`.

Then read enough of the upstream artifacts to detect latent issues exposed by the code,
including ambiguous requirements, missing acceptance criteria, untestable design choices,
incorrect component boundaries, plan slices that cannot be built independently, missing NFR
validation, missing logging/telemetry/error-handling intent, missing build/release/
deployment intent, missing/incorrect Planned Touch Sets, missing user/developer
documentation intent, missing approved mock UI for required UI-facing work, traceability
gaps, or implementation behavior that suggests the upstream artifact specified the wrong thing.

Also verify the upstream artifacts were code-ready for this implementation. If `spec.md`,
`design.md`, or `plan.md` declares Exploratory or Decomposable readiness, or if `plan.md`
is a Breakdown plan rather than an Implementation plan, the code can only be assessed if a
focused child spec/design/implementation plan for the implemented slice is also present and
code-ready.

If any upstream checker fails, or if code assessment reveals that the spec/design/plan must
change before the code can be judged fairly, **stop the code assessment**. Report an
**Upstream blocker** with the exact upstream IDs/sections affected, why the code cannot be
reliably assessed, and the recommended upstream revision. Do not continue to Verification A
or B for the code until the upstream issue is resolved.

## Verification A — Mechanical / Deterministic (run the tool)

Run the checker and report its output verbatim. This is a deterministic **structural**
check: it runs the supplied test command, parses labeled coverage output, checks ID
traceability text in tests, and checks per-module size/TODO/skip markers. It does not prove
test assertions are meaningful, prove real TDD order, or measure PR diff size; Verification B
must judge those from the code, tests, and available git/review evidence.

```pwsh
python checkers/check_code.py --plan plan.md --tests-argv '<json-array>' --cov-min <n> --json
```

If all Python runners fail (`python`, `python3`, and `uv run python`), report the runner
failures and fall back to manual checks where possible.

Always provide `--tests-argv` when possible. Use `--tests` only for simple split-safe
commands, and use `--tests-shell` only for trusted commands that genuinely need shell
features. The gate fails if no test command runs or if no coverage percentage is found in
labeled coverage output. By default, the checker tries to resolve a review base using the
merge-base with the remote/local default branch. Provide `--diff-base <base>` when the
review target is known and automatic resolution is not right. If no review base can be
resolved, actual PR size is reported as unverified and the gate fails; use
`--allow-missing-git-evidence` only for non-git or intentionally evidence-poor reviews and
state that limitation. TDD evidence from git log is also required by default; use
`--allow-missing-tdd-evidence` only when Red/Green history is unavailable and state that
limitation. The checker exits `0` only if every structural gate passes and emits metrics:

- **tests_pass** — the suite returns success; **no skipped/xfail** tests.
- **coverage_pct** — line coverage ≥ `--cov-min` (default 80).
- **bad_id_format** — ID-looking tokens that are not slug-only, including trailing numeric
  IDs, must be empty.
- **pr_traceability_pct** — every plan PR-ID is referenced by ≥1 test. Must be 100%.
- **id_traceability_pct** — every FR/AT/COMP/TEST appears in a test docstring/comment. Must
  be 100%.
- **id_assertion_traceability_pct** — every FR/AT/COMP/TEST appears in the same
  test/function block as a non-trivial assertion-like statement. Must be 100%.
- **oversized_modules** — files exceeding the LOC ceiling. Must be empty.
- **diff_loc / diff_evidence / oversized_diff** — actual added+deleted lines from
  `git diff --numstat` when git evidence is available. If unavailable, qualitative review
  must say actual PR size was not independently verified.
- **tdd_evidence** — Red/Green presence markers from git log between the review base and
  `HEAD`. This is a presence check, not proof that tests really failed before implementation;
  qualitative review must confirm TDD authenticity.
- **vague_hits** — TODO/FIXME/"etc."/skipped markers. Must be 0.
- **gates** + `passed/total`.

Present the JSON, then `passed/total`, coverage %, traceability %, assertion-traceability %,
diff evidence, and TDD evidence. List every uncovered PR/ID, ID without nearby assertion,
failing/skipped test, oversized module, and oversize diff explicitly.

## Verification A2 — Pre-Commit / Local Quality Gates

Verify that the implementation has language-appropriate local quality gates. Look for
`.pre-commit-config.yaml` first. If the repo intentionally uses another hook/check runner,
such as Husky/lint-staged, Lefthook, Overcommit, Gradle/Maven verification tasks, cargo
aliases, Make/NPM/Taskfile commands, or CI-only gates, verify the documented equivalent.

If neither pre-commit nor an equivalent one-command local quality gate is configured, report
this as a finding. A repo should not rely only on reviewer memory for formatting, linting,
type checking, tests, coverage, complexity, security, and dependency checks.

Run the gate, normally:

```pwsh
pre-commit run --all-files
```

If the project uses an equivalent command, run that command instead and report it. The gate
should cover the repo's languages and file types, using established project tools where
available. Examples include:

- **Python**: `ruff format`, `ruff check`, `ty`, `pyright`/`mypy`, `pytest`, `coverage`,
  `bandit`, `pip-audit`, `radon`/`xenon`.
- **JavaScript/TypeScript**: `prettier`, `eslint`, `tsc --noEmit`, `stylelint`, `vitest`/`jest`
  coverage, `playwright`, `npm audit`/`pnpm audit`, `knip`, `madge`, complexity rules.
- **Go**: `gofmt`, `go vet`, `staticcheck`, `golangci-lint`, `govulncheck`, `go test -cover`.
- **Rust**: `cargo fmt`, `cargo clippy -D warnings`, `cargo test`, `cargo llvm-cov`/`tarpaulin`,
  `cargo audit`.
- **Java/Kotlin**: Checkstyle, Spotless, PMD, SpotBugs, Error Prone, `detekt`, `ktlint`,
  Gradle/Maven test tasks, JaCoCo.
- **.NET/C#**: `dotnet format`, Roslyn/StyleCop analyzers, `dotnet test`, Coverlet.
- **Ruby/PHP/Swift/Dart**: RuboCop/Brakeman/SimpleCov; PHP-CS-Fixer/PHPCS/PHPStan/Psalm/PHPUnit;
  SwiftFormat/SwiftLint/Xcode tests; `dart format`, `dart analyze`, `flutter test --coverage`.
- **Shell/SQL/IaC/config/docs**: `shellcheck`, `shfmt`, `sqlfluff`, `hadolint`, `yamllint`,
  `actionlint`, `markdownlint`, `prettier`, `tflint`, `terraform fmt/validate`, `checkov`.
- **Cross-language**: `lizard`, Sonar-compatible reports, CodeQL where configured,
  dependency audits, `gitleaks` or equivalent secret scanning.
- **Build/deployment validation**: repo-native build commands, Docker/BuildKit or
  `docker compose config`, Kubernetes dry-run or `kubeconform`, Helm lint/template,
  Terraform/OpenTofu validate/plan, Bicep/ARM validation, CloudFormation validate,
  serverless/SAM/CDK synth, package publish dry runs, mobile archive/export validation, and
  environment smoke-test commands where available.

Verify thresholds are explicit and met. If the repo does not define thresholds, use these
minimum review expectations:

- Formatter, linter, type checker, dependency audit, and secret scan: zero errors.
- Tests: pass with no skips/xfails unless each is justified.
- Coverage: use the plan's threshold; if absent, at least 80% line coverage overall,
  70% branch coverage where available, and 90% line coverage for pure functional core modules.
- Complexity: cyclomatic complexity ≤10 per function/method and cognitive complexity ≤15
  where supported, with documented exceptions.
- Security/dependency scans: no critical/high findings; medium findings require accepted
  mitigation or follow-up.
- Module size: within the checker's `--max-loc` or stricter repo standard.
- Build/deployment: planned build command succeeds, expected artifact path/name/version is
  produced or validated, deployment manifests/scripts pass lint/dry-run/plan checks, smoke
  and rollback checks are run where planned, and no production deploy happened without
  explicit approval.
- Documentation: planned doc build/generation/link/readability/accessibility checks pass;
  examples or snippets are runnable where practical; public API/reference docs match the
  implemented contract; no user/developer-facing behavior change ships undocumented unless
  the plan explicitly says docs are out of scope.

## Verification B — Qualitative

Reasoned judgment, scored 1–5 with one concrete fix each:

- **TDD authenticity** — tests assert behaviour, not implementation; meaningful Red. Use
  available git history, review notes, command transcripts, or failing-test evidence. If no
  such evidence exists, report that TDD order was not independently verified rather than
  treating final green tests as proof.
- **Test implementation quality and level completeness** — executable acceptance/e2e/API
  workflow tests cover assigned `AT-` items, and planned `TEST-` obligations cover
  unit/pure-core logic, components, contracts, integrations, UI/accessibility/visual
  behavior, quality attributes, migrations, or operations as applicable. Review the test
  code itself: assertions, fixtures, helpers, mocks, generated data, setup/teardown,
  selectors, determinism, speed, isolation, readability, maintainability, and
  false-positive/false-negative risk.
- **Supplemental inner test quality** — code-discovered helper, pure-core, parser, mapper,
  regression, characterization, property/table, adapter, or edge-case tests supplement the
  planned coverage, cite the nearest `PR-` and relevant `FR-`/`AT-`/`TEST-`/`COMP-`, stay
  within the Planned Touch Set, use concrete oracles, and do not smuggle product-visible
  behavior or contract/UX/NFR changes past the upstream artifacts.
- **Verification-oracle rigor** — every test has a concrete pass/fail oracle aligned with
  the design/plan, such as return values, state changes, persisted records, emitted events,
  API responses, DOM/accessibility output, screenshots/visual baselines, generated
  artifacts, structured logs, metrics, traces, deployment signals, or captured external
  calls. Tests that only prove execution, mock invocation, or absence of exceptions are weak
  unless that is the specified behavior.
- **Contract realism** — mocks, fixtures, generated clients, captured examples, and
  contract/integration tests reflect the real producer/consumer boundary, including
  representative success and error variants. Ad-hoc string/object mocks that bypass the
  documented contract are defects.
- **UI quality and selector resilience** — planned styling/layout/responsive/accessibility
  and readable loading/empty/error/validation states are implemented; behavior tests use
  role/text/semantic selectors rather than CSS classes unless style is the contract under
  test.
- **Mock UI fidelity** — when a mock UI was required, production UI changes match the
  approved mock's screens, states, flows, copy intent, and responsive expectations, or
  clearly record an approved deviation.
- **Logging and telemetry fitness** — planned structured logs, events, metrics, traces,
  audit/support IDs, correlation propagation, redaction, alert hooks, and human/agent
  debugging signals are implemented, tested, stable, useful, and free of secrets or
  excessive noise.
- **Error-handling fitness** — UI, API, domain, integration, infrastructure, validation,
  authorization, timeout, offline, and unexpected failures map to safe messages, typed/
  documented errors, retries/fallback/degraded behavior, escalation, and logs/telemetry at
  the right boundary.
- **Build/deployment completeness** — assigned build/package work produces or validates the
  expected artifact; deployment scripts, manifests, IaC, migrations, smoke checks, rollback
  checks, and release docs are implemented and verified where planned.
- **Documentation completeness** — assigned user/developer docs, README/API/reference output,
  examples, tutorials, diagrams, runbooks, troubleshooting, release/migration notes, and doc
  generation are implemented and verified where planned.
- **Correctness** — code satisfies its FR/AT; edge cases handled at the lowest useful test
  level and not only through broad end-to-end tests.
- **Design fidelity** — matches COMP boundaries; pure core stays pure; no layering breaks.
- **Planned scope fidelity** — changed files/sections stay within each PR's Planned Touch Set;
  any out-of-scope edit is flagged as a plan/design/spec revision need, not accepted silently.
- **Readability** — plain test names (IDs in docstrings, not crammed into names), clear
  structure, no dead code. Test helpers and fixtures should reduce drift and duplication
  without obscuring the behavior being asserted.
- **Production quality** — error handling, validation, logging/telemetry, NFRs met,
  artifacts are reproducible, config/secrets are handled safely, documentation matches
  behavior, and deployment/rollback behavior is credible.
- **Quality gate fitness** — pre-commit/equivalent gates are language-appropriate,
  enforce thresholds, are not trivially bypassed, and align with CI.

## Report format

If blocked by Verification 0:

1. **Upstream blocker** (spec/design/plan IDs or sections + why it blocks code review).
2. Required upstream changes.
3. **Verdict**: Blocked-upstream.

Otherwise:

1. Mechanical scorecard (✅/❌ + IDs + totals).
2. Pre-commit/local quality gate scorecard (configured command, tools, thresholds, pass/fail).
3. Qualitative scorecard (1–5 + fixes).
4. **Top fixes** ranked by impact.
5. **Verdict**: Pass / Pass-with-fixes / Needs rework.

## Human review gate (hard stop)

After reporting the code assessment verdict, **stop**. Do not move to the next PR, release,
deployment, or any downstream artifact in the same turn. The next step requires explicit
user approval or an explicit unattended end-to-end instruction in the user's latest message.
