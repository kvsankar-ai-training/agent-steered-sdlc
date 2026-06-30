# Critical Review — Round 2 (Post-Remediation)

A second-round assessment of the agent-steered SDLC after the remediation described in the
top note of [`critical-review.md`](critical-review.md). Companion to that document, which is
preserved as the pre-remediation critique.

- **Reviewer scope:** the same process definition — prompts, checkers, skill, install
  tooling — re-examined against the round-1 findings, plus a fresh adversarial probe of the
  *new* gates.
- **Date:** 2026-06-30
- **Method:** every claim below was **verified by running the code** — the test suite, the
  checker internals against crafted inputs, and git-evidence paths — not inferred from
  reading. Where I say a gate is gameable, I demonstrated it.
- **Repository state reviewed:** commit `0193380` "Harden agent-steered SDLC workflow."
- **Remediation note:** this document is preserved as the round-2 critique. A later hardening
  pass made git diff/TDD evidence default-on for code review, changed no-base diff evidence
  from `HEAD` comparison to "unverified", tightened assertion traceability to the same
  test/function block, rejects trivial tautology assertions, and labels keyword-style gates
  as presence checks requiring qualitative confirmation.

---

## 1. Verdict

This is a **serious, good-faith remediation, not checkbox theater.** The single most
important round-1 finding — that the prompts *oversold* shallow gates as rigorous proof — has
been genuinely fixed: the "do not eyeball this / hard metrics" rhetoric is gone and replaced,
everywhere, with an explicit statement that the checkers are *structural* and "do not prove
requirements are correct, complete, or semantically well tested." That honesty change is
worth more than any single new gate, because it stops the green checkmark from masquerading
as correctness.

The engineering hygiene gaps are closed too: the checkers now have a test suite (16 tests,
all passing) and CI; `shell=True` is opt-in behind `--tests-shell`; the coverage parser no
longer mistakes a progress bar for coverage; the section schema is single-sourced; the
80-vs-100 coverage contradiction is resolved to 80 consistently.

**Where it lands:** the system is still, fundamentally, a *lexical/structural* gate layer
plus LLM judgment — and it now **advertises itself as exactly that.** The remediation moved
several gates from "pure name-match" to "name-match plus a little evidence," which raises the
floor without changing the architecture. The residual weaknesses are incremental (gates still
satisfiable by template words and tautological assertions; the strongest new checks are
opt-in and off by default), not the credibility-level mismatch round 1 identified.

**Round-1 findings substantially resolved: most. Architecture-level concern remaining: the
verification is still LLM-judges-its-own-output, now honestly disclosed rather than
eliminated.**

---

## 2. What was fixed — verified

| # | Round-1 finding | Status | Verification |
|---|---|---|---|
| 6.1 | Checkers had no tests / no CI | **Fixed** | `uv run pytest -q` → 16 passed; `.github/workflows/ci.yml` runs ruff + markdown + pytest `--cov-fail-under=80` |
| Exec summary | Prompts oversold gates as rigor | **Fixed** | "eyeball/hard metrics" grep → 0 hits; every prompt + `AGENTS.md` now says the checker is a "deterministic **structural** check" that "does not prove requirements are correct, complete, or semantically well tested" |
| 3.4 | Coverage = last `%` token (buggy) | **Fixed** | `extract_coverage` now matches only `TOTAL … NN%` or `coverage: NN%`; probe with `100% [=====]`, `coverage: 42%`, `98% faster` → returns **42.0**; unlabeled `100% [progress]` → coverage `None`, gate fails |
| 6.2 | `shell=True` on agent string | **Fixed** | Default is `--tests-argv` (JSON array) or `shlex.split`; shell execution only with explicit `--tests-shell` |
| 3.5 | Vagueness false positives | **Fixed** | `simple`/`robust` removed; word-boundary regex; probe of "simple majority / robust SMTP" → **0** hits |
| 3.6 | NFR "has units" ignored the *right* unit | **Fixed** | New `nfr_units_match_quality` gate with a quality→unit map; their test proves a latency NFR measured in "users" is rejected |
| 5.4 | 80 vs 100 coverage contradiction | **Fixed** | `check_code` default now 80; prompts say 80; CI 80 |
| 5.3 (part) | Section list duplicated in prose + code | **Fixed** | `checkers/schemas.py` is the single source; all three checkers import it |
| 5.2 | One paradigm enforced as pass/fail | **Improved** | Design accepts `Core vs. Shell` **or** `Core vs. Shell / Equivalent Separation`; test proves the alias passes |
| 5.1 | No blessed lightweight path | **Fixed** | `AGENTS.md` + create prompts add a "Lightweight track" for spikes/prototypes/IaC with disposal criteria |
| 4 | Self-grading circularity | **Addressed (instruction-level)** | All review prompts + `docs/review-verification-checklist.md` mandate an adversarial posture, fresh-context/separate-model reviewer, and a two-sub-agent split; require stating "review is not independent" when the same agent created and reviewed |

These are real and, in most cases, well-targeted. The coverage-parser, vagueness, NFR-unit,
safe-exec, single-source-schema, and honesty-relabel fixes are complete and I could not break
them.

---

## 3. What remains — residual findings (verified)

The remediation raised the floor; it did not change the fact that the gates are still mostly
lexical. The honest re-labeling now *covers* this, but for a faithful second round these are
the gaps that a passing run can still hide.

### 3.1 The new assertion-traceability gate is better than name-drop, but still gameable

Round 1's worst case (`# Covers FR-AUTH-10` over `assert True` counting as coverage) is
closed: `id_assertion_traceability_100` now requires a non-weak assertion near the ID, and
their test proves `assert True` is rejected. But I broke it two ways:

- **Tautologies pass.** `assert 1 == 1` near the ID satisfies the gate — only the literal
  `assert true` family is treated as weak. Probe: `assertion_linked_ids` returned
  `{'FR-AUTH-10'}` for a body whose only statement is `assert 1 == 1`.
- **Proximity ≠ relationship.** The gate credits an ID if *any* assertion appears within the
  18-line window — including an assertion belonging to a **different, adjacent test**. Probe:
  an ID mentioned over an empty `pass` test was marked "assertion-linked" because a real
  assertion sat 6 lines above in an unrelated test. So an agent can earn the gate for a
  placeholder by parking it next to a genuine test.

### 3.2 Scenario-shape, TDD, and quality gates are still satisfiable by template words

- `ats_have_scenario_shape` passes on a single word. Probe: `"AT-X-10 verify UC-X-10."`
  passes (the word `verify` alone clears it). It blocks a bare `Covers …` line — a real
  improvement — but an agent that writes `verify`/`then` once still passes.
- `pr_tdd_red_green` (plan) is unchanged: the whole words `red` and `green` in the PR block.
- `git_tdd_evidence` (code) reads `red`/`green` markers from **commit messages**. This moves
  the keyword check from the plan text to the commit log; it is still keyword presence, and a
  commit titled `"red: … green: …"` satisfies it without any real Red-then-Green history.
- `nfr_units_match_quality` only fires when a quality keyword is present. Probe: an NFR with
  no keyword from the map ("handle 5 users … 100 ms") yields **no** mismatch — the unit/
  quality check silently skips.

### 3.3 The strongest new checks are opt-in and off by default

The two checks that would convert honor-system claims into measured facts are not on unless
the reviewer passes flags:

- **Real diff size** (`diff_size_ok`) is enforced only with `--require-git-evidence`;
  otherwise a `None`/over-limit diff still passes. Worse, with **no `--diff-base`**,
  `git_diff_loc` compares the working tree to `HEAD`, which is **0 after the PR is
  committed.** Probe: a committed 500-line change reports `diff_loc = 0`. So absent a base
  branch, the "measure the real diff against 300" fix is a no-op that reports a reassuring
  zero. The always-on size gate is still the plan's **self-declared** LOC number.
- **TDD evidence** (`tdd_evidence_ok`) is enforced only with `--require-tdd-evidence`.

The prompts wire these flags conditionally ("when a git base is known," "only when the
workflow preserves Red/Green evidence"). That is honestly framed, but it means the flagship
"size and TDD are now measured from git" improvement is conditional, and the default run still
relies on agent self-report for both.

### 3.4 Checker self-coverage is uneven where it matters most

CI gates at 80% and the suite reports 81% overall — but `check_code.py`, the most complex and
the only checker that executes commands and shells out to git, sits at **73%**, with several
git-evidence and output branches uncovered. The newest, riskiest code is the least tested.

### 3.5 Independence is disclosed, not achieved, on the fallback path

The adversarial/fresh-context/sub-agent guidance is the right design, and when the platform
supports sub-agents it genuinely separates creation from review. But the documented fallback —
"if the same agent created and reviewed, state that the review is not independent" — makes the
limitation *honest*, not *absent*. A disclaimer does not give the judge a second pair of eyes.
This is likely the ceiling for a prompt-level system, and the project now handles it about as
well as prompts can; it is noted so the residual risk is not mistaken for closed.

### 3.6 Minor / carried-over

- HTML companions (`design.html`, `plan.html`) are still duplicate sources of truth kept in
  sync only by a reviewer's eyeball; round-1 recommendation to generate them was not taken.

---

## 4. Net assessment and recommendations

**Net:** the remediation resolved the credibility problem (over-claimed rigor), the
engineering-hygiene problem (no tests, unsafe exec, buggy parsing, inconsistent thresholds),
and the worst single gameability case (name-drop coverage). What remains is the irreducible
nature of lexical gates plus an LLM judge — now correctly labeled. This is a meaningfully
stronger and more honest system than round 1 reviewed.

**If a third increment is wanted, in priority order:**

1. **Make the real-diff and TDD evidence the default for `/code-review`,** with a base
   branch resolved automatically (e.g. merge-base with the default branch). A measured diff
   of `0` against `HEAD` should be reported as "no base — size unverified," never as a pass.
2. **Strengthen the assertion gate against tautologies and neighbor-bleed:** treat
   constant-equals-constant asserts as weak, and require the assertion to sit inside the same
   test/function block as the ID reference rather than within a line window.
3. **Raise `check_code` self-coverage** to match the others, focusing on the git-evidence and
   command-execution branches — that is the code whose silent failure would most undermine a
   verdict.
4. **State plainly in the prompts that the keyword gates** (`pr_tdd_red_green`, scenario
   shape, commit-message markers) **are presence checks the qualitative reviewer must
   confirm** — the same honesty move already applied to the checkers, extended to the few
   gates where it is not yet explicit.

None of these is architectural. The structure is sound; the remaining work is hardening the
evidence the gates actually collect and defaulting the strong checks on.
