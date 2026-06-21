---
name: multi-model-workflow
description: Routes a feature through three model-specialist phases — Plan (Claude Opus), Code (Claude Sonnet or Codex GPT), Review (Codex GPT) — to match model capability to task cost. Use when building any non-trivial feature and you want planning depth from the frontier model, fast execution from a capable mid-tier, and an independent review from a different model family. Triggers on "multi-model workflow", "plan with opus", "plan then build", "route this across models", or when explicitly invoked with /multi-model-workflow.
---

# Multi-Model Workflow

Three specialists, one feature. Route each phase to the model best suited for it:

| Phase | Model | Why |
|---|---|---|
| **Plan** | Claude Opus 4.8 | Sees around corners. Best at full-codebase reasoning and architectural decisions. |
| **Code** | Claude Sonnet 4.6 or Codex GPT-5.5 | Excellent at execution once the plan is clear. Faster and cheaper than Opus for implementation. |
| **Review** | Codex GPT-5.5 | Independent model family. Catches what the author missed. Different training = different blind spots. |

## Auto-Detection

The skill detects which phase to run based on current state. You can also pass an explicit phase argument.

```
/multi-model-workflow                    → auto-detect
/multi-model-workflow plan <task>        → force Phase 1
/multi-model-workflow code               → force Phase 2 (reads tasks/PLAN.md)
/multi-model-workflow review             → force Phase 3 (reviews current branch)
```

**Auto-detect rules:**
1. No `tasks/PLAN.md` + task description given → **Phase 1**
2. `tasks/PLAN.md` exists + no open PR → **Phase 2**
3. Open PR or reviewed branch → **Phase 3**
4. Ambiguous → ask which phase

---

## Phase 1 — Plan (Claude Opus 4.8)

**Goal:** Produce a complete, unambiguous implementation plan before any code is written.

**Best run in:** Claude Code with Opus. In Claude Code CLI: `claude --model claude-opus-4-8` or toggle `/fast`.

### Steps

1. **Understand the task**
   - Restate the task in one sentence. Ask one clarifying question if anything is ambiguous. Do not ask multiple questions at once.
   - Identify: what changes, which files, what the acceptance criteria are.

2. **Survey the codebase**
   - Read `CLAUDE.md` / `AGENTS.md` for project conventions.
   - Find files relevant to the task: `grep -r "<keyword>" --include="*.py" --include="*.ts" -l`
   - Read the relevant files in full. Do not skim.

3. **Identify risks and alternatives**
   - Name the two most likely ways this plan could go wrong.
   - Name one alternative approach and state why you rejected it.

4. **Write `tasks/PLAN.md`**

   Use this exact structure:

   ```markdown
   # Plan: <task title>
   Generated: <date> | Model: Claude Opus 4.8

   ## What We're Building
   <one paragraph, concrete>

   ## Files to Touch
   | File | Change |
   |---|---|
   | path/to/file.py | <what changes and why> |

   ## Implementation Steps
   1. <atomic step — one file or one function>
   2. ...

   ## Acceptance Criteria
   - [ ] <verifiable, testable criterion>

   ## Risks
   - <risk 1> → mitigation
   - <risk 2> → mitigation

   ## Rejected Alternative
   <approach> — rejected because <reason>

   ## Handoff Notes for Code Phase
   <anything the coding agent needs to know that isn't obvious from the files>
   ```

5. **Hand off**
   - Confirm `tasks/PLAN.md` is written.
   - Tell the user: "Plan complete. Run `/multi-model-workflow code` in Claude Sonnet (default mode) or open in Codex to execute."
   - Do not start writing code.

---

## Phase 2 — Code (Claude Sonnet 4.6 or Codex GPT-5.5)

**Goal:** Execute `tasks/PLAN.md` exactly. No scope creep.

**Best run in:** Claude Code default session (Sonnet 4.6) or Codex (GPT-5.5). Both work; Codex gives more concise output.

### Steps

1. **Read the plan**
   - Read `tasks/PLAN.md` in full before touching any file.
   - If the plan is ambiguous, stop and resolve the ambiguity before proceeding.

2. **Execute incrementally** — follow `incremental-implementation`:
   - Implement one step from the plan at a time.
   - After each step: run tests, confirm the system is in a working state.
   - Never implement multiple steps in one pass.

3. **Stay in scope**
   - Touch only files listed in `tasks/PLAN.md > Files to Touch`.
   - If you discover a needed change not in the plan, stop and add it to the plan first.

4. **Apply overlays as needed**
   - API or interface work → `api-and-interface-design`
   - UI work → `frontend-ui-engineering`
   - Framework-specific patterns → `source-driven-development`
   - High-stakes or unfamiliar code → `doubt-driven-development`

5. **Verify**
   - Run the full test suite: `python3 -m pytest -q` or `npm test` (whichever applies).
   - Check the acceptance criteria in `tasks/PLAN.md` one by one.
   - Commit: `git add -A && git commit -m "<type>: <description> (multi-model-workflow code phase)"`

6. **Hand off**
   - Push the branch: `git push origin <branch>`
   - Open a draft PR: `gh pr create --draft --title "<task>" --body "Multi-model workflow — code phase complete. Awaiting Codex review."`
   - Tell the user: "Code phase done. Open the PR in Codex with GPT-5.5 for independent review: `gh pr view --web`"

---

## Phase 3 — Review (Codex GPT-5.5)

**Goal:** Independent model review — catch what the author missed, from a different training distribution.

**Best run in:** Codex (GPT-5.5). Switch hosts deliberately for this phase. Running in the same model that wrote the code reduces review value.

### Steps

1. **Get the diff**
   ```bash
   git fetch origin
   git diff origin/main...HEAD
   ```

2. **Review against five axes** — follow `code-review-and-quality`:
   - **Correctness** — does it do what `tasks/PLAN.md` says? Does it handle edge cases?
   - **Security** — any new attack surface? Input validation? Auth checks?
   - **Architecture** — does this fit the existing patterns? Any unnecessary coupling?
   - **Performance** — any new N+1 queries, blocking calls, or hot-path regressions?
   - **Tests** — are the acceptance criteria from `tasks/PLAN.md` covered by tests?

3. **Classify each finding**
   - `BLOCKER` — must fix before merge
   - `SUGGESTION` — good idea, not required
   - `NITPICK` — style only, skip unless trivial

4. **Fix all BLOCKERs**
   - Fix each blocker directly. Do not leave them as comments.
   - Re-run tests after each fix.

5. **Write the review report to `tasks/REVIEW.md`**

   ```markdown
   # Review: <task title>
   Reviewed: <date> | Model: Codex GPT-5.5

   ## Verdict
   APPROVED / APPROVED WITH FIXES / BLOCKED

   ## Findings
   | Severity | File | Line | Finding | Fixed? |
   |---|---|---|---|---|
   | BLOCKER | path/to/file | 42 | <what's wrong> | yes/no |
   | SUGGESTION | ... | ... | ... | — |

   ## Acceptance Criteria Check
   - [x] criterion 1 — covered by test_foo.py:42
   - [ ] criterion 2 — NOT COVERED

   ## Summary
   <2-3 sentences on overall quality and confidence>
   ```

6. **Hand off**
   - If verdict is APPROVED or APPROVED WITH FIXES: mark PR ready for review — `gh pr ready`
   - If BLOCKED: push fixes and re-request review
   - Tell the user: "Review complete. See `tasks/REVIEW.md`. PR is [ready / blocked — see findings]."

---

## Model Switching Cheat Sheet

| Host | How to switch to Opus | How to use GPT-5.5 |
|---|---|---|
| Claude Code CLI | `claude --model claude-opus-4-8` or `/fast` toggle | Open in Codex |
| Codex | Not applicable — use Claude Code for Opus | Default model |

**The key discipline:** switch hosts intentionally at each phase boundary. Do not run all three phases in one session with one model — that defeats the purpose.

---

## Gotchas

- **Skipping phases:** Running Plan and Code in the same Sonnet session is cheaper but loses the architectural depth Opus provides. Reserve the shortcut for genuinely trivial tasks.
- **Reviewing your own code:** If you run Phase 3 in the same model that ran Phase 2, the review is weaker. The value is the model switch.
- **Plan drift:** If the implementation diverges from `tasks/PLAN.md`, update the plan before continuing — don't let the two fall out of sync.
- **Never start Phase 2 without a complete `tasks/PLAN.md`:** Partial plans produce partial implementations. The plan gating exists for a reason.
- **Draft PR is required before Phase 3:** The reviewer needs a diff to work from, not an explanation of what changed.

---

## Verification

- [ ] `tasks/PLAN.md` exists and is complete (Phase 1 done)
- [ ] All acceptance criteria from `tasks/PLAN.md` are covered by tests (Phase 2 done)
- [ ] `tasks/REVIEW.md` exists with a verdict (Phase 3 done)
- [ ] No BLOCKER findings remain open
- [ ] PR is marked ready (not draft)
- [ ] `tasks/PLAN.md` and `tasks/REVIEW.md` are committed to the branch

---

## Skill Relationships

### Category
Business Automation

### Lifecycle Position
Meta-orchestrator — wraps spec-driven-development (Phase 1 input), incremental-implementation (Phase 2 execution), and code-review-and-quality (Phase 3 review) into a cross-model routing workflow. Sits above the individual build-phase skills.

### Dependencies
- `spec-driven-development` — run first if requirements are unclear; this skill assumes requirements are already resolved
- `planning-and-task-breakdown` — alternative to Phase 1 for task-level (not feature-level) planning

### Relationships
| Skill | Pattern | Condition | Handoff Artifact |
|---|---|---|---|
| `spec-driven-development` | Sequential upstream | if requirements unclear before planning | SPEC.md → feeds Phase 1 task description |
| `incremental-implementation` | Sequential downstream | Phase 2 execution follows this skill's build loop | tasks/PLAN.md → implementation |
| `code-review-and-quality` | Sequential downstream | Phase 3 uses this skill's five-axis review framework | PR diff → tasks/REVIEW.md |
| `doubt-driven-development` | Behavioral overlay | apply during Phase 2 for high-stakes decisions | — |
| `api-and-interface-design` | Behavioral overlay | apply during Phase 2 when plan includes new interfaces | — |
| `using-agent-skills` | Prerequisite / Gate | using-agent-skills governs when this skill fires | — |

### Runtime Preamble
Running multi-model-workflow. Phase 1 (Plan) is best in Claude Opus — switch with `claude --model claude-opus-4-8` or `/fast`. Phase 2 (Code) runs in default Sonnet or Codex GPT-5.5. Phase 3 (Review) must run in Codex for an independent model perspective.

---

## Host Compatibility

### Target Hosts
- Claude Code: yes — primary host for Phase 1 (Opus) and Phase 2 (Sonnet). Installed via `agent-skills@addy-agent-skills` plugin.
- Codex/OpenAI: yes — primary host for Phase 3 (GPT-5.5 review). Installed via `agent-skills@addy-agent-skills` plugin.

### Tool Mapping
| Claude Code | Codex |
|---|---|
| `Read` / `Grep` / `Glob` | shell reads / `rg` |
| `Edit` / `MultiEdit` | `apply_patch` |
| `Bash` | shell command |
| `AskUserQuestion` | concise chat question |

### Source / Tool Order
1. Read `tasks/PLAN.md` and `CLAUDE.md` / `AGENTS.md` before any implementation work.
2. Read relevant source files in full — do not skim or grep-substitute for reading.
3. Use official documentation MCPs or `source-driven-development` for framework-specific patterns.
4. Use generic web search only as fallback for official-source verification.
