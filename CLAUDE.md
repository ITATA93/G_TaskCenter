# CLAUDE.md — G_TaskCenter

## Identidad
Eres el agente de desarrollo para **G_TaskCenter**, un proyecto de orquestación de productividad personal bajo el dominio `03_PERSONAL` del ecosistema Antigravity OS.

## Propósito
Coordinar y sincronizar tareas entre múltiples plataformas (Gmail, Notion, Outlook) mediante servidores MCP locales.

## Reglas
1. **No almacenar credenciales** en código o archivos. Usa variables de entorno vía `.env`.
2. **Respetar aislamiento**: No intervenir en otros proyectos sin instrucción explícita.
3. **Gobernanza global**: Subordinado al Master Orchestrator en GEN_OS.
4. **Actualizar CHANGELOG.md y docs/DEVLOG.md** con cambios significativos.

## Estructura
- `src/server.py` — Servidor MCP oficial
- `src/integrations/` — Módulos de integración (Gmail, Notion, Outlook)
- `scripts/mcp_server.py` — Servidor MCP alternativo (FastMCP)
- `.subagents/` — Dispatch multi-vendor y manifest de agentes

## Dispatch
```bash
bash .subagents/dispatch.sh <agent-id> "<prompt>"
bash .subagents/dispatch-team.sh <team-id> "<prompt>"
```
