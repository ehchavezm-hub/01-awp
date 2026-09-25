"""Genera app/supabase/esquema.sql = estructura.sql + catálogos del kit.

Los catálogos (etapas, roles, KPI, hitos, checklist AWP, criterios, RACI…)
se leen de las mismas fuentes que las plantillas del kit, para que la
aplicación use exactamente los mismos códigos y textos:
  * implementacion/scripts/datos_proyecto.py y generar_excel.py
  * docs/implementacion/*.md (roles, hitos, actividades por etapa)

Uso:
    python app/supabase/generar_esquema.py
"""

import json
import re
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ / "implementacion" / "scripts"))

import datos_proyecto as dp  # noqa: E402
import generar_excel as ge  # noqa: E402

DOCS = RAIZ / "docs" / "implementacion"
CODIGO_ETAPA = {"Planificación temprana (FEL)": "FEL", "Ingeniería": "ING", "Procura": "PRO",
                "Construcción": "CON", "Comisionamiento": "COM"}

# Anticipación mínima por tipo de restricción (Procedimiento_Gestion_Restricciones, sección 6).
ANTICIPACION = {"Ingeniería": 4, "Materiales": 4, "Equipos de construcción": 3, "Permisos": 3, "Mano de obra": 2,
                "Andamios": 3, "Acceso / interferencias": 2, "Trabajos predecesores": 1, "Calidad": 2, "HSE": 2,
                "Documentación del proveedor": 4, "Interfaz entre fases": 6}

# Hito y plantilla relacionados con cada actividad del checklist AWP.
HITO_ACTIVIDAD = {"FEL-01": "H0", "FEL-03": "H1", "FEL-04": "H2", "FEL-05": "H3", "FEL-07": "H4",
                  "ING-03": "H5", "CON-01": "H6", "CON-04": "H7", "COM-03": "H9", "COM-04": "H10"}
PLANTILLA_ACTIVIDAD = {
    "FEL-01": "Perfiles_Puesto_AWP.docx", "FEL-02": "Registro_Riesgos.xlsx", "FEL-03": "Definicion_CWA.xlsx",
    "FEL-04": "Path_of_Construction.xlsx", "FEL-05": "Seguimiento_Paquetes.xlsx", "FEL-06": "Seguimiento_Paquetes.xlsx",
    "FEL-07": "Matriz_Roles_RACI.xlsx", "ING-01": "Plantilla_EWP.docx", "ING-03": "Plantilla_EWP.docx",
    "PRO-01": "Seguimiento_Paquetes.xlsx", "PRO-03": "Seguimiento_Paquetes.xlsx",
    "CON-01": "Plantilla_CWP.docx", "CON-02": "Plantilla_IWP.docx", "CON-03": "Registro_Restricciones.xlsx",
    "CON-04": "Checklist_Liberacion_IWP.xlsx", "CON-05": "Lookahead_3_Semanas.xlsx", "CON-07": "Tablero_KPI.xlsx",
    "COM-04": "Informe_Cierre_Fase_AWP.docx",
}


def q(v):
    """Literal SQL."""
    if v is None:
        return "null"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, (dict, list)):
        return "'" + json.dumps(v, ensure_ascii=False).replace("'", "''") + "'::jsonb"
    return "'" + str(v).replace("'", "''") + "'"


def insert(tabla, columnas, filas):
    valores = ",\n  ".join("(" + ", ".join(q(v) for v in f) + ")" for f in filas)
    return f"insert into public.{tabla} ({', '.join(columnas)}) values\n  {valores};\n"


def tabla_md(texto, encabezado_inicio):
    """Filas de la primera tabla Markdown cuyo encabezado empieza por el texto dado."""
    lineas = texto.splitlines()
    for i, l in enumerate(lineas):
        if l.startswith("| " + encabezado_inicio):
            filas = []
            for fila in lineas[i + 2:]:
                if not fila.startswith("|"):
                    break
                filas.append([c.strip() for c in fila.strip().strip("|").split("|")])
            return filas
    raise ValueError(f"No se encontró la tabla que empieza con «{encabezado_inicio}»")


def limpiar(md):
    return re.sub(r"\*\*|\*|`", "", re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)).strip()


def actividades_awp():
    texto = (DOCS / "etapas-ciclo-de-vida.md").read_text(encoding="utf-8")
    filas = []
    for etapa, codigo in CODIGO_ETAPA.items():
        m = re.search(r"^## \d\. " + re.escape(etapa) + r"\n(.*?)(?=^## )", texto, re.S | re.M)
        orden = 0
        for linea in m.group(1).splitlines():
            it = re.match(r"^\d+\. \*\*(.+?)\*\*[,:]? ?(.*)$", linea)
            if not it:
                continue
            orden += 1
            cod = f"{codigo}-{orden:02d}"
            nombre = limpiar(it.group(1)).rstrip(".")
            desc = limpiar(it.group(2)).lstrip(": ").strip()
            frase = f"{nombre} {desc}".strip() if desc else nombre + "."
            filas.append((cod, etapa, orden, nombre, frase, HITO_ACTIVIDAD.get(cod), PLANTILLA_ACTIVIDAD.get(cod)))
    return filas


def main():
    partes = [
        "-- ==========================================================================\n"
        "-- ESQUEMA DE LA APLICACIÓN AWP PARA SUPABASE\n"
        "-- ==========================================================================\n"
        "-- Archivo generado por app/supabase/generar_esquema.py a partir de\n"
        "-- estructura.sql y de los catálogos del kit de implementación. No lo edite\n"
        "-- a mano: cambie estructura.sql o los datos del kit y vuelva a generarlo.\n"
        "--\n"
        "-- Cómo usarlo: Supabase > SQL Editor > New query > pegar todo > Run.\n"
        "-- Debe ejecutarse una sola vez, en un proyecto de Supabase vacío.\n"
        "-- No contiene datos de proyectos: solo estructura, seguridad y catálogos\n"
        "-- públicos del kit.\n\n",
        (AQUI / "estructura.sql").read_text(encoding="utf-8"),
        "\n-- ==========================================================================\n"
        "-- CATÁLOGOS DEL KIT\n"
        "-- ==========================================================================\n",
    ]

    partes.append(insert("cat_etapas", ["codigo", "nombre", "orden"],
                         [(c, n, i) for i, (n, c) in enumerate(CODIGO_ETAPA.items(), 1)]))

    org = (DOCS / "organizacion.md").read_text(encoding="utf-8")
    resp = {f[0]: limpiar(f[4]) for f in tabla_md(org, "Código | Rol")}
    partes.append(insert("cat_roles", ["codigo", "nombre", "responsabilidades", "orden"],
                         [(c, n, resp[c], i) for i, (c, n) in enumerate(dp.ROLES, 1)]))

    partes.append(insert("cat_disciplinas", ["codigo", "nombre"], dp.DISCIPLINAS))

    rl = (DOCS / "restricciones-liberacion.md").read_text(encoding="utf-8")
    tipos = {f[0]: f for f in tabla_md(rl, "Tipo | Ejemplos")}
    partes.append(insert("cat_tipos_restriccion", ["nombre", "ejemplos", "responsable_habitual", "anticipacion_semanas"],
                         [(t, tipos[t][1], tipos[t][2], ANTICIPACION[t]) for t in dp.TIPOS_RESTRICCION]))

    partes.append(insert("cat_causas_no_cumplimiento", ["nombre", "orden"],
                         [(c, i) for i, c in enumerate(dp.CAUSAS_NO_CUMPLIMIENTO, 1)]))

    partes.append(insert("cat_kpi", ["codigo", "nombre", "formula", "unidad", "sentido", "meta_f1", "meta_f2", "meta_f3", "tipo"],
                         [(c, n, f, u, s, *m, t) for c, n, f, u, s, m, t in ge.KPIS]))

    hitos = (DOCS / "hitos.md").read_text(encoding="utf-8")
    partes.append(insert("cat_hitos", ["codigo", "nombre", "criterio", "evidencia", "aprueba", "orden"],
                         [(f[0], limpiar(f[1]), limpiar(f[2]), limpiar(f[3]), limpiar(f[4]), i)
                          for i, f in enumerate(tabla_md(hitos, "Código | Hito"), 1)]))

    acts = actividades_awp()
    partes.append(insert("cat_actividades_awp", ["codigo", "etapa", "orden", "nombre", "descripcion", "hito", "plantilla"], acts))

    partes.append(insert("cat_criterios_liberacion", ["numero", "categoria", "criterio", "rol"],
                         [(i, cat, crit, rol) for i, (cat, crit, rol) in enumerate(ge.CRITERIOS_CHECKLIST, 1)]))

    partes.append(insert("cat_criterios_cwa", ["numero", "criterio", "descripcion"],
                         [(i, c, d) for i, (c, d) in enumerate(ge.CRITERIOS_CWA, 1)]))

    partes.append(insert("cat_actividades_raci", ["orden", "etapa", "actividad", "fase", "asignaciones"],
                         [(i, e, a, f, asig) for i, (e, a, f, asig) in enumerate(ge.ACTIVIDADES_RACI, 1)]))

    (AQUI / "esquema.sql").write_text("\n".join(partes), encoding="utf-8")
    print(f"Generado app/supabase/esquema.sql: {len(acts)} actividades AWP, {len(ge.KPIS)} KPI, "
          f"{len(dp.ROLES)} roles, {len(ge.ACTIVIDADES_RACI)} actividades RACI.")


if __name__ == "__main__":
    main()
