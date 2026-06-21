#!/usr/bin/env python3
"""Append Skill Relationships and Host Compatibility sections to all skills."""

import os

SKILLS_DIR = os.path.join(os.path.dirname(__file__), "..", "skills")

# Lifecycle position string per skill
LIFECYCLE = {
    "interview-me": "Step 1 of 13 — Define phase. First skill in the full lifecycle.",
    "idea-refine": "Step 2 of 13 — Define phase. Runs after interview-me, before spec-driven-development.",
    "spec-driven-development": "Step 3 of 13 — Define phase. Runs after idea-refine, before planning-and-task-breakdown.",
    "planning-and-task-breakdown": "Step 4 of 13 — Plan phase. Runs after spec-driven-development, before build phase.",
    "context-engineering": "Step 5 of 13 — Build phase. Runs after planning-and-task-breakdown to load context before coding starts.",
    "source-driven-development": "Step 6 of 13 — Build phase. Behavioral overlay: verifies implementation decisions against official docs throughout the build phase.",
    "incremental-implementation": "Step 7 of 13 — Build phase. Core build skill; orchestrates test-driven-development per slice.",
    "doubt-driven-development": "Step 8 of 13 — Build phase. Behavioral overlay: adversarial review of any non-trivial in-flight decision.",
    "test-driven-development": "Step 9 of 13 — Verify phase. Runs after each incremental-implementation slice; proves behavior before review.",
    "browser-testing-with-devtools": "Verify phase — peer to test-driven-development for browser-specific runtime verification.",
    "debugging-and-error-recovery": "Verify phase — fallback skill invoked when any build or verify step fails unexpectedly.",
    "code-review-and-quality": "Step 10 of 13 — Review phase. Runs after test-driven-development, before git-workflow-and-versioning.",
    "code-simplification": "Review phase — peer to code-review-and-quality; focus is clarity, not correctness.",
    "security-and-hardening": "Review phase — complement to code-review-and-quality for security-sensitive changes.",
    "performance-optimization": "Review phase — complement to code-review-and-quality when performance regressions are suspected.",
    "git-workflow-and-versioning": "Step 11 of 13 — Ship phase. Runs after code-review-and-quality, before ci-cd-and-automation.",
    "documentation-and-adrs": "Step 12 of 13 — Ship phase. Runs alongside or immediately after shipping-and-launch.",
    "ci-cd-and-automation": "Ship phase — peer to git-workflow-and-versioning; automates quality gates for every commit.",
    "deprecation-and-migration": "Ship phase — activated when removing old systems or migrating users between implementations.",
    "shipping-and-launch": "Step 13 of 13 — Ship phase. Final skill in the full lifecycle.",
    "api-and-interface-design": "Build phase — specialist skill invoked when incremental-implementation involves API or interface work.",
    "frontend-ui-engineering": "Build phase — specialist skill invoked when incremental-implementation involves UI work.",
    "using-agent-skills": "Meta — orchestrator skill. Entry point for the entire lifecycle; governs skill discovery and sequencing.",
}

# Category per skill
CATEGORY = {
    "interview-me": "Business Automation",
    "idea-refine": "Scaffolding & Templates",
    "spec-driven-development": "Scaffolding & Templates",
    "planning-and-task-breakdown": "Business Automation",
    "context-engineering": "Infrastructure Ops",
    "source-driven-development": "Library / API Reference",
    "incremental-implementation": "Business Automation",
    "doubt-driven-development": "Code Quality & Review",
    "test-driven-development": "Product Verification",
    "browser-testing-with-devtools": "Product Verification",
    "debugging-and-error-recovery": "Runbook",
    "code-review-and-quality": "Code Quality & Review",
    "code-simplification": "Code Quality & Review",
    "security-and-hardening": "Code Quality & Review",
    "performance-optimization": "Product Verification",
    "git-workflow-and-versioning": "CI/CD & Deployment",
    "documentation-and-adrs": "Scaffolding & Templates",
    "ci-cd-and-automation": "CI/CD & Deployment",
    "deprecation-and-migration": "CI/CD & Deployment",
    "shipping-and-launch": "CI/CD & Deployment",
    "api-and-interface-design": "Library / API Reference",
    "frontend-ui-engineering": "Scaffolding & Templates",
    "using-agent-skills": "Infrastructure Ops",
}

# Relationships table rows per skill: (peer_skill, pattern, condition, handoff)
RELATIONSHIPS = {
    "interview-me": [
        ("idea-refine", "Sequential downstream", "if idea exists but is vague", "captured intent in conversation"),
        ("spec-driven-development", "Sequential downstream", "if requirements are clear after interview", "captured requirements in conversation"),
        ("spec-driven-development", "Prerequisite / Gate", "always — spec should not start without intent clarity", "—"),
    ],
    "idea-refine": [
        ("interview-me", "Sequential upstream", "optional — if intent is unclear before ideation", "captured intent in conversation"),
        ("spec-driven-development", "Sequential downstream", "always — refined idea feeds the spec", "refined idea summary in conversation"),
        ("interview-me", "Alternative / Peer", "use interview-me when needs are unclear; use idea-refine when needs are clear but idea is vague", "—"),
    ],
    "spec-driven-development": [
        ("interview-me", "Sequential upstream", "optional — run first if requirements are ambiguous", "captured intent"),
        ("idea-refine", "Sequential upstream", "optional — run first if idea needs sharpening", "refined idea summary"),
        ("planning-and-task-breakdown", "Sequential downstream", "always — spec feeds the task breakdown", "SPEC.md"),
        ("documentation-and-adrs", "Amplifier", "optional — ADRs capture decisions made during spec phase", "SPEC.md → ADR entries"),
    ],
    "planning-and-task-breakdown": [
        ("spec-driven-development", "Sequential upstream", "always — requires a spec or clear requirements", "SPEC.md or inline requirements"),
        ("incremental-implementation", "Sequential downstream", "always — tasks feed the build phase", "tasks/plan.md, tasks/todo.md"),
        ("context-engineering", "Sequential downstream", "recommended — load context before build starts", "tasks/todo.md"),
    ],
    "context-engineering": [
        ("planning-and-task-breakdown", "Sequential upstream", "recommended — task plan clarifies what context to load", "tasks/plan.md"),
        ("incremental-implementation", "Behavioral overlay", "always — improves output quality of any build-phase skill", "—"),
        ("source-driven-development", "Behavioral overlay", "always — pair with source-driven-development for verified context", "—"),
    ],
    "source-driven-development": [
        ("incremental-implementation", "Behavioral overlay", "always when using a framework or library", "verified code with source citations"),
        ("api-and-interface-design", "Behavioral overlay", "always — API decisions must be doc-verified", "—"),
        ("frontend-ui-engineering", "Behavioral overlay", "always — component and framework patterns must be doc-verified", "—"),
        ("context-engineering", "Peer", "pair together: context-engineering loads the workspace; source-driven-development verifies decisions against docs", "—"),
    ],
    "incremental-implementation": [
        ("planning-and-task-breakdown", "Sequential upstream", "always — requires a task breakdown before building", "tasks/todo.md"),
        ("test-driven-development", "Sequential downstream", "always — each slice must be tested before expanding", "implementation code per slice"),
        ("context-engineering", "Behavioral overlay", "recommended — load context before each session", "—"),
        ("source-driven-development", "Behavioral overlay", "recommended — verify framework usage against official docs", "—"),
        ("doubt-driven-development", "Behavioral overlay", "when stakes are high or code is unfamiliar", "—"),
        ("api-and-interface-design", "Peer", "invoke api-and-interface-design when the slice involves a new API or interface boundary", "—"),
        ("frontend-ui-engineering", "Peer", "invoke frontend-ui-engineering when the slice involves UI components", "—"),
    ],
    "doubt-driven-development": [
        ("incremental-implementation", "Behavioral overlay", "when stakes are high, code is unfamiliar, or a decision is non-trivial", "—"),
        ("spec-driven-development", "Behavioral overlay", "when spec decisions are non-obvious", "—"),
        ("api-and-interface-design", "Behavioral overlay", "when interface contracts are hard to reverse", "—"),
        ("code-review-and-quality", "Peer", "doubt-driven-development reviews in-flight decisions; code-review-and-quality reviews completed code", "—"),
    ],
    "test-driven-development": [
        ("incremental-implementation", "Sequential upstream", "always — tests are written before or alongside each implementation slice", "implementation code"),
        ("code-review-and-quality", "Sequential downstream", "always — tests must pass before code review", "passing test suite"),
        ("debugging-and-error-recovery", "Fallback", "when tests reveal an unexpected failure", "failing test output"),
        ("browser-testing-with-devtools", "Peer", "use browser-testing-with-devtools for runtime DOM/network verification that unit tests cannot cover", "—"),
    ],
    "browser-testing-with-devtools": [
        ("test-driven-development", "Peer", "use for runtime browser verification that complements unit and integration tests", "—"),
        ("frontend-ui-engineering", "Sequential downstream", "run after implementing UI to verify DOM, console errors, and visual output", "browser runtime data"),
        ("debugging-and-error-recovery", "Fallback", "when browser tests reveal unexpected runtime errors", "console logs, network traces"),
        ("shipping-and-launch", "Prerequisite / Gate", "browser tests should pass before any production deploy", "passing browser test run"),
    ],
    "debugging-and-error-recovery": [
        ("test-driven-development", "Fallback", "activated when tests fail unexpectedly", "failing test output"),
        ("incremental-implementation", "Fallback", "activated when an implementation slice breaks the build", "error output"),
        ("test-driven-development", "Sequential downstream", "always — write a regression test after identifying the root cause", "reproduction test + fix"),
        ("browser-testing-with-devtools", "Peer", "use Chrome DevTools for browser-specific runtime debugging", "console logs, network traces"),
    ],
    "code-review-and-quality": [
        ("test-driven-development", "Sequential upstream", "always — tests must pass before review starts", "passing test suite"),
        ("git-workflow-and-versioning", "Sequential downstream", "always — clean commits happen after a passing review", "review sign-off"),
        ("security-and-hardening", "Orchestrator", "invoke for any change touching auth, input handling, or external integrations", "security review findings"),
        ("performance-optimization", "Orchestrator", "invoke when the change touches query paths, loops, or I/O-heavy code", "performance review findings"),
        ("code-simplification", "Peer", "run code-simplification before or during review to reduce noise in the diff", "simplified diff"),
        ("doubt-driven-development", "Peer", "doubt-driven-development reviews in-flight decisions; code-review reviews completed code", "—"),
    ],
    "code-simplification": [
        ("code-review-and-quality", "Peer", "run before code review to reduce diff noise; or as a standalone refactor pass", "simplified code"),
        ("incremental-implementation", "Amplifier", "optional post-pass to simplify the output of a completed implementation slice", "simplified implementation"),
    ],
    "security-and-hardening": [
        ("code-review-and-quality", "Sequential upstream", "invoked by code-review-and-quality for security-sensitive changes", "code diff to review"),
        ("code-review-and-quality", "Sequential downstream", "findings feed back into code-review-and-quality sign-off", "security findings"),
        ("api-and-interface-design", "Behavioral overlay", "security constraints must be applied at interface design time", "—"),
        ("shipping-and-launch", "Prerequisite / Gate", "security review must pass before production deploy", "—"),
    ],
    "performance-optimization": [
        ("code-review-and-quality", "Sequential upstream", "invoked by code-review-and-quality when performance concerns are found", "code diff + profiling data"),
        ("browser-testing-with-devtools", "Peer", "use Chrome DevTools performance panel for frontend-specific profiling", "performance traces"),
        ("shipping-and-launch", "Prerequisite / Gate", "performance baselines should be established before production deploy", "—"),
    ],
    "git-workflow-and-versioning": [
        ("code-review-and-quality", "Sequential upstream", "always — commits happen after a passing code review", "review sign-off"),
        ("ci-cd-and-automation", "Sequential downstream", "always — CI runs are triggered by commits and pushes", "clean commit / PR"),
        ("shipping-and-launch", "Prerequisite / Gate", "clean branch history is required before production deploy", "—"),
    ],
    "documentation-and-adrs": [
        ("spec-driven-development", "Amplifier", "spec decisions that are hard to reverse should be captured as ADRs immediately", "SPEC.md → docs/decisions/*.md"),
        ("shipping-and-launch", "Peer", "run alongside or immediately after launch to document what shipped and why", "docs/decisions/*.md"),
        ("api-and-interface-design", "Sequential downstream", "public API contracts should be documented as ADRs", "API contract → docs/decisions/"),
    ],
    "ci-cd-and-automation": [
        ("git-workflow-and-versioning", "Peer", "CI runs are triggered by git push; the two skills are tightly coupled", "commits / PRs"),
        ("shipping-and-launch", "Sequential upstream", "CI must be green before a production deploy proceeds", "passing CI run"),
        ("test-driven-development", "Amplifier", "CI enforces test-driven-development gates automatically on every push", "—"),
    ],
    "deprecation-and-migration": [
        ("spec-driven-development", "Sequential upstream", "deprecation decisions should be spec'd before any removal work begins", "SPEC.md"),
        ("shipping-and-launch", "Sequential downstream", "migration ships through the same launch checklist as any other change", "migration plan"),
        ("documentation-and-adrs", "Peer", "every deprecation decision should be captured as an ADR", "docs/decisions/*.md"),
        ("git-workflow-and-versioning", "Peer", "use feature flags and atomic commits to keep migration reversible", "—"),
    ],
    "shipping-and-launch": [
        ("git-workflow-and-versioning", "Sequential upstream", "always — clean branch and history required before deploy", "clean branch"),
        ("ci-cd-and-automation", "Sequential upstream", "always — CI must be green before deploy proceeds", "passing CI run"),
        ("security-and-hardening", "Prerequisite / Gate", "security review must be complete before production deploy", "—"),
        ("browser-testing-with-devtools", "Prerequisite / Gate", "browser tests must pass for any UI-facing deploy", "—"),
        ("documentation-and-adrs", "Sequential downstream", "document what shipped and why immediately after launch", "docs/decisions/*.md"),
    ],
    "api-and-interface-design": [
        ("spec-driven-development", "Sequential upstream", "recommended — API contract should derive from the spec", "SPEC.md"),
        ("incremental-implementation", "Sequential downstream", "implementation follows the designed interface contract", "interface contract / schema"),
        ("source-driven-development", "Behavioral overlay", "API patterns must be verified against official framework docs", "—"),
        ("security-and-hardening", "Behavioral overlay", "security constraints (auth, input validation) must be applied at design time", "—"),
        ("documentation-and-adrs", "Sequential downstream", "stable API contracts should be documented as ADRs", "docs/decisions/*.md"),
    ],
    "frontend-ui-engineering": [
        ("planning-and-task-breakdown", "Sequential upstream", "recommended — UI tasks should be broken down before implementation", "tasks/todo.md"),
        ("incremental-implementation", "Peer", "use incremental-implementation for the build loop; use this skill for UI-specific quality standards", "—"),
        ("test-driven-development", "Sequential downstream", "unit and component tests run after each UI slice", "component implementation"),
        ("browser-testing-with-devtools", "Sequential downstream", "runtime DOM and visual verification after UI implementation", "implemented components"),
        ("source-driven-development", "Behavioral overlay", "component and framework patterns must be verified against official docs", "—"),
    ],
    "using-agent-skills": [
        ("all skills", "Orchestrator", "always — this skill governs which other skill is invoked", "user intent → skill selection"),
        ("interview-me", "Sequential downstream", "when user intent is underspecified", "—"),
        ("spec-driven-development", "Sequential downstream", "for any non-trivial build task without a spec", "—"),
    ],
}

# Runtime preambles per skill
PREAMBLES = {
    "interview-me": "Running interview-me to extract intent before any plan, spec, or code. After the interview, I'll route to idea-refine (vague idea) or spec-driven-development (clear requirements).",
    "idea-refine": "Running idea-refine. If intent is unclear, run /interview-me first. After refinement, the next step is spec-driven-development.",
    "spec-driven-development": "Writing the spec before any code. Prerequisites: idea-refine or interview-me are helpful but not required. After spec approval, next step is planning-and-task-breakdown.",
    "planning-and-task-breakdown": "Breaking work into tasks. This requires a spec or clear requirements (run spec-driven-development first if missing). Output feeds incremental-implementation.",
    "context-engineering": "Loading context for the session. Pair with source-driven-development for verified, well-grounded implementation. This improves output quality for any build-phase skill.",
    "source-driven-development": "Grounding implementation in official docs. Pairs with incremental-implementation, api-and-interface-design, and frontend-ui-engineering — invoke those for the build loop.",
    "incremental-implementation": "Building in slices. Prerequisites: planning-and-task-breakdown (tasks/todo.md), context-engineering (recommended). Each slice feeds test-driven-development before expanding.",
    "doubt-driven-development": "Running adversarial fresh-context review. Invoke alongside incremental-implementation, spec-driven-development, or api-and-interface-design when stakes are high.",
    "test-driven-development": "Writing tests before code. Pairs with incremental-implementation (run per slice). If tests fail unexpectedly, route to debugging-and-error-recovery. Passing tests feed code-review-and-quality.",
    "browser-testing-with-devtools": "Runtime browser verification via Chrome DevTools MCP. Prerequisite: Chrome DevTools MCP must be configured. Pairs with test-driven-development; run after frontend-ui-engineering implementation.",
    "debugging-and-error-recovery": "Systematic root-cause investigation. After the fix, write a regression test (test-driven-development) before marking done.",
    "code-review-and-quality": "Five-axis review. Prerequisites: tests must pass (test-driven-development). Orchestrates security-and-hardening and performance-optimization for relevant changes. Passing review feeds git-workflow-and-versioning.",
    "code-simplification": "Simplifying code for clarity. Run before or during code-review-and-quality to reduce diff noise, or as a standalone refactor pass.",
    "security-and-hardening": "Security review. Invoked by code-review-and-quality for security-sensitive changes. Must pass before shipping-and-launch.",
    "performance-optimization": "Performance review. Invoked by code-review-and-quality when bottlenecks are suspected. Pairs with browser-testing-with-devtools for frontend profiling.",
    "git-workflow-and-versioning": "Structuring commits and branches. Prerequisite: code-review-and-quality must pass. Commits trigger ci-cd-and-automation; clean history is required before shipping-and-launch.",
    "documentation-and-adrs": "Recording decisions as ADRs. Pair with spec-driven-development for spec-phase decisions and shipping-and-launch for post-launch documentation.",
    "ci-cd-and-automation": "Automating quality gates. Tightly coupled with git-workflow-and-versioning (CI triggers on push). CI must be green before shipping-and-launch proceeds.",
    "deprecation-and-migration": "Managing deprecation and migration. Start with a spec (spec-driven-development). Every deprecation decision should be captured as an ADR (documentation-and-adrs). Ships through shipping-and-launch.",
    "shipping-and-launch": "Final production launch checklist. Prerequisites: git-workflow-and-versioning (clean branch), ci-cd-and-automation (green CI), security-and-hardening (security review). After launch, run documentation-and-adrs.",
    "api-and-interface-design": "Designing stable interfaces. Derives from spec (spec-driven-development). Apply source-driven-development and security-and-hardening throughout. Output feeds incremental-implementation and documentation-and-adrs.",
    "frontend-ui-engineering": "Building production-quality UI. Feeds test-driven-development and browser-testing-with-devtools. Apply source-driven-development for framework pattern verification.",
    "using-agent-skills": "Skill discovery and lifecycle orchestration. This is the entry point — it maps intent to the right skill and defines the 13-step full lifecycle sequence.",
}


def build_relationships_section(skill_name):
    category = CATEGORY.get(skill_name, "Business Automation")
    lifecycle = LIFECYCLE.get(skill_name, "")
    rels = RELATIONSHIPS.get(skill_name, [])
    preamble = PREAMBLES.get(skill_name, "")

    rows = "\n".join(
        f"| `{r[0]}` | {r[1]} | {r[2]} | {r[3]} |"
        for r in rels
    )

    return f"""
## Skill Relationships

### Category
{category}

### Lifecycle Position
{lifecycle}

### Dependencies
Skills that should run before this one (not hard blockers unless noted as Prerequisite / Gate):
{"None — can be invoked standalone." if not any(r[1] in ("Sequential upstream", "Prerequisite / Gate") for r in rels) else " ".join(f"`{r[0]}`" for r in rels if r[1] in ("Sequential upstream", "Prerequisite / Gate"))}

### Relationships
| Skill | Pattern | Condition | Handoff Artifact |
|---|---|---|---|
{rows}

### Runtime Preamble
{preamble}
"""


HOST_COMPAT_BLOCK = """
## Host Compatibility

### Target Hosts
- Claude Code: yes — installed via `agent-skills@addy-agent-skills` plugin (user scope, globally available)
- Codex/OpenAI: yes — installed via `agent-skills@addy-agent-skills` plugin from the `addy-agent-skills` marketplace

### Tool Mapping
| Claude Code | Codex |
|---|---|
| `Read` / `Grep` / `Glob` | shell reads / `rg` |
| `Edit` / `MultiEdit` | `apply_patch` |
| `Bash` | shell command |
| `AskUserQuestion` | concise chat question |
| `Task` / subagent | main-thread execution |

### Source / Tool Order
1. Read this SKILL.md and any referenced supporting files first.
2. Use local repo artifacts and prior run files before any external lookup.
3. Use GBrain or durable memory when available for recurring research topics.
4. Use official documentation MCPs or preferred research plugins before generic web search.
5. Use generic web search only as fallback or for official-source verification.
"""


def apply_fixes():
    skills = sorted(os.listdir(SKILLS_DIR))
    for skill_name in skills:
        skill_path = os.path.join(SKILLS_DIR, skill_name, "SKILL.md")
        if not os.path.isfile(skill_path):
            continue

        with open(skill_path, "r") as f:
            content = f.read()

        # Skip if sections already present
        if "## Skill Relationships" in content:
            print(f"SKIP {skill_name} — Skill Relationships already present")
            continue

        relationships = build_relationships_section(skill_name)
        content = content.rstrip() + "\n" + relationships + HOST_COMPAT_BLOCK
        with open(skill_path, "w") as f:
            f.write(content)
        print(f"  OK {skill_name}")


if __name__ == "__main__":
    apply_fixes()
    print("\nDone.")
