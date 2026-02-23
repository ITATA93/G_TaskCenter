# Agent Output Governance Standard

> **Version:** 2.0 | **Applies to:** All AI agents in Antigravity projects

---

## File Creation Rules

1. **NEVER** create files in project root (except standard: GEMINI.md, CLAUDE.md, AGENTS.md, CHANGELOG.md, README.md)
2. **NEVER** create ad-hoc log files — use `docs/DEVLOG.md` (append mode only)
3. **NEVER** create TODO/task files outside `docs/TASKS.md`
4. **NEVER** create temporary analysis files — use Knowledge Items or the appropriate `docs/` subdirectory
5. **ALWAYS** check `docs/standards/output_governance.md` before creating any file

## Output Routing Table

| Output Type         | Location                               | Naming Convention          |
| ------------------- | -------------------------------------- | -------------------------- |
| Audit report        | `docs/audit/YYYY-MM-DD_<type>_<scope>_<vendor>-<model>.md` | AG-AUDIT-STD v1.0 |
| Implementation plan | `docs/plans/<name>.md`                 | Max 5 active               |
| Research            | `docs/research/<name>.md`              | Update INDEX.md            |
| ADR                 | `docs/decisions/ADR-NNN-<title>.md`    | Sequential number          |
| Session log         | `docs/DEVLOG.md` (append)              | See format below           |
| Task/TODO           | `docs/TASKS.md` Local section          | Blocker/InProgress/Backlog |
| Knowledge           | Antigravity KIs                        | Via KI system              |
| Skills              | `.gemini/skills/` or `.claude/skills/` | SKILL.md format            |
| Workflows           | `.agent/workflows/`                    | Frontmatter + steps        |
| Config              | `config/`                              | YAML/JSON only             |

## Forbidden Outputs

| ❌ Never Create           | ✅ Instead                      |
| ------------------------ | ------------------------------ |
| `analysis_*.md` in root  | → `docs/research/`             |
| `report_*.md` in root    | → `docs/audit/`                |
| `plan_*.md` in root      | → `docs/plans/`                |
| `log_*.md` anywhere      | → Append to `docs/DEVLOG.md`   |
| `TODO_*.md` or `TODO.md` | → Update `docs/TASKS.md` Local |
| `notes_*.md` anywhere    | → Knowledge Item               |
| `temp_*.md` anywhere     | → `scripts/temp/` (gitignored) |

## Archival Policy

- Audit reports > 30 days → `docs/audit/_archive/`
- Completed plans → DELETE (or archive if ADR-worthy)
- Done TODOs → Remove after 7 days in "Done" section
- Max 5 active plans at any time

## Audit Report Standard (AG-AUDIT-STD v1.0)

### File Naming Convention

```
YYYY-MM-DD_<type>_<scope>_<vendor>-<model>.md
```

All lowercase, hyphens within segments, underscores between segments.

**Type codes:**

| Code | Meaning | Alignment |
|------|---------|-----------|
| `full` | Full/comprehensive audit | ISO 19011 Clause 6 |
| `sec` | Security audit | NIST CSF / SOC 2 |
| `norm` | Normalization/compliance | ISO 19011 Clause 6.4.4 |
| `perf` | Performance audit | ISACA Performance |
| `code` | Code review/quality | ISACA IS audit |
| `infra` | Infrastructure audit | SOC 2 Availability |
| `data` | Data quality/integrity | SOC 2 Processing Integrity |
| `tools` | Tools/dependency audit | Supply chain |
| `plan` | Audit-derived plan | Post-audit action plan |

**Vendor-model codes:**

| Code | Vendor / Model |
|------|----------------|
| `claude-opus46` | Claude Opus 4.6 |
| `claude-sonnet46` | Claude Sonnet 4.6 |
| `claude-haiku45` | Claude Haiku 4.5 |
| `gemini-flash20` | Gemini 2.0 Flash |
| `gemini-pro25` | Gemini 2.5 Pro |
| `codex` | OpenAI Codex |
| `team` | Multi-agent team review |
| `human` | Manual human audit |

**Scope codes:**

| Code | Meaning |
|------|---------|
| `ecosystem` | All projects |
| `core` | 00_CORE domain |
| `hp` | 01_HOSPITAL_PRIVADO domain |
| `hpub` | 02_HOSPITAL_PUBLICO domain |
| `{project-id}` | Specific project (e.g., `ag-consultas`) |

### Required YAML Frontmatter

Every audit report MUST include YAML frontmatter with:
- `audit_id`, `title`, `date`, `timestamp`
- `agent` block: `vendor`, `model`, `interface`, `agent_name`, `team_mode`
- `scope` block: `type`, `domain`, `projects`, `criteria`
- `severity_summary`: `critical`, `high`, `medium`, `low`, `info` counts
- `overall_score` (0-100), `overall_grade` (A-F), `status`, `language`

### Canonical Template

- **Source of truth:** `AG_Plantilla/_template/workspace/docs/audit/_templates/audit-report.md`
- **Local copy:** Each project's `docs/audit/_templates/audit-report.md`

### Audit Directory Structure

```
docs/audit/
  _archive/           # Reports older than 30 days
  _templates/         # audit-report.md template
  INDEX.md            # Auto-maintained audit index
  <active reports>    # Named per convention above
```

### Severity Classification (CVSS v3.1)

| Level | CVSS Range | Action Deadline |
|-------|------------|-----------------|
| Critical | 9.0 - 10.0 | Immediate |
| High | 7.0 - 8.9 | 24 hours |
| Medium | 4.0 - 6.9 | 7 days |
| Low | 0.1 - 3.9 | 30 days |
| Info | 0.0 | None |

### Audit Categories

| Code | Category | Description |
|------|----------|-------------|
| `SEC` | Security | Credentials, secrets, access control, injection, dependencies |
| `GOV` | Governance | Output governance compliance, naming, structure |
| `QA` | Code Quality | Linting, tests, coverage, type safety, dead code |
| `ARCH` | Architecture | Structure, separation of concerns, dependencies |
| `DATA` | Data Integrity | Validation, schema compliance, FHIR compliance |
| `OPS` | Operations | CI/CD, deployment, monitoring, logging |
| `AGENT` | Agent Config | Manifest compliance, dispatch, skills, vendor parity |
| `DOC` | Documentation | README, CHANGELOG, DEVLOG, API docs |

---

## DEVLOG.md Session Entry Format

```markdown
## YYYY-MM-DD (Session: <Topic>)

### Accomplished
- Concrete list of things done

### Decisions
- Key decisions made and rationale

### Metrics
- Files changed: N | Lines: +X/-Y
```

> **No "Next Steps" section.** All pending work goes to `docs/TASKS.md`.
