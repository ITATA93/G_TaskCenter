---
description: Mixture of Experts (MoE) consensus panel for complex architecture and design questions.
---
# Consensus Panel Workflow

Executes a turn-based discussion between Gemini, Claude, and Codex to arrive at a highly refined, peer-reviewed technical solution.

## How it works

1. **Requirements Analyst (Gemini)**: Elaborates the user's request into a detailed technical requirement.
2. **The Architect (Gemini)**: Proposes a high-level architectural design and strategic approach.
3. **The Critic (Claude)**: Reviews the requirement and architecture, finds flaws, security vulnerabilities, and suggests improvements.
4. **The Implementer (Codex)**: Solves technical details, providing code snippets or library configurations that address the critique.
5. **The Master Orchestrator (Gemini)**: Synthesizes a final, unified, and highly polished Implementation Plan based on the entire panel's outputs.

## Usage

Use the `run-consensus.ps1` script, passing your prompt as an argument.

// turbo
1. Execute the panel:
```powershell
.\scripts\run-consensus.ps1 -Topic "Your complex question or architecture request here"
```

2. Review the resulting markdown file generated in `docs/temp/consensus-YYYYMMDD-HHmmss.md`.
