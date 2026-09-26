"""Construye MonteCarlo_Riesgos.xlsm (versión 3) con la macro incrustada y sin protección.

Uso:  python3 build_xlsm.py [--test]
  --test  agrega al módulo las funciones de prueba (solo verificación, no para entrega)
"""

import math
import os
import re
import sys
import zipfile

import xlsxwriter

import contenido as C
from datos_riesgos import COSTO_BASE, PLAZO_BASE, construir_riesgos
from vba_project import build_vba_project

AQUI = os.path.dirname(os.path.abspath(__file__))
EJEMPLO = os.path.join(AQUI, "entrada", "Ejemplo.xlsm")

HOJAS = [("INICIO", "hjInicio"), ("GUIA", "hjGuia"), ("PARAMETROS", "hjParametros"),
         ("RESULTADOS", "hjResultados"), ("CURVA_S", "hjCurvaS"), ("TORNADO", "hjTornado"),
         ("RANGOS", "hjRangos"), ("MATRIZ_PI", "hjMatriz"), ("COMPARACION", "hjComparacion"),
         ("SIMULACION", "hjSimulacion"), ("TEORIA", "hjTeoria")]

# Paleta Bloomberg (plantilla_ppt.pptx) y roles
NEGRO, AMBAR, BLANCO = "#000000", "#FFA028", "#FFFFFF"
GRIS_TXT, BORDE = "#333333", "#333333"
ALTERNA, ENTRADA, SALIDA = "#FFF7EB", "#FFF0D6", "#EDEDED"
P10, P50, P80, P90 = "#4AF6C3", "#FFB020", "#FFA028", "#FB8B1E"
ROJO, VERDE, AZUL, NARANJA = "#FF433D", "#00C805", "#0068FF", "#FF6600"
AMBAR_PROF, PANEL2 = "#CC7A00", "#2A2A2A"

DIMENSIONES = [  # clave, nombre, unidad, base, formato, reserva de gestión, color
    ("COSTO", "Costo", "S/", "=CostoBase", "#,##0", "SI", NARANJA),
    ("PLAZO", "Plazo", "días", "=PlazoBase", "#,##0.0", "NO", AZUL),
    ("ING_DISENO", "Ingeniería de diseño", "HH", None, "#,##0", "NO", AMBAR_PROF),
    ("ING_CAMPO", "Ingeniería de campo", "HH", None, "#,##0", "NO", PANEL2),
]
FILAS_DIM = 6           # tblDimensiones con 2 filas libres para «Agregar dimensión»
FILA_CFG = 5            # fila Excel del primer parámetro (D5)
FILA_ENC_RIESGOS = 15   # encabezado de tblRiesgos (fila Excel)
FILAS_RIESGOS = 60      # filas de datos de tblRiesgos (37 cargadas + 23 libres)


def columnas_riesgos():
    cols = ["ID", "NOMBRE DEL RIESGO", "TIPO", "CATEGORIA", "CAUSA", "DUENO DEL RIESGO", "ESTADO", "ACTIVO",
            "PROBABILIDAD"]
    for d in DIMENSIONES:
        k = d[0]
        cols += ["DIST_" + k, k + "_P1", k + "_P2", k + "_P3", k + "_P4", "AYUDA_" + k]
    cols += ["GRUPO_CORRELACION", "RHO_GRUPO", "ESTRATEGIA", "PROB_RESIDUAL", "FACTOR_IMPACTO_RESIDUAL",
             "COSTO_RESPUESTA", "NOTAS"]
    return cols


# ---------------------------------------------------------------------------
# Densidades para los gráficos de la GUIA (calculadas en Python al construir)
# ---------------------------------------------------------------------------
def beta_pdf(x, a, b):
    if x <= 0 or x >= 1:
        return 0.0
    return math.exp((a - 1) * math.log(x) + (b - 1) * math.log(1 - x) - (math.lgamma(a) + math.lgamma(b) - math.lgamma(a + b)))


def pert_pdf(x, mn, mo, mx, lam=4.0):
    al = 1 + lam * (mo - mn) / (mx - mn)
    be = 1 + lam * (mx - mo) / (mx - mn)
    return beta_pdf((x - mn) / (mx - mn), al, be) / (mx - mn)


def tri_pdf(x, a, m, b):
    if x < a or x > b:
        return 0.0
    return 2 * (x - a) / ((b - a) * (m - a)) if x <= m else 2 * (b - x) / ((b - a) * (b - m))


def norm_pdf(x, mu, s):
    return math.exp(-0.5 * ((x - mu) / s) ** 2) / (s * math.sqrt(2 * math.pi))


def norm_cdf(x):
    return 0.5 * (1 + math.erf(x / math.sqrt(2)))


def graficos_guia():
    """Lista de (titulo, eje x, [(nombre_serie, xs, ys, color)], tipo)."""
    xs = [10 + 0.3 * i for i in range(101)]
    out = [("UNIFORME, TRIANGULAR y PERT (mín 10, moda 15, máx 40)", "Impacto",
            [("UNIFORME", xs, [1 / 30 if 10 <= x <= 40 else 0 for x in xs], AZUL),
             ("TRIANGULAR", xs, [tri_pdf(x, 10, 15, 40) for x in xs], NARANJA),
             ("PERT", xs, [pert_pdf(x, 10, 15, 40) for x in xs], NEGRO)], "xy")]
    out.append(("PERT_MODIFICADA: gamma 2, 4 (PERT) y 8", "Impacto",
                [("gamma 2", xs, [pert_pdf(x, 10, 15, 40, 2) for x in xs], AZUL),
                 ("gamma 4", xs, [pert_pdf(x, 10, 15, 40, 4) for x in xs], NEGRO),
                 ("gamma 8", xs, [pert_pdf(x, 10, 15, 40, 8) for x in xs], NARANJA)], "xy"))
    xs = [-10 + 0.6 * i for i in range(101)]
    fa, fb = norm_cdf((0 - 20) / 10), norm_cdf((35 - 20) / 10)
    out.append(("NORMAL (20; 10) y NORMAL_TRUNCADA en [0; 35]", "Impacto",
                [("NORMAL", xs, [norm_pdf(x, 20, 10) for x in xs], AZUL),
                 ("NORMAL_TRUNCADA", xs, [norm_pdf(x, 20, 10) / (fb - fa) if 0 <= x <= 35 else 0 for x in xs], NARANJA)], "xy"))
    xs = [0.5 + 0.8 * i for i in range(101)]
    m, s = 20.0, 12.0
    s2 = math.log(1 + (s / m) ** 2); mu = math.log(m) - s2 / 2
    k, th = (m / s) ** 2, s * s / m
    out.append(("LOGNORMAL y GAMMA con la misma media (20) y desviación (12)", "Impacto",
                [("LOGNORMAL", xs, [math.exp(-(math.log(x) - mu) ** 2 / (2 * s2)) / (x * math.sqrt(2 * math.pi * s2)) for x in xs], NARANJA),
                 ("GAMMA", xs, [math.exp((k - 1) * math.log(x) - x / th - math.lgamma(k) - k * math.log(th)) for x in xs], AZUL)], "xy"))
    xs = [0.01 + 0.5 * i for i in range(101)]
    out.append(("EXPONENCIAL (media 10) y WEIBULL (forma 2; escala 12)", "Impacto",
                [("EXPONENCIAL", xs, [math.exp(-x / 10) / 10 for x in xs], NARANJA),
                 ("WEIBULL", xs, [(2 / 12) * (x / 12) * math.exp(-(x / 12) ** 2) for x in xs], AZUL)], "xy"))
    xs = [-5 + 0.5 * i for i in range(101)]
    out.append(("GUMBEL (10; 4) y LOGISTICA (15; 3)", "Impacto",
                [("GUMBEL", xs, [(1 / 4) * math.exp(-((x - 10) / 4 + math.exp(-(x - 10) / 4))) for x in xs], NARANJA),
                 ("LOGISTICA", xs, [math.exp(-(x - 15) / 3) / (3 * (1 + math.exp(-(x - 15) / 3)) ** 2) for x in xs], AZUL)], "xy"))
    xs = [100 + 5 * i for i in range(101)]
    out.append(("PARETO (forma 2,5; mínimo 100): cola pesada", "Impacto",
                [("PARETO", xs, [2.5 * 100 ** 2.5 / x ** 3.5 for x in xs], ROJO)], "xy"))
    ks = list(range(0, 13))
    out.append(("POISSON (media 3) y BINOMIAL (n 40; p 0,15)", "Número de eventos",
                [("POISSON", ks, [math.exp(-3) * 3 ** k_ / math.factorial(k_) for k_ in ks], NARANJA),
                 ("BINOMIAL", ks, [math.comb(40, k_) * 0.15 ** k_ * 0.85 ** (40 - k_) for k_ in ks], AZUL)], "col"))
    out.append(("DISCRETA: «0;150000;400000» con «0,6;0,3;0,1»", "Impacto (S/)",
                [("DISCRETA", ["0", "150 000", "400 000"], [0.6, 0.3, 0.1], NEGRO)], "col"))
    # TRIGEN vs TRIANGULAR con los mismos tres valores
    a, b = resolver_trigen(5, 12, 30, 0.10)
    xs = [a + (b - a) * i / 100 for i in range(101)]
    out.append(("TRIGEN (5 / 12 / 30 al 10 %) vs. TRIANGULAR (5 / 12 / 30)", "Impacto",
                [("TRIGEN", xs, [tri_pdf(x, a, 12, b) for x in xs], NARANJA),
                 ("TRIANGULAR", xs, [tri_pdf(x, 5, 12, 30) for x in xs], AZUL)], "xy"))
    return out


def resolver_trigen(bajo, m, alto, q):
    a, b = bajo, alto
    for _ in range(80):
        lo, hi = bajo - 10 * (alto - bajo), bajo
        for _ in range(80):
            md = (lo + hi) / 2
            if (bajo - md) ** 2 - q * (b - md) * (m - md) > 0: lo = md
            else: hi = md
        a = (lo + hi) / 2
        lo, hi = alto, alto + 10 * (alto - bajo)
        for _ in range(80):
            md = (lo + hi) / 2
            if (md - alto) ** 2 - q * (md - a) * (md - m) > 0: hi = md
            else: lo = md
        b = (lo + hi) / 2
    return a, b


# ---------------------------------------------------------------------------
def col_letra(c):  # c: indice 0
    s = ""
    c += 1
    while c:
        c, r = divmod(c - 1, 26)
        s = chr(65 + r) + s
    return s


def direcciones():
    """Direcciones de las tablas (para el modulo de pruebas; LibreOffice no tiene ListObjects)."""
    n = len(columnas_riesgos())
    r_enc = FILA_ENC_RIESGOS
    ncols_esc = 3 + len(DIMENSIONES)
    return {
        "R_ENC": "B%d:%s%d" % (r_enc, col_letra(n), r_enc),
        "R_CUERPO": "B%d:%s%d" % (r_enc + 1, col_letra(n), r_enc + FILAS_RIESGOS),
        "D_ENC": "H5:O5", "D_CUERPO": "H6:O%d" % (5 + FILAS_DIM),
        "E_ENC": "Q5:%s5" % col_letra(16 + ncols_esc - 1), "E_CUERPO": "Q6:%s10" % col_letra(16 + ncols_esc - 1),
    }


def modulos_vba(test=False):
    code = open(os.path.join(AQUI, "MonteCarlo.bas"), encoding="ascii").read().split("\n", 1)[1]
    if test:
        prueba = open(os.path.join(AQUI, "pruebas", "PruebaInterna.bas"), encoding="ascii").read()
        for k, v in direcciones().items():
            prueba = prueba.replace("{{%s}}" % k, v)
        code += prueba
    mods = [{"name": "ThisWorkbook", "kind": "workbook", "code": "Option Explicit\n"}]
    for _, cn in HOJAS:
        mods.append({"name": cn, "kind": "worksheet", "code": "Option Explicit\n"})
    mods.append({"name": "MonteCarlo", "kind": "module", "code": code})
    return mods


def build(path, test=False):
    riesgos, mapeo = construir_riesgos(EJEMPLO)
    bin_path = os.path.join(os.path.dirname(path) or ".", "vbaProject.bin")
    with open(bin_path, "wb") as f:
        f.write(build_vba_project(modulos_vba(test)))

    wb = xlsxwriter.Workbook(path)
    wb.set_vba_name("ThisWorkbook")
    wb.add_vba_project(bin_path)
    wb.set_properties({"title": "Análisis cuantitativo de riesgos - Simulación Montecarlo",
                       "subject": "Riesgos de costo, plazo e ingeniería en obras de construcción",
                       "category": "Gestión de riesgos",
                       "keywords": "riesgos, Montecarlo, contingencia, construcción",
                       "comments": "Macro VBA incluida y abierta (módulo MonteCarlo). Idioma: español (Perú)."})
    wb.set_custom_property("Idioma", "es-PE")

    base = {"font_name": "Calibri", "font_size": 10, "valign": "vcenter"}

    def F(**kw):
        d = dict(base); d.update(kw)
        return wb.add_format(d)

    borde = {"border": 1, "border_color": BORDE}
    f_banda = F(bold=True, font_size=16, font_color=AMBAR, bg_color=NEGRO)
    f_banda_vacia = F(bg_color=NEGRO)
    f_sub = F(italic=True, font_color=GRIS_TXT)
    f_sec = F(bold=True, font_size=11, font_color=NEGRO, bottom=2, bottom_color=AMBAR)
    f_hdr = F(bold=True, font_color=AMBAR, bg_color=NEGRO, align="center", text_wrap=True, **borde)
    f_txt = F(text_wrap=True, valign="top", **borde)
    f_txt_alt = F(text_wrap=True, valign="top", bg_color=ALTERNA, **borde)
    f_txt_b = F(bold=True, text_wrap=True, valign="top", **borde)
    f_nota = F(italic=True, font_color=GRIS_TXT, text_wrap=True, valign="top")
    f_aviso = F(bold=True, bg_color=P50, font_color=NEGRO, text_wrap=True, **borde)
    f_lbl = F(bold=True, align="right")
    f_in = F(bg_color=ENTRADA, **borde)
    f_in_c = F(bg_color=ENTRADA, align="center", **borde)
    f_in_n0 = F(bg_color=ENTRADA, num_format="#,##0", **borde)
    f_in_n1 = F(bg_color=ENTRADA, num_format="#,##0.0", **borde)
    f_in_pct = F(bg_color=ENTRADA, num_format="0%", align="center", **borde)
    f_in_pct1 = F(bg_color=ENTRADA, num_format="0.0%", align="center", **borde)
    f_in_txt = F(bg_color=ENTRADA, text_wrap=True, valign="top", **borde)
    f_in_gen = F(bg_color=ENTRADA, num_format="#,##0.##", **borde)
    f_out = F(bg_color=SALIDA, font_color=NEGRO, **borde)
    f_out_n0 = F(bg_color=SALIDA, num_format="#,##0", **borde)
    f_estimado = F(bg_color=ENTRADA, align="center", border=2, border_color=AMBAR_PROF)
    f_placeholder = F(bold=True, font_size=13, font_color=AMBAR, bg_color=NEGRO)

    ws = {}
    for nombre, cn in HOJAS:
        s = wb.add_worksheet(nombre)
        s.set_vba_name(cn)
        s.hide_gridlines(2)
        s.set_column("A:A", 2)
        ws[nombre] = s

    def banda(s, texto, ncols, sub=None):
        s.set_row(1, 30)
        s.write(1, 1, texto, f_banda)
        for c in range(2, 1 + ncols):
            s.write_blank(1, c, None, f_banda_vacia)
        if sub:
            s.write(2, 1, sub, f_sub)

    # ============================================================== INICIO
    s = ws["INICIO"]
    s.set_tab_color(AMBAR)
    s.set_column("B:B", 24)
    s.set_column("C:C", 120)
    banda(s, "ANÁLISIS CUANTITATIVO DE RIESGOS — SIMULACIÓN MONTECARLO", 2,
          "Costo, plazo e ingeniería (diseño y campo) en obras de construcción · amenazas y oportunidades")
    s.merge_range(4, 1, 4, 2, "⚠ Los 32 riesgos R-01…R-32 traen ESTIMACIONES PRELIMINARES (ESTADO = «ESTIMADO – VALIDAR») "
                  "con costo base supuesto S/ 200 M y plazo 730 días. Valídelas con cada dueño de riesgo antes de usar los resultados.",
                  f_aviso)
    s.set_row(4, 32)
    fila = 6
    s.write(fila, 1, "HOJAS DEL LIBRO", f_sec); fila += 1
    for i, (h, d) in enumerate(C.HOJAS):
        s.write(fila, 1, h, f_txt_b)
        s.write(fila, 2, d, f_txt if i % 2 == 0 else f_txt_alt)
        fila += 1
    fila += 1
    s.write(fila, 1, "CÓMO USAR ESTA HERRAMIENTA", f_sec); fila += 1
    for i, p in enumerate(C.PASOS):
        s.write(fila, 1, "PASO %d" % (i + 1), f_txt_b)
        s.write(fila, 2, p, f_txt if i % 2 == 0 else f_txt_alt)
        s.set_row(fila, 30)
        fila += 1
    fila += 1
    s.write(fila, 1, "METODOLOGÍA (resumen)", f_sec); fila += 1
    for i, (t, d) in enumerate(C.METODO_RESUMEN):
        s.write(fila, 1, t, f_txt_b)
        s.write(fila, 2, d, f_txt if i % 2 == 0 else f_txt_alt)
        s.set_row(fila, 28)
        fila += 1
    s.write(fila, 1, "Detalle completo", f_txt_b)
    s.write(fila, 2, "Hoja TEORIA (13 secciones) y hoja GUIA (cómo elegir y llenar las distribuciones).", f_txt)
    fila += 2
    s.write(fila, 1, "LIMITACIONES", f_sec); fila += 1
    for t in C.LIMITACIONES:
        s.write(fila, 1, "•", F(align="right", bold=True, font_color=AMBAR_PROF))
        s.write(fila, 2, t, f_nota)
        s.set_row(fila, 28)
        fila += 1
    s.activate()

    # ============================================================== GUIA
    s = ws["GUIA"]
    s.set_tab_color(AMBAR_PROF)
    s.set_column("B:B", 30)
    s.set_column("C:C", 28)
    s.set_column("D:G", 20)
    s.set_column("H:H", 48)
    s.set_column("I:I", 48)
    banda(s, "GUÍA DE DISTRIBUCIONES PARA NO ESPECIALISTAS", 8,
          "Cómo describir la incertidumbre de cada impacto y qué poner en P1…P4. Fuente principal: Vose (caps. 1, 9 y 14).")
    fila = 4
    s.write(fila, 1, "1. ¿QUÉ ES UNA DISTRIBUCIÓN?", f_sec); fila += 1
    for t in C.GUIA_QUE_ES:
        s.merge_range(fila, 1, fila, 8, t, F(text_wrap=True, valign="top", bold=t.startswith("En cada")))
        s.set_row(fila, 30 if len(t) > 150 else 18)
        fila += 1
    fila += 1
    s.write(fila, 1, "2. ÁRBOL DE DECISIÓN: ¿QUÉ SÉ DEL IMPACTO?", f_sec); fila += 1
    s.merge_range(fila, 1, fila, 4, "SI USTED SABE…", f_hdr)
    s.merge_range(fila, 5, fila, 7, "USE", f_hdr); fila += 1
    for i, (a, b) in enumerate(C.GUIA_ARBOL):
        fm = f_txt if i % 2 == 0 else f_txt_alt
        s.merge_range(fila, 1, fila, 4, a, fm)
        s.merge_range(fila, 5, fila, 7, b, F(bold=True, bg_color=(ALTERNA if i % 2 else BLANCO), **borde))
        fila += 1
    fila += 1
    s.write(fila, 1, "3. CÓMO PREGUNTAR AL EXPERTO (3 preguntas)", f_sec); fila += 1
    for t in C.GUIA_PREGUNTAS:
        s.merge_range(fila, 1, fila, 8, t, F(text_wrap=True, valign="top"))
        s.set_row(fila, 18)
        fila += 1
    fila += 1
    s.write(fila, 1, "4. CATÁLOGO: QUÉ VA EN P1…P4 (tblDistribuciones, fuente de los menús y de la AYUDA)", f_sec); fila += 1
    f0 = fila
    datos = [[c[0], c[1], c[2], c[3], c[4], C.ayuda(c), c[5], c[6]] for c in C.CATALOGO]
    s.add_table(f0, 1, f0 + len(datos), 8, {
        "name": "tblDistribuciones", "style": "Table Style Light 1", "autofilter": False,
        "columns": [{"header": h, "header_format": f_hdr, "format": F(text_wrap=True, valign="top", **borde)}
                    for h in ["DISTRIBUCION", "P1", "P2", "P3", "P4", "AYUDA", "CUANDO USAR", "EJEMPLO"]],
        "data": datos})
    for i in range(len(datos)):
        s.set_row(f0 + 1 + i, 30)
    s.set_column("G:G", 36)
    fila = f0 + len(datos) + 2
    s.write(fila, 1, "5. ERRORES FRECUENTES", f_sec); fila += 1
    for t in C.GUIA_ERRORES:
        s.write(fila, 1, "✖", F(align="right", bold=True, font_color=ROJO))
        s.merge_range(fila, 2, fila, 8, t, F(text_wrap=True))
        fila += 1
    fila += 1
    s.write(fila, 1, "6. FORMA DE LAS DISTRIBUCIONES (densidad de probabilidad: más alta = más probable)", f_sec); fila += 1
    graf = graficos_guia()
    col_datos = 30  # columna AE en adelante: datos de los gráficos
    s.write(3, col_datos, "Datos de los gráficos de la sección 6 (generados al construir el libro)", f_sub)
    for gi, (titulo, ejex, series, tipo) in enumerate(graf):
        c0 = col_datos + gi * 4
        ch = wb.add_chart({"type": "scatter", "subtype": "smooth"} if tipo == "xy" else {"type": "column"})
        for si, (nom, xs, ys, color) in enumerate(series):
            cx = c0 if tipo == "xy" or si == 0 else c0
            s.write(4, c0, ejex, f_hdr)
            s.write(4, c0 + 1 + si, nom, f_hdr)
            for k, (x, y) in enumerate(zip(xs, ys)):
                s.write(5 + k, c0, x)
                s.write(5 + k, c0 + 1 + si, round(y, 8))
            n = len(xs)
            ref_x = ["GUIA", 5, c0, 4 + n, c0]
            ref_y = ["GUIA", 5, c0 + 1 + si, 4 + n, c0 + 1 + si]
            opts = {"name": nom, "categories": ref_x, "values": ref_y}
            if tipo == "xy":
                opts["line"] = {"color": color, "width": 2.25}
                opts["marker"] = {"type": "none"}
            else:
                opts["fill"] = {"color": color}
                opts["border"] = {"color": BORDE}
            ch.add_series(opts)
        ch.set_title({"name": titulo, "name_font": {"size": 11, "bold": True, "name": "Calibri"}})
        ch.set_x_axis({"name": ejex, "num_font": {"size": 9}, "major_gridlines": {"visible": False}})
        ch.set_y_axis({"name": "Densidad" if tipo == "xy" else "Probabilidad", "num_font": {"size": 9},
                       "major_gridlines": {"visible": True, "line": {"color": "#D9D9D9"}}})
        ch.set_legend({"position": "bottom"} if len(series) > 1 else {"none": True})
        ch.set_size({"width": 470, "height": 270})
        if tipo == "col":
            ch.set_chartarea({"border": {"none": True}})
        s.insert_chart(fila + (gi // 2) * 15, 1 + (gi % 2) * 4, ch, {"x_offset": 5, "y_offset": 5})
    fila += ((len(graf) + 1) // 2) * 15 + 1
    s.write(fila, 1, "7. LISTA DE LOS MENÚS DESPLEGABLES (nombre definido ListaDistribuciones)", f_sec); fila += 1
    l0 = fila
    for i, nom in enumerate(C.LISTA_MENU):
        s.write(fila, 1, nom, f_out); fila += 1
    wb.define_name("ListaDistribuciones", "=GUIA!$B$%d:$B$%d" % (l0 + 1, l0 + len(C.LISTA_MENU)))

    # ============================================================== PARAMETROS
    s = ws["PARAMETROS"]
    s.set_tab_color(AMBAR)
    cols = columnas_riesgos()
    banda(s, "ANÁLISIS DE RIESGOS — PARÁMETROS DE ENTRADA", 21,
          "Celdas ámbar claro = editables · gris = calculadas. Valide y luego corra la simulación con los botones.")
    cfg = [
        ("Costo base del proyecto (S/)", "CostoBase", COSTO_BASE, f_in_n0,
         "SUPUESTO (S/ 120–300 M): reemplácelo por el costo base del contrato."),
        ("Plazo base del proyecto (días)", "PlazoBase", PLAZO_BASE, f_in_n1,
         "SUPUESTO (24 meses): reemplácelo por el plazo contractual."),
        ("Número de iteraciones", "Iteraciones", 10000, f_in_n0, "Entero de 1,000 a 100,000 (10,000 recomendado)."),
        ("Semilla aleatoria", "Semilla", 12345, f_in_gen, "Número = resultados reproducibles; vacía = distintos en cada corrida."),
        ("Nivel de confianza", "NivelConfianza", 0.80, f_in_pct, "De 50 % a 95 %: define la reserva para contingencias (P80 usual)."),
        ("Reserva de gestión (% de la base)", "ReservaGestionPct", 0.0, f_in_pct1,
         "Trabajo no previsto; no se simula. Se aplica a las dimensiones con RESERVA_GESTION = SI."),
    ]
    s.set_column("B:B", 8)
    s.set_column("C:C", 48)
    s.write(3, 1, "CONFIGURACIÓN", f_sec)
    for i, (lbl, nombre, val, fm, nota) in enumerate(cfg):
        r = FILA_CFG - 1 + i
        s.merge_range(r, 1, r, 2, lbl, f_lbl)
        s.write(r, 3, val, fm)
        s.write(r, 4, nota, F(italic=True, font_color=GRIS_TXT))
        wb.define_name(nombre, "=PARAMETROS!$D$%d" % (r + 1))
    s.data_validation(FILA_CFG - 1, 3, FILA_CFG, 3, {"validate": "decimal", "criteria": ">=", "value": 0,
                      "error_title": "Valor no válido", "error_message": "Ingrese un número mayor o igual a 0 o deje la celda vacía."})
    s.data_validation(FILA_CFG + 1, 3, FILA_CFG + 1, 3, {"validate": "integer", "criteria": "between", "minimum": 1000,
                      "maximum": 100000, "error_title": "Iteraciones", "error_message": "Entero entre 1,000 y 100,000."})
    s.data_validation(FILA_CFG + 3, 3, FILA_CFG + 3, 3, {"validate": "decimal", "criteria": "between", "minimum": 0.5,
                      "maximum": 0.95, "error_title": "Nivel de confianza", "error_message": "Entre 50 % y 95 %."})
    s.data_validation(FILA_CFG + 4, 3, FILA_CFG + 4, 3, {"validate": "decimal", "criteria": "between", "minimum": 0,
                      "maximum": 1, "error_title": "Reserva de gestión", "error_message": "Entre 0 % y 100 %."})

    # tblDimensiones (columnas H..O, desde la fila 4)
    dc0 = 7
    s.write(3, dc0, "DIMENSIONES DE IMPACTO (tblDimensiones)", f_sec)
    enc_dim = ["CLAVE", "NOMBRE", "UNIDAD", "BASE", "FORMATO", "ACTIVA", "RESERVA_GESTION", "COLOR"]
    s.add_table(4, dc0, 4 + FILAS_DIM, dc0 + 7, {
        "name": "tblDimensiones", "style": "Table Style Light 1", "autofilter": False,
        "columns": [{"header": h, "header_format": f_hdr} for h in enc_dim]})
    for i in range(FILAS_DIM):
        r = 5 + i
        if i < len(DIMENSIONES):
            clave, nom, uni, bas, fmt, rg, color = DIMENSIONES[i]
            s.write(r, dc0, clave, f_in)
            s.write(r, dc0 + 1, nom, f_in)
            s.write(r, dc0 + 2, uni, f_in_c)
            if bas:
                s.write_formula(r, dc0 + 3, bas, F(bg_color=SALIDA, num_format=fmt, **borde),
                                COSTO_BASE if clave == "COSTO" else PLAZO_BASE)
            else:
                s.write_blank(r, dc0 + 3, None, f_in_n0)
            s.write(r, dc0 + 4, fmt, f_in_c)
            s.write(r, dc0 + 5, "SI", f_in_c)
            s.write(r, dc0 + 6, rg, f_in_c)
            s.write(r, dc0 + 7, color, f_in_c)
        else:
            for c in range(8):
                s.write_blank(r, dc0 + c, None, f_in)
    s.data_validation(5, dc0 + 5, 4 + FILAS_DIM, dc0 + 5, {"validate": "list", "source": ["SI", "NO"]})
    s.data_validation(5, dc0 + 6, 4 + FILAS_DIM, dc0 + 6, {"validate": "list", "source": ["SI", "NO"]})
    s.write(4 + FILAS_DIM + 1, dc0, "Filas libres para «＋ AGREGAR DIMENSIÓN». La CLAVE es ASCII, en mayúsculas y sin espacios.",
            F(italic=True, font_color=GRIS_TXT))

    # tblEscalas (columnas Q..W)
    ec0 = 16
    s.write(3, ec0, "ESCALAS DE LA MATRIZ P-I (tblEscalas)", f_sec)
    enc_esc = ["NIVEL", "DESCRIPCION", "PROB_MAX"] + ["IMP_" + d[0] for d in DIMENSIONES]
    s.add_table(4, ec0, 9, ec0 + len(enc_esc) - 1, {
        "name": "tblEscalas", "style": "Table Style Light 1", "autofilter": False,
        "columns": [{"header": h, "header_format": f_hdr} for h in enc_esc]})
    niveles = [(1, "Muy bajo", 0.10, 200000, 5, 100, 100), (2, "Bajo", 0.30, 600000, 15, 300, 300),
               (3, "Medio", 0.50, 1800000, 45, 900, 900), (4, "Alto", 0.70, 5400000, 120, 2700, 2700),
               (5, "Muy alto", 1.00, None, None, None, None)]
    for i, fila_n in enumerate(niveles):
        r = 5 + i
        s.write(r, ec0, fila_n[0], f_in_c)
        s.write(r, ec0 + 1, fila_n[1], f_in)
        s.write(r, ec0 + 2, fila_n[2], f_in_pct)
        for j, v in enumerate(fila_n[3:]):
            fm = f_in_n0
            if v is None:
                s.write_blank(r, ec0 + 3 + j, None, fm)
            else:
                s.write(r, ec0 + 3 + j, v, fm)
    s.write(10, ec0, "Umbral = valor máximo del nivel (razón ~3, Vose). Nivel 5 vacío = sin tope.", F(italic=True, font_color=GRIS_TXT))
    for c in range(ec0, ec0 + len(enc_esc)):
        s.set_column(c, c, 13)
    s.set_column(ec0 + 1, ec0 + 1, 11)

    # Botones (formas con macro; se asigna en el post-proceso del dibujo)
    s.set_row(11, 40)
    botones = [("▶ CORRER SIMULACIÓN", "EjecutarSimulacion", 220), ("✔ VALIDAR DATOS", "ValidarDatos", 170),
               ("✖ LIMPIAR RESULTADOS", "LimpiarResultados", 190), ("＋ AGREGAR DIMENSIÓN", "AgregarDimension", 190)]
    x = 4
    for texto, macro, ancho in botones:
        s.insert_textbox(11, 1, texto, {
            "width": ancho, "height": 38, "x_offset": x, "y_offset": 1,
            "font": {"bold": True, "color": AMBAR, "size": 11, "name": "Calibri"},
            "align": {"vertical": "middle", "horizontal": "center"},
            "fill": {"color": NEGRO}, "line": {"color": AMBAR_PROF, "width": 1.25},
            "description": macro})
        x += ancho + 14

    # tblRiesgos
    s.write(FILA_ENC_RIESGOS - 2, 1, "REGISTRO DE RIESGOS (tblRiesgos) — una fila por riesgo; la distribución vacía indica que "
            "el riesgo no afecta esa dimensión. Columnas AYUDA_ = qué poner en P1…P4.", f_sec)
    r0 = FILA_ENC_RIESGOS - 1
    col_fmt = {"ID": f_in_c, "NOMBRE DEL RIESGO": f_in_txt, "TIPO": f_in_c, "CATEGORIA": f_in_c, "CAUSA": f_in_txt,
               "DUENO DEL RIESGO": f_in, "ESTADO": f_in_c, "ACTIVO": f_in_c, "PROBABILIDAD": f_in_pct,
               "GRUPO_CORRELACION": f_in_c, "RHO_GRUPO": F(bg_color=ENTRADA, num_format="0.00", align="center", **borde),
               "ESTRATEGIA": f_in_c, "PROB_RESIDUAL": f_in_pct, "FACTOR_IMPACTO_RESIDUAL": F(bg_color=ENTRADA, num_format="0.00", align="center", **borde),
               "COSTO_RESPUESTA": f_in_n0, "NOTAS": f_in_txt}
    fmt_dim = {"COSTO": f_in_n0, "PLAZO": f_in_n1, "ING_DISENO": f_in_n0, "ING_CAMPO": f_in_n0}
    col_defs = []
    for h in cols:
        if h.startswith("AYUDA_"):
            k = h[6:]
            col_defs.append({"header": h, "header_format": f_hdr, "format": F(bg_color=SALIDA, text_wrap=True, font_size=9, **borde),
                             "formula": "=IFERROR(INDEX(tblDistribuciones[AYUDA],MATCH([@[DIST_%s]],tblDistribuciones[DISTRIBUCION],0)),\"\")" % k})
        elif h.startswith("DIST_"):
            col_defs.append({"header": h, "header_format": f_hdr, "format": f_in_c})
        elif re.match(r".*_P[1-4]$", h):
            col_defs.append({"header": h, "header_format": f_hdr, "format": fmt_dim[h.rsplit("_P", 1)[0]]})
        else:
            col_defs.append({"header": h, "header_format": f_hdr, "format": col_fmt[h]})
    c0 = 1
    s.add_table(r0, c0, r0 + FILAS_RIESGOS, c0 + len(cols) - 1, {
        "name": "tblRiesgos", "style": "Table Style Light 1", "columns": col_defs})
    ci = {h: c0 + i for i, h in enumerate(cols)}
    ayuda = {c[0]: C.ayuda(c) for c in C.CATALOGO}
    for i, rg in enumerate(riesgos):
        r = r0 + 1 + i
        vals = {"ID": rg["ID"], "NOMBRE DEL RIESGO": rg["NOMBRE"], "TIPO": rg["TIPO"], "CATEGORIA": rg["CATEGORIA"],
                "CAUSA": rg["CAUSA"], "DUENO DEL RIESGO": rg["DUENO"], "ESTADO": rg["ESTADO"], "ACTIVO": rg["ACTIVO"],
                "PROBABILIDAD": rg["PROB"], "GRUPO_CORRELACION": rg["GRUPO"], "RHO_GRUPO": rg["RHO"], "NOTAS": rg["NOTAS"]}
        for h, v in vals.items():
            fm = f_estimado if (h == "ESTADO" and "ESTIMADO" in rg["ESTADO"]) else col_fmt[h]
            if v in (None, ""):
                s.write_blank(r, ci[h], None, fm)
            else:
                s.write(r, ci[h], v, fm)
        for k, spec in rg["DIMS"].items():
            if spec:
                s.write(r, ci["DIST_" + k], spec[0], f_in_c)
                for j, v in enumerate(spec[1:]):
                    if v is not None:
                        s.write(r, ci["%s_P%d" % (k, j + 1)], v, fmt_dim[k])
            texto = ayuda.get(spec[0], "") if spec else ""
            s.write_formula(r, ci["AYUDA_" + k],
                            "=IFERROR(INDEX(tblDistribuciones[AYUDA],MATCH(tblRiesgos[[#This Row],[DIST_%s]],"
                            "tblDistribuciones[DISTRIBUCION],0)),\"\")" % k,
                            F(bg_color=SALIDA, text_wrap=True, font_size=9, **borde), texto)
        s.set_row(r, 45)
    # Validaciones de tblRiesgos
    f1, f2 = r0 + 1, r0 + FILAS_RIESGOS

    def lista(h, fuente, titulo, mensaje):
        s.data_validation(f1, ci[h], f2, ci[h], {"validate": "list", "source": fuente, "input_title": titulo,
                                                 "input_message": mensaje, "error_title": titulo,
                                                 "error_message": "Elija un valor de la lista."})
    lista("TIPO", ["AMENAZA", "OPORTUNIDAD"], "Tipo", "AMENAZA (perjudica) u OPORTUNIDAD (favorece).")
    lista("ACTIVO", ["SI", "NO"], "Activo", "SI = se simula; NO = se ignora.")
    lista("ESTADO", ["EJEMPLO", "ESTIMADO – VALIDAR", "CUANTIFICADO", "PENDIENTE DE CUANTIFICAR", "CERRADO"], "Estado",
          "Estado del riesgo en el registro.")
    lista("ESTRATEGIA", ["ESCALAR", "EVITAR", "TRANSFERIR", "MITIGAR", "ACEPTAR", "EXPLOTAR", "COMPARTIR", "MEJORAR"],
          "Estrategia (PMI)", "Amenazas: escalar, evitar, transferir, mitigar, aceptar. Oportunidades: escalar, explotar, compartir, mejorar, aceptar.")
    for d in DIMENSIONES:
        s.data_validation(f1, ci["DIST_" + d[0]], f2, ci["DIST_" + d[0]], {
            "validate": "list", "source": "=ListaDistribuciones", "input_title": "Distribución",
            "input_message": "Elija la distribución (vacío = no afecta). Vea la hoja GUIA.",
            "error_title": "Distribución", "error_message": "Elija una distribución de la lista."})
    for h, mx in (("PROBABILIDAD", 1), ("PROB_RESIDUAL", 1), ("FACTOR_IMPACTO_RESIDUAL", 1), ("RHO_GRUPO", 0.95)):
        s.data_validation(f1, ci[h], f2, ci[h], {"validate": "decimal", "criteria": "between", "minimum": 0, "maximum": mx,
                                                 "error_title": h, "error_message": "Ingrese un valor entre 0 y %s." % mx})
    s.data_validation(f1, ci["COSTO_RESPUESTA"], f2, ci["COSTO_RESPUESTA"], {"validate": "decimal", "criteria": ">=",
                      "value": 0, "error_title": "Costo de respuesta", "error_message": "Ingrese un número ≥ 0."})
    anchos = {"ID": 7, "NOMBRE DEL RIESGO": 60, "TIPO": 13, "CATEGORIA": 14, "CAUSA": 40, "DUENO DEL RIESGO": 14,
              "ESTADO": 20, "ACTIVO": 8, "PROBABILIDAD": 12, "GRUPO_CORRELACION": 17, "RHO_GRUPO": 10, "ESTRATEGIA": 13,
              "PROB_RESIDUAL": 11, "FACTOR_IMPACTO_RESIDUAL": 13, "COSTO_RESPUESTA": 13, "NOTAS": 50}
    for h in cols:
        w = anchos.get(h, 20 if h.startswith("AYUDA_") else (15 if h.startswith("DIST_") else 11))
        s.set_column(ci[h], ci[h], w)
    s.set_row(r0, 32)
    s.freeze_panes(r0 + 1, 3)
    # Guía de parámetros debajo de la tabla
    g0 = r0 + FILAS_RIESGOS + 3
    s.write(g0, 1, "GUÍA RÁPIDA DE PARÁMETROS (detalle en la hoja GUIA)", f_sec)
    s.write_row(g0 + 1, 1, ["", "DISTRIBUCIÓN", "P1", "P2", "P3", "P4"], f_hdr)
    for i, c in enumerate(C.CATALOGO):
        fm = f_txt if i % 2 == 0 else f_txt_alt
        s.write_row(g0 + 2 + i, 1, ["", c[0], c[1], c[2], c[3], c[4]], fm)

    # ============================================================== HOJAS DE SALIDA
    salidas = {"RESULTADOS": ("RESULTADOS", VERDE), "CURVA_S": ("CURVA S", AZUL), "TORNADO": ("TORNADO", ROJO),
               "RANGOS": ("RANGOS", P90), "MATRIZ_PI": ("MATRIZ PROBABILIDAD-IMPACTO", P50),
               "COMPARACION": ("COMPARACIÓN ANTES / DESPUÉS", P10), "SIMULACION": ("SIMULACIÓN", PANEL2)}
    for nombre, (titulo, color) in salidas.items():
        s = ws[nombre]
        s.set_tab_color(color)
        s.set_row(1, 26)
        s.write(1, 1, "%s — Presione ▶ CORRER SIMULACIÓN en la hoja PARAMETROS" % titulo, f_placeholder)
        for c in range(2, 13):
            s.write_blank(1, c, None, f_banda_vacia)
    ws["RANGOS"].freeze_panes(4, 3)
    ws["SIMULACION"].freeze_panes(4, 2)

    # ============================================================== TEORIA
    s = ws["TEORIA"]
    s.set_tab_color(NEGRO)
    s.set_column("B:B", 150)
    banda(s, "TEORÍA UTILIZADA EN ESTA HERRAMIENTA", 1,
          "Fuentes entre corchetes: ver sección 13. Fórmulas en texto legible.")
    fila = 4
    for titulo, parrafos in C.TEORIA:
        s.write(fila, 1, titulo, f_sec); fila += 1
        for p in parrafos:
            s.write(fila, 1, p, F(text_wrap=True, valign="top"))
            s.set_row(fila, 15 * max(1, math.ceil(len(p) / 160)))
            fila += 1
        fila += 1

    wb.close()
    os.remove(bin_path)
    asignar_macros_botones(path, [b[0] for b in botones], [b[1] for b in botones])
    return riesgos, mapeo


def asignar_macros_botones(path, textos, macros):
    """Asigna la macro (atributo macro de xdr:sp) y forma redondeada a los cuadros de texto de PARAMETROS."""
    tmp = path + ".tmp"
    with zipfile.ZipFile(path) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename.startswith("xl/drawings/drawing") and item.filename.endswith(".xml"):
                xml = data.decode("utf-8")
                cambios = 0
                for texto, macro in zip(textos, macros):
                    patron = re.compile(r'<xdr:sp macro="" textlink="">(?:(?!</xdr:sp>).)*?' + re.escape(texto), re.S)
                    m = patron.search(xml)
                    if m:
                        bloque = m.group(0).replace('<xdr:sp macro=""', '<xdr:sp macro="[0]!%s"' % macro, 1)
                        bloque = bloque.replace('prst="rect"', 'prst="roundRect"')
                        xml = xml[:m.start()] + bloque + xml[m.end():]
                        cambios += 1
                if cambios:
                    assert cambios == len(macros), "no se encontraron todos los botones"
                    data = xml.encode("utf-8")
            zout.writestr(item, data)
    os.replace(tmp, path)


if __name__ == "__main__":
    test = "--test" in sys.argv
    out = os.path.join(AQUI, "pruebas", "MonteCarlo_Prueba.xlsm") if test else os.path.join(AQUI, "MonteCarlo_Riesgos.xlsm")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out, test)
    print("OK ->", out)
