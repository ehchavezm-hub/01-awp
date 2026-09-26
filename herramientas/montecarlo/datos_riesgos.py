"""Datos de entrada del libro: riesgos (leidos de Ejemplo.xlsm) y estimaciones del ANEXO A del prompt v3.

Las estimaciones de R-01 a R-32 son PRELIMINARES (ESTADO = "ESTIMADO – VALIDAR"): se hicieron con un
costo base supuesto de S/ 200 M y un plazo de 730 días. Deben validarse con el dueño de cada riesgo.
"""

import re

import openpyxl

COSTO_BASE = 200_000_000
PLAZO_BASE = 730
M = 1_000_000
K = 1_000

# ID: (categoria, grupo, prob, costo, plazo, ing_diseno, ing_campo)
#   costo = (dist, p1, p2, p3); plazo/ing = (dist, p1, p2, p3) o None
ESTIMACIONES = {
    "R-01": ("CONTRACTUAL", "CONTRACTUAL", 0.40, ("PERT", 1.5 * M, 4.0 * M, 9.0 * M), None, None, None),
    "R-02": ("CONTRACTUAL", "CONTRACTUAL", 0.50, ("PERT", 300 * K, 800 * K, 1.8 * M), None, ("TRIANGULAR", 80, 200, 400), None),
    "R-03": ("PRODUCCION", "SOBRECONSUMO", 0.60, ("PERT", 400 * K, 1.0 * M, 2.2 * M), None, None, None),
    "R-04": ("COSTOS", "", 0.50, ("PERT", 800 * K, 2.0 * M, 4.5 * M), None, None, None),
    "R-05": ("APROBACIONES", "APROBACIONES", 0.45, ("PERT", 200 * K, 500 * K, 1.2 * M), ("TRIANGULAR", 15, 30, 60),
             ("TRIANGULAR", 120, 300, 600), None),
    "R-06": ("CALIDAD", "CALIDAD", 0.35, ("PERT", 150 * K, 400 * K, 900 * K), ("TRIANGULAR", 3, 7, 15), None,
             ("TRIANGULAR", 200, 500, 1200)),
    "R-07": ("CALIDAD", "CALIDAD", 0.30, ("PERT", 100 * K, 300 * K, 700 * K), ("TRIANGULAR", 2, 5, 12), None,
             ("TRIANGULAR", 150, 400, 900)),
    "R-08": ("CALIDAD", "CALIDAD", 0.30, ("PERT", 100 * K, 350 * K, 800 * K), None, None, ("TRIANGULAR", 150, 350, 800)),
    "R-09": ("SSOMA", "", 0.08, ("PERT", 300 * K, 1.2 * M, 4.0 * M), ("TRIANGULAR", 5, 15, 45), None, None),
    "R-10": ("CONTRACTUAL", "CONTRACTUAL", 0.40, ("PERT", 200 * K, 600 * K, 1.5 * M), None, None, None),
    "R-11": ("APROBACIONES", "APROBACIONES", 0.55, ("PERT", 200 * K, 600 * K, 1.4 * M), ("TRIANGULAR", 10, 20, 45), None, None),
    "R-12": ("TERCEROS", "", 0.25, ("PERT", 300 * K, 1.0 * M, 3.5 * M), ("TRIANGULAR", 0, 7, 30), None,
             ("TRIANGULAR", 100, 300, 800)),
    "R-13": ("APROBACIONES", "APROBACIONES", 0.50, ("PERT", 100 * K, 400 * K, 1.0 * M), ("TRIANGULAR", 5, 15, 35), None, None),
    "R-14": ("INGENIERIA", "INGENIERIA", 0.65, ("PERT", 800 * K, 2.5 * M, 6.0 * M), ("TRIANGULAR", 10, 25, 60),
             ("PERT", 500, 1500, 4000), ("PERT", 300, 900, 2500)),
    "R-15": ("TERCEROS", "", 0.30, ("PERT", 150 * K, 400 * K, 900 * K), None, None, None),
    "R-16": ("PERMISOS", "", 0.12, ("PERT", 500 * K, 1.8 * M, 5.0 * M), ("TRIANGULAR", 15, 45, 120),
             ("TRIANGULAR", 200, 500, 1200), None),
    "R-17": ("CONTRACTUAL", "CONTRACTUAL", 0.40, ("PERT", 300 * K, 900 * K, 2.0 * M), None, None, None),
    "R-18": ("CONTRACTUAL", "CONTRACTUAL", 0.45, ("PERT", 400 * K, 1.2 * M, 2.8 * M), None, None, None),
    "R-19": ("CONTRACTUAL", "CONTRACTUAL", 0.40, ("PERT", 200 * K, 500 * K, 1.2 * M), None, None, None),
    "R-20": ("CONTRACTUAL", "EXTENSION_PLAZO", 0.35, ("PERT", 800 * K, 2.5 * M, 6.0 * M), None, None, None),
    "R-21": ("INGENIERIA", "INGENIERIA", 0.55, ("PERT", 500 * K, 1.5 * M, 3.5 * M), ("TRIANGULAR", 5, 12, 30),
             ("PERT", 400, 1000, 2500), None),
    "R-22": ("INGENIERIA", "INGENIERIA", 0.45, ("PERT", 300 * K, 900 * K, 2.2 * M), None, ("PERT", 300, 700, 1800), None),
    "R-23": ("INGENIERIA", "INGENIERIA", 0.40, ("PERT", 200 * K, 600 * K, 1.5 * M), None, ("PERT", 200, 500, 1200), None),
    "R-24": ("COSTOS", "", 0.90, ("TRIANGULAR", 300 * K, 500 * K, 800 * K), None, None, None),
    "R-25": ("COSTOS", "", 0.50, ("PERT", 200 * K, 600 * K, 1.4 * M), None, None, None),
    "R-26": ("COSTOS", "EXTENSION_PLAZO", 0.40, ("PERT", 1.0 * M, 3.0 * M, 7.0 * M), None, None, None),
    "R-27": ("COSTOS", "EXTENSION_PLAZO", 0.40, ("PERT", 400 * K, 1.2 * M, 3.0 * M), None, None, None),
    "R-28": ("PRODUCCION", "SOBRECONSUMO", 0.50, ("PERT", 300 * K, 800 * K, 1.8 * M), None, None, None),
    "R-29": ("PRODUCCION", "SOBRECONSUMO", 0.45, ("PERT", 200 * K, 500 * K, 1.2 * M), None, None, None),
    "R-30": ("PRODUCCION", "SOBRECONSUMO", 0.40, ("PERT", 100 * K, 300 * K, 700 * K), None, None, None),
    "R-31": ("PRODUCCION", "SOBRECONSUMO", 0.50, ("PERT", 300 * K, 900 * K, 2.0 * M), None, None, None),
    "R-32": ("PRODUCCION", "SOBRECONSUMO", 0.50, ("PERT", 200 * K, 600 * K, 1.5 * M), None, None, None),
}
RHO_GRUPO = {"CONTRACTUAL": 0.5, "APROBACIONES": 0.5, "CALIDAD": 0.4, "INGENIERIA": 0.5,
             "EXTENSION_PLAZO": 0.6, "SOBRECONSUMO": 0.4}
NOTA_BASE = ("Estimación preliminar del analista con costo base supuesto S/ 200 M y plazo 730 días; "
             "validar con el dueño del riesgo.")
NOTAS_EXTRA = {
    "R-03": " Probabilidad > 50 %: activa la advertencia M5.",
    "R-11": " Probabilidad > 50 %: activa la advertencia M5.",
    "R-14": " Probabilidad > 50 %: activa la advertencia M5.",
    "R-21": " Probabilidad > 50 %: activa la advertencia M5.",
    "R-24": " «Ya realizados»: casi seguro; la advertencia M5 sugiere pasarlo a la línea base.",
    "R-17": " Confirmar si es oportunidad (reconocimiento del cliente).",
    "R-18": " Confirmar si es oportunidad (reconocimiento del cliente).",
    "R-19": " Confirmar si es oportunidad (reconocimiento del cliente).",
    "R-20": " Confirmar si es oportunidad (reconocimiento del cliente).",
    "R-09": " Baja probabilidad y alto impacto: domina la cola del plazo.",
    "R-16": " Baja probabilidad y alto impacto: domina la cola del plazo.",
}

# Riesgos demostrativos de la version 1 (filas 12-16 de Ejemplo.xlsm), inactivos.
EJEMPLOS = [
    # id, nombre, prob, costo, plazo
    ("EJ-1", "Ingeniería en desarrollo (90 entregables)", 1.0, None, ("TRIANGULAR", 7, 14, 28)),
    ("EJ-2", "Alza de precios de materiales", 1.0, ("NORMAL", 50000, 25000, None), None),
    ("EJ-3", "Condiciones geotécnicas imprevistas", 0.35, ("PERT", 30000, 80000, 200000), ("PERT", 10, 25, 60)),
    ("EJ-4", "Huelga o paralización", 0.20, None, ("TRIANGULAR", 5, 15, 45)),
    ("EJ-5", "Demora en permisos y aprobaciones", 1.0, None, ("UNIFORME", 10, 40, None)),
]


def normalizar(t):
    return re.sub(r"\s+", " ", str(t)).strip()


def leer_ejemplo(ruta):
    """Devuelve (filas_origen, riesgos) leyendo Ejemplo.xlsm (solo valores, sin VBA)."""
    ws = openpyxl.load_workbook(ruta, data_only=True)["PARAMETROS"]
    tabla = ws.tables["tblRiesgos"]
    ref = tabla.ref                                   # B11:N61
    c0, f0 = ref.split(":")[0][0], int(ref.split(":")[0][1:])
    f1 = int(re.findall(r"\d+", ref.split(":")[1])[0])
    enc = [c.value for c in ws[f0]][1:14]
    filas = []
    for f in range(f0 + 1, f1 + 1):
        vals = [ws.cell(f, c).value for c in range(2, 15)]
        if any(v not in (None, "") for v in vals):
            filas.append((f, dict(zip(enc, vals))))
    return enc, filas


def construir_riesgos(ruta_ejemplo):
    """Mapea Ejemplo.xlsm a las filas de tblRiesgos v3. Devuelve (riesgos, mapeo)."""
    enc, filas = leer_ejemplo(ruta_ejemplo)
    reales = [(f, d) for f, d in filas if f >= 17]
    demos = [(f, d) for f, d in filas if f < 17]
    assert len(reales) == 32, len(reales)
    assert len(demos) == 5, len(demos)
    riesgos = []
    for n, (f, d) in enumerate(reales, 1):
        rid = "R-%02d" % n
        nombre = normalizar(d["NOMBRE DEL RIESGO"])
        causa = ""
        m = re.search(r"\s-\s*Debido al?\s+(.*)$", nombre, re.I)
        if m:
            causa = m.group(1).strip()
        cat, grupo, prob, costo, plazo, dis, cam = ESTIMACIONES[rid]
        riesgos.append(dict(
            ID=rid, NOMBRE=nombre, TIPO="AMENAZA", CATEGORIA=cat, CAUSA=causa, DUENO="",
            ESTADO="ESTIMADO – VALIDAR", ACTIVO="SI", PROB=prob,
            DIMS={"COSTO": costo, "PLAZO": plazo, "ING_DISENO": dis, "ING_CAMPO": cam},
            GRUPO=grupo, RHO=RHO_GRUPO.get(grupo) if grupo else None,
            NOTAS=NOTA_BASE + NOTAS_EXTRA.get(rid, ""), FILA_ORIGEN=f))
    for (f, d), (eid, nom, prob, costo, plazo) in zip(demos, EJEMPLOS):
        assert normalizar(d["NOMBRE DEL RIESGO"]) == nom, (d["NOMBRE DEL RIESGO"], nom)
        riesgos.append(dict(
            ID=eid, NOMBRE=nom, TIPO="AMENAZA", CATEGORIA="EJEMPLO", CAUSA="", DUENO="",
            ESTADO="EJEMPLO", ACTIVO="NO", PROB=prob,
            DIMS={"COSTO": costo, "PLAZO": plazo, "ING_DISENO": None, "ING_CAMPO": None},
            GRUPO="", RHO=None, NOTAS="EJEMPLO – desactivar al cargar datos reales (riesgo demostrativo de la versión 1).",
            FILA_ORIGEN=f))
    mapeo = [
        ("ID (vacío en R-01…R-32; 1–5 en ejemplos)", "ID", "R-01…R-32 según el orden de las filas 17–48; EJ-1…EJ-5 para las filas 12–16"),
        ("NOMBRE DEL RIESGO", "NOMBRE DEL RIESGO", "espacios recortados y dobles unidos; texto sin otros cambios"),
        ("NOMBRE DEL RIESGO (tras « - Debido a»)", "CAUSA", "copia del texto posterior a «Debido a» (15 filas)"),
        ("ACTIVO (SI/NO)", "ACTIVO", "R-01…R-32 = SI (estimados); EJ = NO (decisión D1)"),
        ("PROBABILIDAD (0-1)", "PROBABILIDAD", "EJ: igual al origen; R: ANEXO A (el origen está vacío)"),
        ("DIST_COSTO, C_P1…C_P3", "DIST_COSTO, COSTO_P1…COSTO_P3", "EJ: igual al origen; R: ANEXO A"),
        ("DIST_PLAZO, T_P1…T_P3", "DIST_PLAZO, PLAZO_P1…PLAZO_P3", "EJ: igual al origen; R: ANEXO A"),
        ("—", "DIST_ING_DISENO…, DIST_ING_CAMPO…", "nuevas dimensiones; R: ANEXO A"),
        ("NOTAS", "NOTAS", "EJ: «EJEMPLO – desactivar…»; R: nota de estimación preliminar"),
        ("—", "TIPO, CATEGORIA, ESTADO, GRUPO_CORRELACION, RHO_GRUPO", "ANEXO A (TIPO = AMENAZA; ESTADO = ESTIMADO – VALIDAR / EJEMPLO)"),
    ]
    return riesgos, mapeo
