# Skill: Project Initialization

## Purpose
Initialize new projects with standardized structure and configuration.

## Usage
```bash
gemini /project:init "project-name" --type={type}
```

## Supported Project Types
- **fullstack**: Full-stack web application
- **api**: Backend API only
- **frontend**: Frontend only
- **cli**: Command-line tool
- **library**: Reusable library/package

## Generated Structure
```
project-name/
├── .gemini/
│   ├── agents/          ← Project-specific agents
│   ├── commands/        ← Custom commands
│   ├── rules/           ← Project rules
│   ├── workflows/       ← Project workflows
│   ├── scripts/         ← Utility scripts
│   └── settings.json
├── .claude/
│   ├── commands/        ← Claude slash commands
│   └── skills/          ← Claude skills
├── .agent/
│   ├── rules/           ← Agent behavior rules
│   └── workflows/       ← Agent workflows
├── .subagents/
│   └── manifest.json    ← Sub-agent configuration
├── src/                 ← Source code
├── tests/               ← Tests
├── docs/                ← Documentation
├── scripts/             ← Build/deploy scripts
├── config/              ← Configurations
├── GEMINI.md            ← Gemini instructions
├── CLAUDE.md            ← Claude instructions
├── CHANGELOG.md         ← Version history
├── .gitignore
├── .env.example
└── README.md
```

## Post-Init Tasks
1. Configure .env from .env.example
2. Run /session:start
3. Review TODO.md for initial tasks
