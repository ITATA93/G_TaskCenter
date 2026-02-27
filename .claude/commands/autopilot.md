Execute a mission in full Autopilot mode — zero user intervention.

You are now in **AUTOPILOT MODE**. Follow the workflow defined in
`.agent/workflows/autopilot.md` and enforce all guardrails from
`.agent/rules/autopilot-guardrails.md`.

## IMPORTANT: Read these files FIRST
1. `.agent/workflows/autopilot.md` — execution protocol
2. `.agent/rules/autopilot-guardrails.md` — safety boundaries

## Your mission
{{input}}

## Execution Protocol

### Step 1: Parse & Announce
Parse the mission above into the structured mission YAML format.
Print the AUTOPILOT ENGAGED banner with mission summary.

### Step 2: Pre-Flight
- Read `docs/TODO.md` and first entry of `docs/DEVLOG.md`
- Stash any uncommitted work: `git stash push -m "autopilot-safeguard"`
- Create branch: `git checkout -b autopilot/<slug-from-goal>`
- Explore codebase to identify scope
- Generate internal execution plan

### Step 3: Execute Autonomously
- Make ALL changes without asking the user
- Use the Decision Engine for any ambiguity (prefer reversible, minimal, conventional)
- Auto-commit after each logical unit on the autopilot/* branch
- Run tests after changes; auto-fix failures (max 2 retries)
- Monitor constraints continuously
- If a kill switch triggers → STOP immediately, go to Step 5

### Step 4: Post-Flight
- Run final tests
- Generate the full Post-Flight Report (format in autopilot.md)
- Print it to the user
- Append abbreviated session entry to `docs/DEVLOG.md`
- Tell user how to review: `git diff main...autopilot/<slug>`

### Step 5: Abort (only if needed)
- Commit WIP with message explaining why
- Generate Post-Flight Report with ABORTED status
- Print recovery instructions

## Rules During Execution
- Do NOT ask the user any questions — use the Decision Engine
- Do NOT modify CLAUDE.md, GEMINI.md, or AGENTS.md
- Do NOT push to main/master under any circumstances
- Do NOT run database destructive operations
- Do NOT use --force on any command
- DO commit frequently on the autopilot/* branch
- DO log every decision internally for the post-flight report
- DO stop if the same error occurs 3 times
