# Skill: Project Initialization

> **Universal** — Works across all vendors (Gemini, Claude, Codex)

## Purpose

Initialize new projects with standardized Antigravity structure.

## Standard Structure

```
project-name/
├── .agent/
│   ├── rules/              ← Universal rules (all vendors read)
│   │   ├── project-rules.md
│   │   └── session-protocol.md
│   ├── skills/             ← Universal skills
│   └── workflows/          ← Universal workflows
├── .gemini/                ← Gemini-specific config
├── .claude/                ← Claude-specific config
├── .codex/                 ← Codex-specific config
├── .subagents/
│   └── manifest.json       ← Sub-agent configuration
├── src/                    ← Source code
├── tests/                  ← Tests
├── docs/
│   ├── DEVLOG.md           ← Session diary
│   ├── TODO.md             ← Task tracker
│   ├── architecture/       ← Design docs
│   ├── standards/          ← Output governance, etc.
│   └── research/           ← Deep research results
├── scripts/                ← Utility scripts
├── config/                 ← Configurations
├── GEMINI.md               ← Gemini instructions
├── CLAUDE.md               ← Claude instructions
├── AGENTS.md               ← Agent dispatch guide
├── CHANGELOG.md
├── .gitignore
├── .env.example
└── README.md
```

## Post-Init Checklist

1. Configure `.env` from `.env.example`
2. Review and customize `docs/TODO.md`
3. Run first session — agent will auto-read TODO+DEVLOG
