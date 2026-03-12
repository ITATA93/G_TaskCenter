---
description: Flujo de Auditoría Cognitiva (Skills, Prompts y Workflows)
---
# Workflow: Cognitive Audit Pipeline

Este flujo debe ejecutarse para validar la salud "cognitiva" del ecosistema, evaluando la redundancia, seguridad e integridad de los Agentes, Prompts, Skills y Workflows. Se aplica principalmente durante la ejecución de los ciclos de mejora, o cuando se añade una nueva herramienta.

## Paso 1: Evaluación de Prompts y Perfiles de Agentes (Adversarial Review)

1. Invoca al subagente `skeptic` o `reviewer` para que audite los archivos maestros de perfiles: `GEMINI.md`, `CLAUDE.md` y `AGENTS.md`.
2. **Validación de Reglas Absolutas**: El revisor debe confirmar que los perfiles prohíben explícitamente operaciones destructivas no autorizadas (ej. DELETE, DROP sin HITL) y la alteración de bases de datos.
3. **Delegación Estructurada**: Se debe validar que los agentes sigan el protocolo de delegación (Clasificador de Complejidad Nivel 1, 2, 3).
4. El sistema evalúa si las penalizaciones están documentadas para la inyección de directivas.

## Paso 2: Auditoría de Skills (Herramientas)

1. Ejecuta el análisis estático (`scripts/audit_suite.py --aspect cognitive`) o invoca al `skill-pool-manager` sobre los directorios `.subagents/skills/` y la biblioteca externa.
2. **Control de Idempotencia y Secretos**: Verifica que ninguna skill exponga o asigne contraseñas.
3. **Validación de Metadata**: Todas las herramientas deben contar con un documento `SKILL.md` (o metadata en yaml) debidamente diligenciado.

## Paso 3: Análisis Estático de Workflows

1. Analiza todos los flujos ubicados en `.agent/workflows/` y `.gemini/workflows/`.
2. **HITL (Human-in-the-Loop)**: Asegura que todo flujo con operaciones mutágenas contenga controles manuales en la vida real.
3. **Etiquetas (Tags)**: Identifica marcadores de automatización seguros (`// turbo`, `// turbo-all`).
4. **Trazabilidad**: Todo flujo debe producir un artefacto o actualizar logísticas como `DEVLOG.md`.

## Paso 4: Cierre y Consolidación

1. Consolida los hallazgos con un grade en `docs/audit/cognitive_audit_[timestamp].md`.
2. Emplea `/project-improvement-loop` para delegar automáticamente las correcciones recomendadas por los hallazgos en la evaluación de los perfiles.
