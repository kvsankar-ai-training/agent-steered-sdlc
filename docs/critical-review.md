# Critical Review: Agent-Steered SDLC

A critical assessment of the AI-agent-assisted software development process defined in
this repository — the eight `spec/design/plan/code` × `create/review` command prompts, the
four deterministic `checkers/*.py`, the `agent-steered-sdlc` skill, and the multi-tool
install tooling.

- **Reviewer scope:** the *process definition itself* — its claims, its enforcement
  mechanisms, and the gap between the two. Not a review of any product built with it.
- **Date:** 2026-06-29
- **Sources reviewed:** `AGENTS.md`, `prompts/*.prompt.md` (8), `checkers/*.py` (4),
  `skills/agent-steered-sdlc/SKILL.md`, `pyproject.toml`, `.pre-commit-config.yaml`.
- **Verification:** claims about checker behavior below were confirmed by running the
  checker code against probe inputs, not inferred from reading alone.
- **Remediation note, 2026-06-30:** this review is preserved as the pre-remediation critique.
  The repository now has checker tests, CI, safer `--tests-argv` execution, labeled coverage
  parsing, git diff/TDD evidence reporting, assertion-adjacent traceability checks, AT
  scenario-shape checks, NFR unit/quality checks, shared checker section schemas, a
  lightweight track, and adversarial-review guidance.

---

## 1. Executive summary

This is a genuinely thoughtful, internally coherent SDLC for steering coding agents. Its
spine — a traceability chain from stakeholder need to acceptance test to component to PR to
executable test, with deterministic coverage gates — is the strongest idea here and is well
executed at the structural level. The three-scope readiness model
(`Exploratory / Decomposable / Code-ready`) is a real contribution: it stops an agent from
coding straight out of a hand-wavy product brief.

The central weakness is a **mismatch between the rhetoric of enforcement and the reality of
enforcement.** The prompts repeatedly tell the agent these are "deterministic," "hard
metrics," "do not eyeball this," gates that "exit 0 only if every gate passes." In fact the
checkers verify *document hygiene* — that IDs exist, are cross-referenced as strings, are
zero-gap numbered, sections are present, and certain banned words are absent. They do **not**
verify the things the process most wants to guarantee: that tests are meaningful, that TDD
actually happened, that a PR is really ≤300 LOC, that coverage is really met, or that a
"covered" requirement is substantively tested rather than merely name-dropped. Worse, the
prompts explicitly instruct the agent to *optimize so review finds nothing to fix* — which,
against gates this shallow, is an invitation to coverage theater.

The second structural weakness is **non-independent verification.** Creator and reviewer are
the same model running sibling prompts, and the self-review loop ("repeat until `/x-review`
would Pass") has the same model grade its own homework with the same blind spots.

Both weaknesses are fixable, and the structural gates remain useful for what they actually
catch (missing sections, orphaned IDs, unbuilt requirements). The recommendation is to
**re-label the gates honestly, harden the few that are gameable by construction, and break
the self-grading circularity.**

**Overall:** strong design thinking, oversold enforcement. Use it, but do not trust the
green checkmark as evidence of correctness.

---

## 2. What the process gets right

These are real strengths and should be preserved.

1. **The traceability spine is coherent.** `UN → FEAT → UC → FR/NFR → AT → COMP → PR → test`
   is a clean, end-to-end chain, and the same IDs are threaded through every artifact and
   every checker. This is the best part of the system.
2. **Mechanical/qualitative separation is the right instinct.** Splitting "can a script
   check it?" from "does it need judgment?" is exactly how to divide labor between a
   deterministic gate and an LLM. The problem is *where the line was drawn* (§3), not the
   idea.
3. **The readiness model prevents premature implementation.** Forcing every artifact to
   declare `Exploratory / Decomposable / Code-ready`, and blocking `/code-create` unless it
   has a code-ready implementation plan, is a genuinely good guard against the classic agent
   failure of coding from a vague prompt.
4. **Test ownership is allocated deliberately across stages** (spec writes `AT-` intent,
   design defines the test architecture, plan schedules levels per PR, code makes them
   executable). The "don't push all coverage to E2E" guidance is sound testing advice.
5. **Tool-agnostic distribution is good engineering.** One canonical source installed into
   Codex / Copilot / Claude / Gemini / Pi targets, with cross-install for WSL/Windows.
6. **Upstream-consistency gates** in the review prompts (stop and fix the spec if the design
   exposes a spec defect) correctly model that defects are cheapest to fix upstream.
7. **Small-PR + TDD + functional-core/imperative-shell** is a defensible, opinionated house
   style that will produce more reviewable changes than an unconstrained agent.

---

## 3. The core problem: the checkers measure form, not substance

The prompts lean hard on the checkers for authority ("Do **not** eyeball this... hard
metrics"). But every coverage and quality gate reduces to **string presence**, so it is
satisfiable without the underlying property holding. This matters more than any other
finding because the whole process is sold on these gates being rigorous.

### 3.1 "Coverage" is co-reference, not verification

- `check_spec.py` counts a use case as covered if its ID **string appears anywhere inside
  any `AT-` block** (`covered_by`). An acceptance test that says *"AT-AUTH-10 — verifies
  UC-AUTH-10"* and nothing else yields **100% UC→AT coverage**. No check that the AT
  describes an observable behavior, a Given/When/Then, or anything testable.
- `check_plan.py` counts an `FR/AT/COMP` as covered if its ID appears in any delivery block
  or the Coverage Map. Listing the ID is sufficient.
- `check_code.py` counts an `FR/AT/COMP` as "traced" if the ID string appears in test file
  text (`i in test_text`) — and the prompts *instruct the agent to put those IDs in
  docstrings/comments*. A test body of `assert True` with `# Covers FR-AUTH-10` passes
  `id_traceability_100`.

**Consequence:** every coverage percentage in this system is a *name-matching* metric, not a
*semantic* one. An agent told to "optimize so review finds nothing" will reliably produce
100% on all of them while proving nothing.

### 3.2 TDD is verified by keyword, and Red is never observed

- `check_plan.py`'s `pr_tdd_red_green` gate passes if the whole words `red` and `green` both
  appear in the PR block. An agent writing `Red:` / `Green:` headers by template satisfies it
  regardless of whether test-first discipline occurred. (It does correctly require *whole
  words* — `evergreen` does not match — but that is the limit of its rigor.)
- `check_code.py` runs the final suite **once** and cannot see ordering. The headline
  principle "no prod line lands without a prior failing test" is **structurally
  unverifiable** by this tooling and is enforced only by the agent's self-report. The review
  prompt asks the reviewer to judge "meaningful Red," but at review time everything is green
  and there is no Red artifact to inspect — nothing examines git history.

### 3.3 The 300-LOC ceiling never measures a diff

- `check_plan.py` reads the LOC number the plan **declares** for each PR and checks it
  is ≤300. It never measures actual change size. A 900-line PR labeled "200 LOC" passes.
- `check_code.py` checks per-**file** length against `--max-loc` defaulting to **600** (not
  300, and per-file not per-PR). So the flagship "≤300 LOC reviewable PRs" guarantee is
  entirely on the honor system.

### 3.4 Coverage percentage parsing is fragile and silently wrong

`check_code.py` greps the test command's stdout/stderr for percentage tokens and takes the
**last** one as coverage (`COV.findall(…)` then `[-1]`). Confirmed by probe: against output
containing `100% [=====]`, `coverage: 42%`, and `98% faster`, it reports **98%** as coverage.
Any later percentage — a progress bar, a timing line, xdist worker output — silently becomes
"coverage" and can pass or fail the gate for the wrong reason.

### 3.5 The vagueness gate has false positives and false negatives

`vague_hits` is a banned-substring scan. Confirmed by probe: the benign sentence *"The system
uses a simple majority and a robust SMTP simplex link."* scores **2 violations** (`simple`
in "simple"/"simplex" context, `robust`). Meanwhile it is trivially evaded by synonyms
("straightforward," "quick," "solid"). It penalizes legitimate prose and misses real
vagueness — the worst of both directions.

### 3.6 NFR "has units" doesn't check the *right* unit

`check_spec.py` accepts an NFR if a number is followed by any unit from a hardcoded list
(`ms|s|%|mb|gb|req|rps|users|days|...`). A latency NFR reading *"supports up to 5 users"*
passes the units gate. The list is also web/infra-centric: a precision/accuracy NFR
("rounded to 2 decimal places," "±0.5°C") has no matching unit and must be reworded to
satisfy the regex rather than to be correct.

### 3.7 Design "no dependency cycles" and "tested" are easily false-passed

- `check_design.py` builds the dependency graph **only** from edges where a component's block
  references an `IFACE-` owned by another component. A design that states dependencies in
  prose ("COMP-A calls COMP-B") creates no edge, so a real cycle is invisible and the gate
  passes.
- A component counts as "tested" if its `COMP-` ID **appears in the Test Strategy section
  text** — one mention in a sentence satisfies `comp_test_coverage_100`.

> **The honest characterization:** these gates reliably catch *structural omissions* — a
> missing section, an unreferenced requirement, a malformed or duplicate ID, an interface
> with no owner. That is genuinely useful and worth keeping. They do **not** measure
> correctness, test quality, real size, real coverage, or real TDD, and the prompts should
> stop implying that they do.

---

## 4. Non-independent verification (the self-grading loop)

Every `*-create` prompt ends with: run the checker, then run/perform the matching `*-review`,
and **repeat until the review would Pass.** But:

- The reviewer is the **same model** running a sibling prompt. The qualitative pass — which
  is where all the real judgment lives, since the mechanical pass is shallow (§3) — is the
  LLM evaluating its own output with the same priors that produced it. An agent that wrote a
  plausible-but-wrong requirement tends to write a plausible-but-wrong acceptance test for it
  and pass its own review. Self-consistency is not correctness.
- The loop's termination condition ("until `/x-review` would return Pass") can converge on a
  *locally self-consistent* artifact set that is globally wrong, and it will report green.
- The much-emphasized "two distinct verifications" are not independent: one is a shallow
  deterministic check, the other is the same generator acting as judge. There is no
  adversarial or outside perspective anywhere in the loop.

This is the second-most-important finding. The process presents itself as having strong
review, but the review is structurally biased toward ratifying the creation.

---

## 5. Process-shape concerns

### 5.1 Ceremony cost vs. value

The full pipeline — SRS with `UN/FEAT/UC/FR/NFR/AT`, SDD with Mermaid context/component/
sequence/ER diagrams + ADRs + core/shell tables, a PR plan with touch sets and wave graphs +
an HTML companion, then TDD code — is a large amount of generated documentation. For
long-lived, multi-developer, safety- or compliance-relevant products this overhead is
justified. For the median agent task it is heavy. The three-scope model softens this
(slice/change can drop sections), but even a slice/change still runs multiple checkers and
multiple review passes and must satisfy coverage and section gates. There is a real risk that
teams either (a) pay disproportionate ceremony cost, or (b) quietly route around the process
for "small stuff," eroding it.

**The process needs an explicit, blessed lightweight path** for spikes, exploratory data/ML
work, infra-as-code, and throwaway prototypes — not just smaller documents, but permission to
skip stages — so the escape hatch is the documented one rather than an ad-hoc bypass.

### 5.2 Monoculture / one worldview baked into pass/fail

The checkers hard-require a single template and paradigm: exact section titles in exact order
(`Drivers & Constraints`, `Core vs. Shell`, `Non-Functional Requirements`), mandatory
functional-core/imperative-shell framing, `shall`-style requirements, Mermaid diagrams, ADRs,
300-LOC PRs, Red/Green. Each is defensible alone; together they impose one ideology as a
binary gate. A design that legitimately doesn't use core/shell separation must still emit a
"Core vs. Shell" section to pass. The prompts say "where relevant," but the *checkers* are
not that flexible. Opinionated defaults are fine; **opinions enforced as pass/fail with no
documented override are brittle.**

### 5.3 Duplicate sources of truth invite drift

- The required section list lives **twice**: as prose in each prompt and as a `SECTIONS`
  constant in each checker. Nothing keeps them in sync; if one is edited they diverge
  silently.
- `design.html` / `plan.html` companions duplicate `design.md` / `plan.md`. The only "check"
  that they match is a reviewer eyeballing them — manual and unenforced, so drift is likely.

### 5.4 Internal inconsistency on the coverage bar

`code-create` says default **80%** line coverage (90% for core); `check_code.py` defaults to
**100%**; the `code-review` prompt's example invocation passes `--cov-min 100`. Three
different numbers for the same knob. A 100% line-coverage gate is, on its own, a metric widely
known to induce low-value tests and gaming — especially under an explicit "optimize so review
finds nothing" instruction. The intended default should be stated once, in one place, with a
rationale.

---

## 6. Engineering / operational findings

1. **The checkers have no tests and no CI.** A repository whose entire thesis is "tests prove
   correctness, TDD always, high coverage" ships ~960 lines of parsing-heavy Python
   (fence handling, list-marker stripping, heading-level tracking) with **zero tests**, no
   coverage gate on itself, and no `.github`/CI. Pre-commit runs only `ruff` + `pymarkdown`.
   This is a credibility/dogfooding gap: the tool that judges everyone's tests is itself
   unverified, and its parsing is exactly the kind of subtle code that regresses invisibly.
   **This should be fixed first — it is the cheapest way to earn the authority the prompts
   claim.**
2. **`subprocess.run(cmd, shell=True)` on an agent-supplied `--tests` string** is an
   arbitrary-command-execution surface. Low risk for a local dev tool, but notable given the
   security-conscious framing and that an agent composes the command.
3. **Environment fragility is already visible.** The `python → python3 → uv run python`
   fallback ladder is repeated in every prompt and every checker invocation, implying the
   runtime has been flaky in practice. PowerShell-first examples assume a Windows-centric
   environment.
4. **Incomplete scaffolding:** `.agents/` is empty and `skills/.../agents/openai.yaml` is
   191 bytes — the multi-agent surface looks unfinished relative to the prose.
5. **No schema/version contract** between prompts and checkers. If a prompt's ID scheme or
   section list evolves, there is no versioned compatibility check; artifacts and checkers can
   silently disagree.

---

## 7. Risk summary

| # | Finding | Severity | Why it matters |
|---|---------|----------|----------------|
| 3.1 | Coverage = string co-reference, not verification | **High** | Core guarantee is gameable by construction; "optimize so review finds nothing" makes gaming the path of least resistance |
| 4 | Creator and reviewer are the same model; self-grading loop | **High** | The only deep check (qualitative) is biased toward ratifying the creation |
| 3.2 | TDD verified by keyword; Red never observed | **High** | "No code without a failing test" is unenforceable and unenforced |
| 3.3 | 300-LOC ceiling checks a declared number, not the diff | **Med-High** | Flagship "small PR" promise is honor-system only |
| 3.4 | Coverage % = last `%` token in output | **Medium** | Silent correctness bug; gate passes/fails for wrong reason |
| 6.1 | Checkers have no tests / no CI | **Medium** | Undermines the project's own thesis; invisible regressions |
| 5.1 | Ceremony cost; no blessed lightweight path | **Medium** | Process gets bypassed for small work, eroding adoption |
| 3.5–3.7 | Vagueness false +/-, NFR wrong-unit, design cycle/test false-pass | **Medium** | Gates give false confidence in both directions |
| 5.2 | One paradigm enforced as binary pass/fail | **Medium** | Brittle outside the assumed architecture style |
| 5.3 | Section list & HTML duplicated; drift risk | **Low-Med** | Maintenance hazard |
| 5.4 | 80 vs 100 coverage inconsistency | **Low-Med** | Confusing; 100% gate can backfire |
| 6.2 | `shell=True` on agent-supplied command | **Low** | Execution surface |

---

## 8. Recommendations (prioritized)

### Do first — cheap, high-credibility

1. **Test the checkers and put them in CI.** Add a `tests/` suite covering the parsing edge
   cases (fences, list markers, heading levels, the coverage-parse bug, the vagueness false
   positives). Apply this repo's own coverage gate to its own code. Until the judge is
   tested, its verdicts are unearned.
2. **Re-label the gates honestly in the prompts.** Replace "hard metrics / do not eyeball"
   with an accurate statement: *these gates catch structural omissions (missing sections,
   orphan/duplicate IDs, unbuilt requirements); they do not measure correctness, test quality,
   real size, or real coverage — that is the reviewer's job.* This single change removes the
   false confidence without touching code.
3. **Fix the coverage-percent parser.** Anchor on a labeled token (`TOTAL ... NN%`, or
   `coverage: NN%`), or require a machine-readable coverage report (`coverage.json`,
   `--cov-report=json`, `lcov`) instead of scraping stdout for the last `%`.
4. **Resolve the 80/100 coverage contradiction** to one documented default with a rationale,
   and stop defaulting to 100% unless a domain genuinely warrants it.

### Do next — close the gameable gaps

1. **Measure real PR size and real Red.** Have `check_code.py` (or a new git-aware checker)
   read `git diff --stat` for actual changed LOC against 300, and inspect commit history for a
   failing-test commit preceding the implementation commit. Without git evidence, demote "TDD"
   and "≤300 LOC" from "gate" to "self-reported claim" in the prompts.
2. **Make coverage semantic, not lexical, where feasible.** At minimum, require an `AT-`/test
   to contain a Given/When/Then or an assertion structure, not just the referenced ID. Flag
   tests whose only link to a requirement is a comment with no assertion touching it.
3. **Break the self-grading circularity.** Run the `*-review` pass as a *separate, adversarial
   role* — a different system prompt explicitly instructed to refute the artifact and default
   to "needs rework" when unsure, ideally a different model or a fresh context with no memory
   of authoring. Even a structural change (review must cite a concrete counterexample to pass)
   reduces rubber-stamping.

### Do when convenient — robustness and reach

1. **Add a documented lightweight track** (spike / prototype / data-exploration / IaC) that is
   allowed to skip stages, so the escape hatch is blessed rather than improvised.
2. **Single-source the section schema.** Generate the prompt's section list from the checker
   constant (or vice versa) so they cannot drift; consider generating `*.html` from `*.md`
   instead of maintaining both.
3. **Soften paradigm lock-in.** Allow a design to declare "no core/shell split applies here"
   and satisfy the gate with a justification, rather than forcing an empty section.
4. **Replace the substring vagueness scan** with something that has fewer false positives
   (word-boundary + context, or drop it and let the reviewer own vagueness), and make the NFR
   check validate that the unit *matches the quality being constrained*.
5. **Harden `shell=True`** by accepting an argv list, or document the trust boundary.

---

## 9. Bottom line

The architecture of this process is good and the traceability spine is worth building on. The
problem is not the design — it is that the **enforcement layer is far weaker than the prompts
claim**, and the **review layer is the same agent grading itself.** Today, a fully green run
of all four checkers plus all four self-reviews is consistent with an artifact set that is
name-matched, keyword-decorated, and substantively wrong — and the process's own "optimize so
review finds nothing" instruction actively steers toward that outcome.

Close the gap between claim and reality — test the checkers, re-label the gates honestly, fix
the genuinely buggy ones, measure size/TDD/coverage from real evidence, and make review
adversarial and independent — and this becomes a strong, trustworthy agent SDLC rather than a
well-structured one that overstates its own assurances.
