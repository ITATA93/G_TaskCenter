# Protocolo de Actualización Segura y Normalización

Este protocolo define cómo Antigravity debe actualizar o normalizar proyectos existentes sin corromper el trabajo previo.

## 1. Principio de Seguridad (Non-Destructive Update)
Antes de sobrescribir cualquier configuración crítica, el agente debe:
1.  **Backup**: Crear una copia de seguridad de los archivos a modificar en una carpeta `.backup/` o `_legacy/`.
2.  **Diff**: Comparar versiones para asegurar que no se pierden configuraciones personalizadas del usuario.
3.  **Validación**: Si la actualización implica cambios en scripts de build o deploy, estos no se activan automáticamente.

## 2. Registro de Cambios (Feedback Loop)
Cada actualización debe registrarse en `AG_Plantilla/config/project_registry.json` con:
- Fecha y tipo de acción (creación, normalización, update).
- Agentes y Skills utilizados.
- Resultado de la operación.

## 3. Lista de Tareas Post-Actualización (Startup Checklist)
Al finalizar una actualización, el agente generará/actualizará un archivo `UPDATE_TASKS.md` en la raíz del proyecto objetivo.
Este archivo actúa como un "semáforo" para el inicio del proyecto.

### Formato de `UPDATE_TASKS.md`:
```markdown
# 🚀 Tareas de Inicio tras Actualización
> Generado automáticamente por Antigravity el [FECHA]

El sistema ha sido actualizado a la versión [VERSION]. Antes de continuar, ejecuta:

- [ ] **Validar Identidad**: Revisa `GEMINI.md` para confirmar las nuevas instrucciones.
- [ ] **Instalar Dependencias**: Si `requirements.txt` cambió, ejecuta `pip install -r requirements.txt`.
- [ ] **Test de Regresión**: Ejecuta `pytest` para confirmar que la normalización no rompió lógica.
- [ ] **Limpieza**: Si todo funciona, puedes borrar la carpeta `_legacy/`.

## Cambios Aplicados
- [x] Actualización de `manifest.json` a v2.1
- [x] Sincronización de `dispatch.sh`
```

## 4. Retroalimentación de Skills
Si se detecta que una Skill o Prompt específico generó un conflicto o un resultado subóptimo en un proyecto, se debe registrar en el `project_registry.json` bajo el campo `issues_log` para evitar reutilizar esa estrategia sin corrección.
