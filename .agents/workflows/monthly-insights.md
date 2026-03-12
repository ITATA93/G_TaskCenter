---
description: Monthly usage insights review and workflow optimization cycle
---

# Monthly Insights Review Workflow

Leverage Claude Code's `/insights` command to perform a monthly review of development patterns and optimize workflows.

## When to Use
- Last workday of each month
- After completing a major project milestone
- When team velocity feels suboptimal

## Steps

1. **Generate insights report**
   ```
   /insights
   ```
   This analyzes the last 30 days of Claude Code usage across all sessions.

2. **Save the generated report**
   - The HTML report is auto-generated
   - Copy key findings to `docs/audit/insights-YYYY-MM.md`

3. **Analyze key metrics**
   - Tool usage patterns (which tools are used most/least)
   - Session duration distribution
   - Model distribution (opus vs sonnet vs haiku usage)
   - Common error patterns and retries

4. **Identify optimization opportunities**
   - Friction points: recurring issues that slow down work
   - Underused features: capabilities not being leveraged
   - Over-reliance patterns: tasks better suited for different agents/tools

5. **Create action items**
   - Update `docs/TODO.md` with workflow improvements
   - Modify agent configurations in `.subagents/manifest.json` if needed
   - Update `CLAUDE.md` or `GEMINI.md` with new patterns discovered

6. **Compare with previous month** (if available)
   - Check `docs/audit/insights-*.md` for trends
   - Validate that previous month's action items were effective

## Output
- `docs/audit/insights-YYYY-MM.md` — Monthly insights summary
- Updated `docs/TODO.md` — New optimization tasks
- Updated configurations if patterns suggest changes
