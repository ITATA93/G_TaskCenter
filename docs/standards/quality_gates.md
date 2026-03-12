---
title: GEN_OS Quality Gates and Agentic Quality Standard
depends_on:
  - docs/standards/mcp_security.md
  - docs/standards/supply_chain_governance.md
impacts:
  - docs/standards/supply_chain_governance.md
  - .github/workflows/ci.yml
---

# GEN_OS Quality Gates and Agentic Quality Standard

Version: 1.1.0  
Reference date: 2026-02-22

This standard defines high quality controls for the agentic system while preserving autonomia/autonomy.

## 1. Mandatory Test Pyramid (L0-L3)

1. `L0` Schema and static validation
- Manifest, workflow specs, and core config files must be valid and consistent.
- Frontmatter cross-references must be coherent.

2. `L1` Unit tests
- Core scripts and critical helper contracts must be covered by deterministic unit tests.
- Every new quality control added to the audit suite should include at least one direct unit test.

3. `L2` Integration tests
- MCP servers and shared infra connectors must be validated against contract-level behavior.
- Dispatcher and routing paths should be tested across happy-path and controlled-failure scenarios.

4. `L3` Security and adversarial tests
- Secret leakage checks, prompt-injection resistance, and permission boundaries are required.
- High-risk execution paths must be documented in the risk register and compensated with controls.

5. `L4` Semantic and Functional Validation (Agentic Self-Improvement)
- Apps must not just compile; they must make logical sense. Prevent "empty designs" or "meaningless workflows".
- Requires validation by the `skeptic` (Adversarial Critic) or `visual-verifier` agents before considering the task complete.
- Architectural decisions must be grounded in domain reality, updating project System Prompts (e.g., GEMINI.md/CLAUDE.md) when conceptual errors are found to prevent recurrence.

## 2. Quality Gates for Merge and Release

- `G1` Governance gate: dictionary completeness + output governance + docs consistency.
- `G2` Runtime gate: scripts compile, tests pass, workflows validate.
- `G3` Agentic gate: manifest contract, dispatcher guardrails, and docs-runtime parity pass.
- `G4` Security gate: no secret exposure and no undocumented bypass path.
- `G5` Supply chain gate: package pinning completeness and typosquatting defense.
- `G6` Semantic gate: functional coherence verified by adversarial/visual agents (prevents 'empty' or 'illogical' apps).

Any failure in `G1` to `G6` blocks release candidates.

## 3. HITL and Autonomy Balance

- HITL is mandatory for destructive operations and high-risk irreversible changes.
- Agent autonomy is preserved for low-risk and pre-authorized operations.
- `needs_approval` in agent manifest is the contract boundary for runtime approval posture.
- Permission allowlists must be synchronized and audited (`permission_sync.py` + local settings profile).

## 4. Documentation Reflects Runtime Behavior

Documentation files that describe agents, scripts, and controls must reflect current runtime behavior.

Minimum parity rules:
- `docs/library/agents.md` must match runtime IDs from `.subagents/manifest.json`.
- `docs/library/scripts.md` cannot describe implemented scripts as placeholders/stubs.
- `docs/library/audit_controls.md` must list active runtime risk controls and compensating controls.

## 5. Continuous Audit Cadence

- Run `audit_suite.py --aspect full` at least once per working day with report output.
- Run focused checks after targeted changes:
  - `--aspect agents` and `--aspect runtime` after dispatch or manifest updates.
  - `--aspect documentation` after editing `docs/library/*` or standards.
  - `--aspect mcp` after MCP server or MCP test updates.
  - `--aspect security_dynamic` after security control changes.
  - `--aspect supply_chain` after dependency manifest or lock updates.
  - `--aspect infra_health` after infrastructure deploys or tunnel changes.
- Keep audit reports versioned in `docs/audit/` and indexed in `docs/audit/INDEX.md`.

## CI Pipeline

The quality gates are enforced automatically via GitHub Actions (`.github/workflows/ci.yml`):

| Gate | Name | Triggers | Tests |
|------|------|----------|-------|
| G1 | Governance | push, PR | `dictionary_completeness.py`, `doc_governance.py` |
| G2 | Runtime | after G1 | `pytest -m "not slow and not integration and not adversarial"` |
| G3 | Integration | after G2 | `pytest -m "integration"`, `audit_suite.py --aspect full` |
| G4 | Security | after G2 | `pytest -m "adversarial"`, `secret_scanner.py`, `supply_chain_audit.py` |

G3 and G4 run in parallel after G2 passes. All gates must pass for a merge to master.

## MCP Security

All MCP tool functions are protected by the security middleware (`@secured_tool` decorator). See `docs/standards/mcp_security.md` for the authorization matrix, audit trail schema, and rate limiting policy.
