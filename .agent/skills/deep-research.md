# Skill: Deep Research

> **Universal** — Works across all vendors (Gemini, Claude, Codex)

## Purpose

Execute comprehensive research on topics to update project knowledge base.

## Usage

### Ad-hoc Research
Ask the agent to research a specific topic. Results are saved to `docs/research/`.

### Scheduled Research (via workflow)
Use the `/deep-research-update` workflow to research all configured topics.

## Process

1. Define research query with clear scope
2. Execute research using available tools (web search, documentation)
3. Save results to `docs/research/{DATE}_{topic}.md`
4. Update `docs/research/INDEX.md` if it exists
5. Present executive summary to user

## Output Format

```markdown
# Research: {topic}

_Date: YYYY-MM-DD | Source: {vendor}_

## Executive Summary
- Key finding 1
- Key finding 2

## Detailed Findings
[Full research content with sections]

## Sources
- [Source 1](url)
- [Source 2](url)

## Recommendations
- How to apply findings to current project
```

## Configuration

Research topics can be defined in `config/research_topics.yaml` for scheduled updates.
