# Codex CLI 2026 - Capacidades y Limitaciones

## Resumen

Codex CLI (OpenAI) en 2026 es un CLI **completamente funcional** con una única limitación significativa: **no tiene Task tool para subagentes paralelos**.

---

## Comparación de Capacidades (2026 Actualizado)

| Característica | Claude Code | Gemini CLI | Codex CLI |
|----------------|-------------|------------|-----------|
| Task Tool (Subagentes) | ✅ Sí (10+) | ❌ No | ❌ No |
| Ejecución Paralela | ✅ Sí | ❌ No | ❌ No |
| **Integración MCP** | ✅ Sí | ❌ No | ✅ **Sí** |
| **Sistema de Skills** | ✅ Sí | ✅ Sí | ✅ **Sí** |
| **Web Search** | ✅ Sí | ✅ Sí | ✅ **Sí** |
| **Deep Research** | ✅ Pro | ❌ No | ✅ **Pro** |
| Context Window | 200K | 1M | 128K-256K |
| Modelos | 3 tiers | 2 tiers | 2 (effort+model) |
| Modo | Full | Partial | **Casi Full** |

---

## Única Limitación Real

### Sin Task Tool (Subagentes Paralelos)

**Claude Code:**
```
[Main Agent] → [Subagent 1] ─┐
            → [Subagent 2] ──┼─→ [Aggregated Result]
            → [Subagent 3] ─┘
            (paralelo, 10+ agentes)
```

**Codex CLI:**
```
[Main Agent] → [Task 1] → [Task 2] → [Task 3] → [Result]
              (secuencial, mismo agente)
```

**Impacto:** Para workflows que requieren múltiples agentes simultáneos, Codex toma más tiempo al ejecutar secuencialmente.

---

## Capacidades Completas (2026)

### ✅ MCP Integration

Codex 2026 soporta MCP (Model Context Protocol) servers:

```toml
# ~/.codex/config.toml
[mcp_servers.filesystem]
command = "npx"
args = ["-y", "@anthropic-ai/mcp-server-filesystem", "/path/to/dir"]

[mcp_servers.github]
command = "npx"
args = ["-y", "@anthropic-ai/mcp-server-github"]
env = { GITHUB_TOKEN = "your-token" }
```

### ✅ Skills System

Codex soporta Agent Skills desde enero 2026:

```bash
# Skills via prompt
codex exec "Use the code-review skill to analyze src/"

# Skills en archivos
~/.codex/skills/
├── code-review.md
├── test-generator.md
└── doc-writer.md
```

### ✅ Web Search

Integrado por defecto, permite búsquedas web en tiempo real:

```bash
codex exec "Search for the latest React 19 features and summarize"
```

### ✅ Deep Research (Pro)

Disponible con licencia Pro:

```bash
# Activa modo deep research
codex exec --deep-research "Analyze security best practices for OAuth 2.1"
```

---

## Modelos Disponibles

### Standard
- **gpt-5.2-codex**: Modelo base, excelente para desarrollo

### Pro License
- **gpt-5.1-codex-max**: Contexto extendido, razonamiento mejorado

### Effort Levels
| Effort | Uso | Tokens Reasoning |
|--------|-----|------------------|
| `xhigh` | Arquitectura, análisis complejo | Máximo |
| `high` | Implementación, tests | Alto |
| `medium` | Tareas estándar | Medio |
| `low` | Fixes rápidos, docs | Mínimo |

---

## Invocación

### Comando Básico
```bash
codex exec --dangerously-bypass-approvals-and-sandbox "prompt"
```

### Con Effort Level
```bash
CODEX_MODEL_REASONING_EFFORT=high codex exec \
  --dangerously-bypass-approvals-and-sandbox \
  "Analiza este código..."
```

### Via Dispatcher (Multi-vendor)
```bash
./.subagents/dispatch.sh code-analyst "Analiza src/" codex
```

### Con MCP Server
```bash
# Asegurar config.toml tiene los servers configurados
codex exec "List files in the project using MCP filesystem"
```

---

## Pro License Features

| Feature | Standard | Pro |
|---------|----------|-----|
| Deep Research | ❌ | ✅ |
| GPT-5.1-Codex-Max | ❌ | ✅ |
| Extended Context | 128K | 256K |
| Priority Queue | ❌ | ✅ |
| Citations | Basic | Full |

---

## Recomendaciones de Uso

### ✅ Usar Codex para:
- Tareas de desarrollo estándar
- Análisis de código con MCP integration
- Documentación y generación de tests
- Research con web search
- Cualquier tarea que no requiera subagentes paralelos

### ⚠️ Considerar alternativas cuando:
- Se necesitan 5+ tareas simultáneas
- Code reviews con múltiples perspectivas paralelas
- CI/CD pipelines con ejecución masiva paralela

### 🔄 Enfoque Híbrido:
- Codex para análisis inicial (MCP + web search)
- Claude para ejecución paralela cuando se necesite
- Codex para documentación final

---

## Troubleshooting

### Error: "codex: command not found"
```bash
npm install -g @openai/codex
```

### Error: MCP server not found
```bash
# Verificar config.toml
cat ~/.codex/config.toml

# Instalar MCP server
npx -y @anthropic-ai/mcp-server-filesystem
```

### Habilitar Deep Research (Pro)
```bash
# Verificar licencia
codex --version --license

# Si no tienes Pro, upgradar en platform.openai.com
```

---

## Referencias

- [OpenAI Codex CLI Documentation](https://platform.openai.com/docs/codex)
- [MCP Protocol Specification](https://modelcontextprotocol.io)
- [Antigravity Workspace](..)
