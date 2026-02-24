# G_TaskCenter — Personal Task Orchestration

> Satellite project in the Antigravity ecosystem.
> **Domain:** `03_PERSONAL` | **Orchestrator:** GEN_OS | **Prefix:** G_

## Proposito

Hub centralizado de productividad personal. Orquesta tareas, calendarios y
bandejas de entrada entre Gmail, Notion, Outlook y n8n, ofreciendo una vista
unificada mediante servidores MCP locales.

## Arquitectura

```text
G_TaskCenter/
  src/
    server.py           # Servidor MCP oficial (tool: list_unified_tasks)
    sync_engine.py      # Motor de sincronizacion entre plataformas
    models.py           # Modelos de datos unificados
    integrations/       # Modulos por plataforma
      gmail.py          # Lectura de tareas desde Gmail
      notion.py         # Sync bidireccional con Notion
      outlook.py        # Tareas y calendario Outlook
      n8n.py            # Integracion con workflows n8n
  scripts/
    mcp_server.py       # Servidor MCP alternativo (FastMCP)
  n8n_workflows/        # Definiciones de workflows n8n
    gmail_to_notion.json
    outlook_to_notion.json
    error_notifier.json
  docs/                 # Documentacion y estado
```

Los servidores MCP corren localmente (sidecar) y exponen herramientas de lectura
y sincronizacion. Las credenciales se manejan exclusivamente via `.env`.

## Uso con Gemini CLI

```bash
# Dispatch subagente
bash .subagents/dispatch.sh reviewer "Audit integrations"
bash .subagents/dispatch-team.sh code-and-review "Review sync engine"

# Operaciones permitidas sin HITL:
#   - Lectura/escritura a servicios via MCP locales
#   - Ejecucion de scripts de automantenimiento
# Operaciones que requieren HITL:
#   - Modificacion de permisos o acceso a archivos
```

## Scripts

```bash
# Servidor MCP oficial
python src/server.py

# Servidor MCP alternativo (FastMCP)
python scripts/mcp_server.py

# Importar workflows n8n
# Los JSON en n8n_workflows/ se importan directamente en la instancia n8n
```

## Configuracion

```bash
cp .env.example .env       # Configurar credenciales
pip install -r requirements.txt   # Instalar dependencias
python src/server.py       # Iniciar servidor MCP
```

**Variables requeridas** (ver `.env.example`):

```env
GMAIL_CREDENTIALS_PATH=...
NOTION_API_KEY=...
OUTLOOK_CLIENT_ID=...
OUTLOOK_CLIENT_SECRET=...
N8N_BASE_URL=...
N8N_API_KEY=...
```

**Requisitos:** Python >= 3.11, dependencias en `requirements.txt`, cuentas
configuradas en Gmail/Notion/Outlook, instancia n8n (opcional).
