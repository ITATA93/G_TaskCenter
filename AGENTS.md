# AGENTS.md — G_TaskCenter

## Subagent Manifest
Agents for this project are defined in `.subagents/manifest.json`.

## Available Agents

| ID | Name | Vendor Pref | Risk Tier | Approval |
|----|------|------------|-----------|----------|
| lead-orchestrator | Master Orchestrator | gemini | high | yes |
| reviewer | Audit & Security Reviewer | claude | medium | no |
| domain-builder | Domain Code Engineer | gemini | high | yes |
| support | Documentation Writer | gemini | low | no |
| deep-researcher | Deep Research Specialist | gemini | low | no |
| skill-pool-manager | Skill Pool Manager | claude | medium | no |
| skeptic | Adversarial Critic | claude | low | no |

## Teams

| Team | Agents | Mode | Use Case |
|------|--------|------|----------|
| full-audit | reviewer, lead-orchestrator | sequential | Full project audit with orchestrator oversight |
| code-and-review | domain-builder, reviewer | sequential | Generate code then review for quality and security |
| research-and-document | deep-researcher, support | sequential | Research a topic then document findings |
| adversarial-review | domain-builder, skeptic | sequential | Generate code then critic validates |

## Dispatch
```bash
bash .subagents/dispatch.sh <agent-id> "<prompt>"
bash .subagents/dispatch-team.sh <team-id> "<prompt>"
```
