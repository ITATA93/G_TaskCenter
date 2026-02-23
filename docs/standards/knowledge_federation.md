# Estándar de Federación de Conocimiento (Knowledge Vault 1.0)

## 1. Principios Fundamentales
Este estándar define la arquitectura de memoria para todos los proyectos del ecosistema Antigravity. El objetivo es garantizar que cualquier agente (Salud, Legal, Auditoría) pueda leer, escribir y compartir conocimiento sin barreras de formato.

### 1.1 Regla de Oro
> **"Si entra a la memoria, se folia, se indexa y se respalda en Markdown."**

---

## 2. Arquitectura de Almacenamiento (The Shadow Twin Patter)

Todo repositorio de conocimiento debe seguir estrictamente esta estructura de carpetas:

```text
data/
└── knowledge_repo/
    ├── raw/       # VERDAD FÍSICA (Inmutable)
    │   └── DOC-2026-001_Norma_Tecnica_147.pdf
    └── shadow/    # VERDAD LÓGICA (Legible por Agente)
        └── DOC-2026-001_Norma_Tecnica_147.md
```

### 2.1 Estrategia de Foliación
Cada documento ingresado al sistema recibe un **ID Único de Folio**:
- **Formato:** `DOC-{YYYY}-{SEQ}`
- **Ejemplo:** `DOC-2026-001`
- **Persistencia:** Este ID vincula el archivo físico, el archivo Markdown y el registro en la base de datos.

---

## 3. Esquema de Base de Datos (Universal SQL)

Cada proyecto instancia su propia base de datos SQLite en `data/knowledge_vault.db`. Este esquema es MANDATORIO y no debe modificarse arbitrariamente.

### 3.1 Tabla: Inventario de Fuentes (`sources_index`)
Controla la existencia y vigencia de los archivos foliados.

```sql
CREATE TABLE IF NOT EXISTS sources_index (
    folio_id TEXT PRIMARY KEY,          -- DOC-2026-001
    file_name TEXT NOT NULL,            -- Norma_Tecnica_147.pdf
    file_hash TEXT NOT NULL,            -- SHA-256 del archivo raw
    source_url TEXT,                    -- URL original (origen)
    institution TEXT,                   -- MINSAL, CGR, etc.
    ingestion_date TEXT,                -- ISO 8601
    validity_status TEXT DEFAULT 'active' -- active, deprecated, superseded
);
```

### 3.2 Tabla: Memoria de Hallazgos (`findings_memory`)
Almacena el conocimiento extraído para evitar reprocesar documentos ("No investigar lo mismo dos veces").

```sql
CREATE TABLE IF NOT EXISTS findings_memory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    folio_id TEXT NOT NULL,             -- FK -> sources_index
    topic TEXT NOT NULL,                -- Ej: "Vacunas", "Licencias"
    quote_text TEXT NOT NULL,           -- Cita textual
    page_number INTEGER,                -- Ubicación física
    finding_type TEXT,                  -- OBLIGATION, PROHIBITION, DEFINITION
    confidence_score REAL,              -- 0.0 a 1.0
    FOREIGN KEY(folio_id) REFERENCES sources_index(folio_id)
);
```

### 3.3 Tabla: Log de Operaciones (`audit_log`)
Trazabilidad de acciones del agente (scan, update, sync).

```sql
CREATE TABLE IF NOT EXISTS audit_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
    operation TEXT,                     -- INGEST, SYNC_PUSH, SYNC_PULL
    details TEXT                        -- JSON payload
);
```

---

## 4. Protocolo de Federación (Sync)

Al compartir el mismo esquema, los proyectos pueden sincronizarse mediante comandos estandarizados manejados por la CLI (`saia_cli` o equivalente).

- **Push Global:** `INSERT INTO central_db.sources_index SELECT * FROM local_db.sources_index WHERE new=1`
- **Pull Referencial:** Traer metadatos de normas sin descargar los archivos hasta que sea necesario.
