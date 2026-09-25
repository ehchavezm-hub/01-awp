# Kit de implementación de AWP

Kit para implementar Advanced Work Packaging (AWP) en un proyecto de construcción ejecutado en tres fases (proyecto tipo). El contenido completo del plan está en la sección **Implementación** de la web (`docs/implementacion/`).

## Contenido

| Ruta | Contenido |
|---|---|
| `Plan_Implementacion_AWP.docx` | Plan de implementación en Word (mismo contenido que la web). |
| `plantillas/*.xlsx` | 11 plantillas Excel (restricciones, RACI, seguimiento de paquetes, CWA, Path of Construction, liberación de IWP, lookahead, checklist, KPI, riesgos y lecciones aprendidas). |
| `plantillas/*.docx` | 7 plantillas y procedimientos Word (IWP, CWP, EWP, procedimiento de restricciones, acta del taller de PoC, informe de cierre de fase y perfiles de puesto). |
| `scripts/` | Scripts que generan todos los archivos a partir de datos maestros comunes. |

La web publica los `.xlsx` y `.docx` de esta carpeta en `implementacion/descargas/` mediante el hook `hooks/descargas.py`.

## Cómo regenerar los archivos

Los datos del proyecto tipo (fases, CWA, CWP, roles, estados, listas) están en `scripts/datos_proyecto.py`. Después de cambiarlos, o de editar las páginas de `docs/implementacion/`:

```bash
pip install -r implementacion/scripts/requirements.txt
python implementacion/scripts/generar_excel.py        # plantillas Excel
python implementacion/scripts/generar_word.py         # plantillas Word
python implementacion/scripts/generar_plan_word.py    # plan en Word (desde las páginas de la web)
```

Los diagramas del plan se guardan como PNG en `scripts/diagramas/`. Si cambia un diagrama Mermaid de la web, hace falta [mermaid-cli](https://github.com/mermaid-js/mermaid-cli) (`mmdc`) para renderizarlo; su ruta se indica con la variable `MMDC`.

## Verificación

```bash
soffice --headless --calc --convert-to xlsx --outdir /tmp/recalculado implementacion/plantillas/*.xlsx
python implementacion/scripts/verificar_excel.py /tmp/recalculado
```

LibreOffice recalcula todas las fórmulas; el script comprueba que ninguna dé error y que todas las listas desplegables apunten a rangos con nombre existentes.
