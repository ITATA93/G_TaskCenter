---
id: IDX-ROOT-001
titulo: Knowledge Vault Index
proyecto: AG_Plantilla
ultima_actualizacion: 2026-02-03
---

# 🏥 Knowledge Vault Pattern

> Bóveda de Conocimiento Estructurada para Documentación de Alta Densidad.

Este patrón permite gestionar grandes volúmenes de información (ej. Hospitales, Legales) descomponiéndola en átomos navegables por IA.

## 1. Estrategia de "Documentos Gemelos" (Shadow Twins)

Para manejar PDFs, Imágenes y Scans, utilizamos una estrategia dual:

### A. Repositorio de Referencia (La Fuente Legal)
*   **Ubicación**: `docs/references/`
*   **Contenido**: Archivos binarios originales (`.pdf`, `.jpg`, `.docx`).
*   **Uso**: Solo para humanos o auditoría legal. El agente **NO** lee esto rutinariamente.

### B. Repositorio Ágil (La Memoria del Agente)
*   **Ubicación**: `docs/knowledge_vault/`
*   **Contenido**: Markdown puro (`.md`) estructurado semánticamente.
*   **Transformación**: Cada binario se convierte en un MD que resume y estructura la data clave.

#### Ejemplo de Gemelos
| Tipo            | Archivo                                               | Contenido                             |
| :-------------- | :---------------------------------------------------- | :------------------------------------ |
| **Referencia**  | `docs/references/manual_uci_2025.pdf`                 | 500 páginas, imágenes, firma digital. |
| **Agile Vault** | `docs/knowledge_vault/infraestructura/uci_resumen.md` | Texto extraído, tablas clave, reglas. |

## 2. Estructura de Metadatos (Vinculación)

El archivo en el Vault debe "apuntar" a su fuente original mediante Frontmatter:

```yaml
---
id: KNOWLEDGE-001
titulo: Resumen Infraestructura UCI
tipo: extracted_knowledge
source: ../../references/manual_uci_2025.pdf
checksum: a1b2c3d4
---
```

## 3. Mapa de Navegación (Indices)

Cada directorio debe contener un `README.md` que actúe como mapa:

```markdown
# Índice de Infraestructura
- [UCI](./uci_resumen.md) (Extracto de manual 2025)
- [Quirófanos](./quirofanos_specs.md)
```

## 4. Reglas de Atomicidad

1.  **Un Concepto = Un Archivo**: No copies el PDF entero a un MD gigante. Divídelo por temas.
2.  **Imágenes**: Si el PDF tiene un diagrama crítico, extrae la imagen a `docs/knowledge_vault/_assets/` e incrustala en el MD.
3.  **Tablas**: Convierte tablas de imagen a Markdown Tables siempre que sea posible.
