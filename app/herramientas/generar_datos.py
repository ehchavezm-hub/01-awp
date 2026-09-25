"""Genera los datos públicos de la aplicación a partir del repositorio:

* app/web/datos/glosario.js – siglas de includes/abreviaturas.md más
  definiciones, ejemplos y enlaces de los conceptos AWP principales.
* app/web/datos/recursos.js – catálogo de la biblioteca de recursos, tomado
  de docs/implementacion/plantillas.md (misma descripción que la web).

Uso:
    python app/herramientas/generar_datos.py
"""

import json
import re
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
SALIDA = RAIZ / "app" / "web" / "datos"

# Conceptos con explicación ampliada: definición breve, ejemplo del proyecto tipo
# y página de la web de consulta (ruta relativa a la raíz de la web).
CONCEPTOS = {
    "AWP": ("Forma de planificar y ejecutar en la que la secuencia de construcción manda: el proyecto se divide en áreas y paquetes, y la ingeniería y la procura se entregan en el orden que construcción necesita.", "Beneficio de referencia del CII: +25 % de productividad y −10 % de costo total instalado.", "introduccion/que-es-awp-insight/"),
    "CWA": ("Área geográfica o lógica del proyecto que organiza la secuencia de construcción. No se superpone con otras CWA y pertenece a una sola fase.", "CWA-2.01 · Instalación principal – bloque A.", "implementacion/flujo-paquetes/"),
    "CWP": ("Paquete de construcción de una sola disciplina dentro de una CWA, de menos de 40 000 HH. Es una actividad de nivel 3 del cronograma y se divide en IWP.", "CWP-2.01-EST-01 · Estructura metálica bloque A.", "implementacion/flujo-paquetes/"),
    "EWP": ("Paquete de ingeniería con todo lo que necesita un CWP: planos IFC, especificaciones y lista de materiales. Se entrega en la secuencia del Path of Construction.", "EWP-2.01-EST-01, emitido IFC antes de la fecha requerida por el PoC.", "implementacion/flujo-paquetes/"),
    "PWP": ("Paquete de procura con los materiales, equipos y documentación del proveedor que requiere un CWP, con fechas requeridas en obra (RAS).", "PWP-2.01-EST-01 · estructura fabricada y pernos.", "implementacion/flujo-paquetes/"),
    "IWP": ("Paquete de instalación: el trabajo de un capataz y su cuadrilla durante alrededor de una semana (300 a 600 HH). Solo va a campo sin restricciones abiertas.", "IWP-2.01-EST-01-001 · Montaje de columnas nivel 1 ejes A1–A4 · 420 HH.", "implementacion/flujo-paquetes/"),
    "PoC": ("Path of Construction: la secuencia en que se construirán las CWA y los CWP. Se define en talleres de planificación interactiva y dirige las fechas de ingeniería y procura.", "Primero la sala eléctrica (energización temprana), luego los bloques A y B.", "implementacion/etapas-ciclo-de-vida/"),
    "WFP": ("Workface Planning: preparar y entregar a cada cuadrilla IWP completos y sin restricciones, con un backlog de trabajo liberado.", "1 planificador de frente de trabajo por cada 50 trabajadores.", "procedimientos/3-workface-planning/"),
    "FEL": ("Front-End Loading: la planificación temprana del proyecto. En AWP es la etapa donde se definen las CWA, el PoC y el plan de liberación de paquetes.", "Hitos H0 a H4 del plan de implementación.", "implementacion/etapas-ciclo-de-vida/"),
    "PPC": ("Porcentaje de plan cumplido: IWP completados en la semana según el plan ÷ IWP planificados. Mide la confiabilidad del plan semanal (KPI K08).", "29 de 36 IWP completados = 80,6 %.", "implementacion/kpi/"),
    "KPI": ("Indicador clave de desempeño. El kit usa 13 (K01–K13) con las mismas fórmulas en todas las fases para poder compararlas.", "K03 · IWP liberados sin restricciones ≥ 95 % en la Fase 2.", "implementacion/kpi/"),
    "IFC": ("Emitido para construcción: estado de un documento de ingeniería aprobado para construir. Solo documentos IFC entran a un IWP.", "Plano EST-PL-2011 rev. 2 IFC.", "referencia/glosario/"),
    "RAS": ("Fecha requerida en obra de un material o equipo, calculada desde el Path of Construction.", "Estructura del bloque A: 10 días antes del primer IWP de montaje.", "implementacion/flujo-paquetes/"),
    "SWP": ("Paquete de trabajo de sistema: agrupa el trabajo por sistemas para el comisionamiento y la puesta en marcha.", "SWP del sistema de agua de servicio del bloque A.", "implementacion/etapas-ciclo-de-vida/"),
    "Backlog": ("Cartera de IWP liberados y listos para ejecutar, medida en semanas de trabajo. Meta del kit: 2 a 4 semanas.", "58 000 HH liberadas ÷ 20 800 HH por semana = 2,7 semanas.", "implementacion/restricciones-liberacion/"),
    "Restricción": ("Cualquier información, material, equipo, permiso, acceso u otro factor que impida o retrase la ejecución segura y completa de un trabajo.", "R-0005 · Grúa de 100 t no disponible para el montaje de columnas.", "implementacion/restricciones-liberacion/"),
    "AWP Champion": ("Responsable de liderar la implementación de AWP a tiempo completo: procedimientos, plantillas, formación, talleres del PoC, KPI y lecciones.", "Designarlo es el hito H0 del plan.", "implementacion/organizacion/"),
    "Hito": ("Punto de control de la implementación AWP con un criterio de cumplimiento y una evidencia. El kit define H0 a H10 para cada fase.", "H7 · Primer IWP liberado: checklist firmado y entregado al capataz.", "implementacion/hitos/"),
    "Fase del proyecto": ("Cada parte en que se divide la ejecución del proyecto (Fase 1, 2, 3…). Pueden superponerse en el tiempo.", "Fase 1 · Infraestructura y obras tempranas.", "implementacion/proyecto-tipo/"),
    "Etapa del ciclo de vida": ("Cada etapa por la que pasa el trabajo de una fase: planificación temprana (FEL), ingeniería, procura, construcción y comisionamiento.", "Cada fase recorre las cinco etapas.", "implementacion/etapas-ciclo-de-vida/"),
    "Lookahead": ("Programación de las próximas 3 semanas con IWP tomados del backlog, confirmando recursos críticos.", "Reunión semanal de lookahead (jueves).", "implementacion/restricciones-liberacion/"),
}

# Categoría de cada recurso y ruta del formulario en la app (si existe).
CATEGORIA = {
    "Plan_Implementacion_AWP.docx": ("Planificación", None),
    "Definicion_CWA.xlsx": ("Planificación", "cwa"), "Path_of_Construction.xlsx": ("Planificación", "poc"),
    "Programa_Liberacion_IWP.xlsx": ("Planificación", "liberacion"), "Lookahead_3_Semanas.xlsx": ("Planificación", "lookahead"),
    "Plantilla_CWP.docx": ("Planificación", "paquetes"), "Plantilla_EWP.docx": ("Planificación", "paquetes"),
    "Plantilla_IWP.docx": ("Planificación", "paquetes"), "Acta_Taller_Path_of_Construction.docx": ("Planificación", "poc"),
    "Registro_Restricciones.xlsx": ("Control", "restricciones"), "Seguimiento_Paquetes.xlsx": ("Control", "paquetes"),
    "Checklist_Liberacion_IWP.xlsx": ("Control", "liberacion"), "Tablero_KPI.xlsx": ("Control", "kpi"),
    "Registro_Riesgos.xlsx": ("Control", "riesgos"), "Registro_Lecciones_Aprendidas.xlsx": ("Control", "lecciones"),
    "Informe_Cierre_Fase_AWP.docx": ("Control", "fases"), "Procedimiento_Gestion_Restricciones.docx": ("Control", "documentos"),
    "Matriz_Roles_RACI.xlsx": ("Organización", "roles"), "Perfiles_Puesto_AWP.docx": ("Organización", "roles"),
}

MODULOS_PRESENTACION = [
    ("1", "Por qué AWP", "5–12", None), ("2", "Qué es AWP", "13–24", "paquetes"),
    ("3", "Preparar la organización", "25–34", "roles"), ("4", "Planificación preliminar (FEL)", "35–46", "poc"),
    ("5", "Ingeniería y compras", "47–58", "paquetes"), ("6", "Construcción", "59–74", "restricciones"),
    ("7", "Puesta en marcha", "75–79", "hitos"), ("8", "Información y tecnología", "80–86", None),
    ("9", "Roles y organización", "87–95", "roles"), ("10", "Medición", "96–102", "kpi"),
    ("11", "Escalar y adoptar", "103–110", None), ("12", "Errores y lecciones", "111–118", "lecciones"),
    ("13", "Hoja de ruta", "119–122", "avance"),
]


def limpiar(md):
    md = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", md)
    md = re.sub(r"\*\*|`", "", md)
    return re.sub(r"(?<!\w)\*([^*]+)\*(?!\w)", r"\1", md).strip()


def glosario():
    siglas = {}
    for linea in (RAIZ / "includes" / "abreviaturas.md").read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\*\[([^\]]+)\]: (.+)$", linea)
        if m:
            siglas[m.group(1)] = m.group(2).strip()
    datos = {}
    for sigla, nombre in siglas.items():
        if sigla.endswith("s") and sigla[:-1] in siglas:
            continue  # plurales (CWPs, IWPs…)
        datos[sigla] = {"nombre": nombre}
    for clave, (definicion, ejemplo, pagina) in CONCEPTOS.items():
        datos.setdefault(clave, {}).update({"definicion": definicion, "ejemplo": ejemplo, "pagina": pagina})
        if clave == "PoC":
            datos[clave]["nombre"] = siglas.get("PoC", "Path of Construction – ruta de construcción")
    return datos


def recursos():
    texto = (RAIZ / "docs" / "implementacion" / "plantillas.md").read_text(encoding="utf-8")
    lista = []
    for fila in texto.splitlines():
        if not fila.startswith("| **"):
            continue
        c = [x.strip() for x in fila.strip().strip("|").split("|")]
        archivo = re.search(r"\(descargas/([^)]+)\)", c[4]).group(1)
        cat, formulario = CATEGORIA[archivo]
        lista.append({
            "nombre": limpiar(c[0]), "archivo": archivo, "tipo": archivo.rsplit(".", 1)[1],
            "para": limpiar(c[1]), "cuando": limpiar(c[2]), "quien": limpiar(c[3]),
            "categoria": cat, "formulario": formulario,
        })
    lista.insert(0, {
        "nombre": "Plan de implementación de AWP", "archivo": "Plan_Implementacion_AWP.docx", "tipo": "docx",
        "para": "Plan completo para el proyecto tipo: fases, etapas del ciclo de vida, hitos, roles, flujo de paquetes, restricciones, riesgos, KPI, lecciones y cronograma.",
        "cuando": "Al iniciar el proyecto y en cada puerta de control entre fases.", "quien": "AWP Champion; lo aprueba el cliente.",
        "categoria": "Planificación", "formulario": "avance",
    })
    web = [
        ("Plan de implementación (web)", "implementacion/", "El mismo plan, navegable, con diagramas.", "Para consultar rápido desde el celular o la obra.", "Todo el equipo"),
        ("Glosario de siglas y términos", "referencia/glosario/", "Todas las siglas AWP explicadas en español.", "Cuando aparezca una sigla nueva.", "Todo el equipo"),
        ("Curso integrado de AWP (2023)", "formacion/curso-awp-2023/", "Unas 34 lecciones: CWA, PoC, EWP, CWP, WFP, restricciones, KPI y lecciones.", "Formación del equipo antes de cada fase.", "Planificadores, líderes y supervisores"),
        ("Procedimiento 3.0 Workface Planning", "procedimientos/3-workface-planning/", "Procedimiento de referencia de WFP: backlog, lookahead, Pack Track y códigos de demora.", "Al preparar la construcción de cada fase.", "Líder de WFP y planificadores"),
    ]
    for nombre, ruta, para, cuando, quien in web:
        lista.append({"nombre": nombre, "archivo": ruta, "tipo": "web", "para": para, "cuando": cuando, "quien": quien,
                      "categoria": "Capacitación", "formulario": None})
    return lista


def main():
    SALIDA.mkdir(parents=True, exist_ok=True)
    cab = "// Generado por app/herramientas/generar_datos.py. No editar a mano.\n"
    (SALIDA / "glosario.js").write_text(
        cab + "export const GLOSARIO = " + json.dumps(glosario(), ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    r = recursos()
    presentacion = {
        "nombre": "Implementar AWP: guía práctica de implementación", "archivo": "presentacion/implementacion_awp.pptx",
        "tipo": "pptx", "laminas": 122, "categoria": "Capacitación",
        "para": "Material para formar al equipo antes de cada fase. Recorre un proyecto real etapa por etapa, con las cifras del CII, la COAA e Insight-AWP.",
        "cuando": "Arranque del proyecto y de cada fase; inducción del personal nuevo.", "quien": "AWP Champion (lo presenta)",
        "modulos": [{"n": n, "nombre": nom, "laminas": lam, "modulo_app": mod} for n, nom, lam, mod in MODULOS_PRESENTACION],
        "nota": "En la presentación, «Fase 1–4» son las etapas del ciclo de vida (planificación preliminar, ingeniería y compras, construcción y puesta en marcha).",
    }
    (SALIDA / "recursos.js").write_text(
        cab + "export const RECURSOS = " + json.dumps(r, ensure_ascii=False, indent=1) + ";\n"
        + "export const PRESENTACION = " + json.dumps(presentacion, ensure_ascii=False, indent=1) + ";\n", encoding="utf-8")
    print(f"glosario.js y recursos.js generados ({len(r)} recursos).")


if __name__ == "__main__":
    main()
