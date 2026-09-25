"""Construye MonteCarlo_Riesgos.xlsm con la macro incrustada.

Uso:  python3 build_xlsm.py [--test]
  --test  agrega un modulo de pruebas (solo para verificacion, no para entrega)
"""

import os
import sys

import xlsxwriter

from vba_project import build_vba_project

AQUI = os.path.dirname(os.path.abspath(__file__))

SHEETS = [  # (nombre de pestana, CodeName)
    ("INICIO", "shInicio"),
    ("PARAMETROS", "shParam"),
    ("RESULTADOS", "shRes"),
    ("CURVA_S", "shCurva"),
    ("TORNADO", "shTornado"),
    ("RANGOS", "shRangos"),
    ("SIMULACION", "shSim"),
]

DISTS = ["TRIANGULAR", "PERT", "NORMAL", "UNIFORME", "LOGNORMAL", "EXPONENCIAL", "WEIBULL"]

GUIA = [
    ("TRIANGULAR", "P1 = Mínimo", "P2 = Moda (más probable)", "P3 = Máximo",
     "Cuando se conoce el mínimo, el valor más probable y el máximo."),
    ("PERT", "P1 = Mínimo", "P2 = Moda (más probable)", "P3 = Máximo",
     "Beta-PERT (λ = 4): como la triangular pero con más peso en la moda."),
    ("NORMAL", "P1 = Media", "P2 = Desviación estándar", "",
     "Variación simétrica. Puede dar valores negativos (oportunidades): no se truncan a 0."),
    ("UNIFORME", "P1 = Mínimo", "P2 = Máximo", "",
     "Cualquier valor entre el mínimo y el máximo es igual de probable."),
    ("LOGNORMAL", "P1 = Media", "P2 = Desviación estándar", "",
     "Sesgada a la derecha; media y desviación de la variable (no del logaritmo). Útil para costos."),
    ("EXPONENCIAL", "P1 = Media", "", "",
     "P1 es la MEDIA (λ = 1/P1). Para tiempos entre eventos."),
    ("WEIBULL", "P1 = Forma (k)", "P2 = Escala (λ)", "",
     "Flexible: fallas, durabilidad, duraciones."),
]

RIESGOS = [
    (1, "Ingeniería en desarrollo (90 entregables)", "SI", 1.0,
     "", None, None, None, "TRIANGULAR", 7, 14, 28, "Cuello de botella principal"),
    (2, "Alza de precios de materiales", "SI", 1.0,
     "NORMAL", 50000, 25000, None, "", None, None, None, "Media = 50k, Desv.Est. = 25k"),
    (3, "Condiciones geotécnicas imprevistas", "SI", 0.35,
     "PERT", 30000, 80000, 200000, "PERT", 10, 25, 60, "Afecta costo y plazo en el mismo evento"),
    (4, "Huelga o paralización", "SI", 0.20,
     "", None, None, None, "TRIANGULAR", 5, 15, 45, "Prob. 20%; impacto triangular"),
    (5, "Demora en permisos y aprobaciones", "SI", 1.0,
     "", None, None, None, "UNIFORME", 10, 40, None, "Cualquier valor entre 10 y 40 días"),
]

TABLE_FIRST_ROW = 11      # fila Excel del encabezado de tblRiesgos
TABLE_ROWS = 50           # filas de datos (12..61)

def vba_modules(test=False):
    code = open(os.path.join(AQUI, "MonteCarlo.bas"), encoding="ascii").read()
    code = code.split("\n", 1)[1]  # quitar 'Attribute VB_Name' (lo agrega el generador)
    if test:
        code += open(os.path.join(AQUI, "pruebas", "PruebaInterna.bas"), encoding="ascii").read()
    mods = [{"name": "ThisWorkbook", "kind": "workbook", "code": "Option Explicit\n"}]
    for _, cn in SHEETS:
        mods.append({"name": cn, "kind": "worksheet", "code": "Option Explicit\n"})
    mods.append({"name": "MonteCarlo", "kind": "module", "code": code})
    return mods


def build(path, test=False):
    bin_path = os.path.join(os.path.dirname(path) or ".", "vbaProject.bin")
    with open(bin_path, "wb") as f:
        f.write(build_vba_project(vba_modules(test)))

    wb = xlsxwriter.Workbook(path)
    wb.set_vba_name("ThisWorkbook")
    wb.add_vba_project(bin_path)
    wb.set_properties({"title": "Análisis de riesgos - Simulación Montecarlo",
                       "subject": "Riesgos de costo y plazo en obras de construcción",
                       "comments": "Macro VBA incluida (módulo MonteCarlo)."})

    VERDE = "#0F6E56"
    base = {"font_name": "Calibri", "font_size": 10, "valign": "vcenter"}

    def F(**kw):
        d = dict(base)
        d.update(kw)
        return wb.add_format(d)

    f_title = F(bold=True, font_size=16, font_color=VERDE)
    f_sub = F(italic=True, font_color="#5F5E5A")
    f_sec = F(bold=True, font_size=11, font_color=VERDE)
    f_hdr = F(bold=True, font_color="#FFFFFF", bg_color=VERDE, border=1, border_color="#D0CEC6",
              align="center", text_wrap=True)
    f_txt = F(border=1, border_color="#D0CEC6", text_wrap=True)
    f_txt_b = F(border=1, border_color="#D0CEC6", bold=True)
    f_txt_alt = F(border=1, border_color="#D0CEC6", text_wrap=True, bg_color="#F1EFE8")
    f_lbl = F(bold=True)
    f_note = F(italic=True, font_color="#5F5E5A", text_wrap=True)
    f_in = F(bg_color="#FFF2CC", border=1, border_color="#D0CEC6")
    f_in_num = F(bg_color="#FFF2CC", border=1, border_color="#D0CEC6", num_format="#,##0")
    f_in_num1 = F(bg_color="#FFF2CC", border=1, border_color="#D0CEC6", num_format="#,##0.0")
    f_in_int = F(bg_color="#FFF2CC", border=1, border_color="#D0CEC6", num_format="#,##0", bold=True)
    f_in_pct = F(bg_color="#FFF2CC", border=1, border_color="#D0CEC6", num_format="0%", align="center")
    f_in_c = F(bg_color="#FFF2CC", border=1, border_color="#D0CEC6", align="center")
    f_in_num_g = F(bg_color="#FFF2CC", border=1, border_color="#D0CEC6", num_format="#,##0.##")
    f_placeholder = F(bold=True, font_size=13, font_color=VERDE)

    ws = {}
    for name, cn in SHEETS:
        s = wb.add_worksheet(name)
        s.set_vba_name(cn)
        s.hide_gridlines(2)
        s.set_column("A:A", 2)
        ws[name] = s

    # ------------------------------------------------------------------ INICIO
    s = ws["INICIO"]
    s.set_tab_color(VERDE)
    s.set_column("B:B", 26)
    s.set_column("C:C", 110)
    s.write("B2", "ANÁLISIS DE RIESGOS — SIMULACIÓN MONTECARLO", f_title)
    s.write("B3", "Herramienta de gestión cuantitativa de riesgos (costo y plazo) para obras de construcción", f_sub)
    s.write("B5", "HOJAS DEL LIBRO", f_sec)
    hojas = [
        ("PARAMETROS", "Configuración (costo/plazo base, iteraciones, semilla) y tabla de riesgos tblRiesgos. "
                       "Celdas amarillas = editables. Aquí están los botones."),
        ("RESULTADOS", "Percentiles P0–P100 de costo y plazo, estadísticas y contingencias P50/P80/P90."),
        ("CURVA_S", "Curvas S (probabilidad acumulada) con marcas P50 y P80, e histogramas de frecuencia."),
        ("TORNADO", "Sensibilidad: correlación de Spearman, contribución a la varianza y swing por riesgo."),
        ("RANGOS", "Mínimo, P10, P25, P50, P75, P90, máximo y promedio de cada riesgo y de los totales."),
        ("SIMULACION", "Datos crudos de las primeras 5,000 iteraciones (totales y cada riesgo)."),
    ]
    for i, (h, d) in enumerate(hojas):
        s.write(5 + i, 1, h, f_txt_b)
        s.write(5 + i, 2, d, f_txt if i % 2 == 0 else f_txt_alt)

    s.write("B13", "CÓMO USAR ESTA HERRAMIENTA", f_sec)
    pasos = [
        "Abra el archivo y pulse «Habilitar contenido» (macros). Si Windows bloquea las macros: clic derecho "
        "en el archivo > Propiedades > marque «Desbloquear».",
        "En PARAMETROS ingrese (opcional) el costo y el plazo base del proyecto, el número de iteraciones "
        "(10,000 recomendado) y, si quiere resultados reproducibles, una semilla.",
        "Complete tblRiesgos: nombre, ACTIVO (SI/NO), probabilidad de ocurrencia y la distribución y "
        "parámetros del impacto en costo y/o en plazo. Deje vacía la dimensión que el riesgo no afecta.",
        "Pulse «✔ VALIDAR DATOS»: las celdas con errores se marcan en rojo y se listan en un mensaje.",
        "Pulse «▶ CORRER SIMULACIÓN». Las hojas de resultados se regeneran con tablas y gráficos.",
        "Use el P80 como contingencia recomendada (P90 si quiere ser conservador). "
        "«✖ LIMPIAR RESULTADOS» vacía las hojas de salida.",
    ]
    for i, p in enumerate(pasos):
        s.write(13 + i, 1, "PASO %d" % (i + 1), f_txt_b)
        s.write(13 + i, 2, p, f_txt if i % 2 == 0 else f_txt_alt)
        s.set_row(13 + i, 28)

    s.write("B21", "DISTRIBUCIONES DISPONIBLES", f_sec)
    s.write("B22", "DISTRIBUCIÓN", f_hdr)
    s.write("C22", "PARÁMETROS Y USO", f_hdr)
    for i, g in enumerate(GUIA):
        s.write(22 + i, 1, g[0], f_txt_b)
        pars = " | ".join(x for x in g[1:4] if x)
        s.write(22 + i, 2, pars + "  —  " + g[4], f_txt if i % 2 == 0 else f_txt_alt)

    s.write("B31", "MODELO Y SUPUESTOS", f_sec)
    notas = [
        "Cada riesgo ocurre con su PROBABILIDAD en cada iteración (vacía = 1 = siempre ocurre). Si ocurre, "
        "el impacto en costo y el impacto en plazo se muestrean en la MISMA iteración (el mismo evento dispara ambos).",
        "Costo total del impacto = suma de los impactos en costo; plazo total = suma de los impactos en plazo "
        "(supuesto conservador: los riesgos de plazo se suman, como si estuvieran en la ruta crítica).",
        "Los riesgos se muestrean de forma independiente (sin correlación entre riesgos).",
        "NORMAL puede producir valores negativos: se conservan (representan oportunidades). No se truncan a 0.",
        "Mín = Moda = Máx (TRIANGULAR/PERT) o Mín = Máx (UNIFORME) se tratan como un valor constante.",
        "Percentiles con interpolación lineal (mismo criterio que PERCENTIL.INC). Generador aleatorio: Rnd() de VBA.",
        "Swing (TORNADO) = media del total cuando el riesgo está en su 10% superior − media cuando está en su 10% inferior.",
    ]
    for i, n in enumerate(notas):
        s.write(31 + i, 1, "•", F(align="right", font_color=VERDE, bold=True))
        s.write(31 + i, 2, n, f_note)
        s.set_row(31 + i, 26)
    s.activate()

    # -------------------------------------------------------------- PARAMETROS
    s = ws["PARAMETROS"]
    s.set_tab_color("#FFC000")
    widths = {"B": 6, "C": 40, "D": 11, "E": 13, "F": 14, "G": 11, "H": 11, "I": 11,
              "J": 14, "K": 9, "L": 9, "M": 9, "N": 40}
    for col, w in widths.items():
        s.set_column("%s:%s" % (col, col), w)
    s.write("B2", "ANÁLISIS DE RIESGOS — PARÁMETROS DE ENTRADA", f_title)
    s.write("B3", "Complete la configuración y la tabla tblRiesgos (celdas amarillas) y pulse ▶ CORRER SIMULACIÓN.",
            f_sub)
    cfg = [
        (4, "Costo base del proyecto (S/)", None, f_in_num, "Opcional. Si se ingresa, RESULTADOS muestra el costo total (base + impacto)."),
        (5, "Plazo base del proyecto (días)", None, f_in_num1, "Opcional. Si se ingresa, RESULTADOS muestra el plazo total (base + impacto)."),
        (6, "Número de iteraciones", 10000, f_in_int, "Recomendado: 10,000  |  Mínimo: 1,000  |  Máximo: 100,000"),
        (7, "Semilla aleatoria", None, f_in_num_g, "Vacía = resultados distintos en cada corrida. Número = resultados reproducibles."),
    ]
    for r, lbl, val, fmt, note in cfg:
        s.merge_range(r, 1, r, 2, lbl, F(bold=True, align="right"))
        s.write(r, 3, val, fmt)
        s.write(r, 4, note, F(italic=True, font_color="#5F5E5A"))
    wb.define_name("CostoBase", "=PARAMETROS!$D$5")
    wb.define_name("PlazoBase", "=PARAMETROS!$D$6")
    wb.define_name("Iteraciones", "=PARAMETROS!$D$7")
    wb.define_name("Semilla", "=PARAMETROS!$D$8")
    s.data_validation("D5:D6", {"validate": "decimal", "criteria": ">=", "value": 0,
                                "error_title": "Valor no válido",
                                "error_message": "Ingrese un número mayor o igual a 0 (o deje la celda vacía)."})
    s.data_validation("D7", {"validate": "integer", "criteria": "between", "minimum": 1000, "maximum": 100000,
                             "input_title": "Iteraciones",
                             "input_message": "Entero entre 1,000 y 100,000.",
                             "error_title": "Valor no válido",
                             "error_message": "El número de iteraciones debe ser un entero entre 1,000 y 100,000."})
    s.data_validation("D8", {"validate": "integer", "criteria": "between", "minimum": 0, "maximum": 2147483647,
                             "ignore_blank": True, "error_title": "Semilla no válida",
                             "error_message": "Ingrese un entero positivo o deje la celda vacía."})

    s.set_row(8, 34)
    btn = {"height": 36, "font": {"bold": True}}
    s.insert_button("B9", dict(btn, macro="RunMonteCarlo", caption="▶ CORRER SIMULACIÓN",
                               width=230, x_offset=4, y_offset=0))
    s.insert_button("B9", dict(btn, macro="ValidarDatos", caption="✔ VALIDAR DATOS",
                               width=170, x_offset=248, y_offset=0))
    s.insert_button("B9", dict(btn, macro="ClearResults", caption="✖ LIMPIAR RESULTADOS",
                               width=190, x_offset=432, y_offset=0))

    headers = ["ID", "NOMBRE DEL RIESGO", "ACTIVO (SI/NO)", "PROBABILIDAD (0-1)",
               "DIST_COSTO", "C_P1", "C_P2", "C_P3",
               "DIST_PLAZO", "T_P1", "T_P2", "T_P3", "NOTAS"]
    col_fmt = [f_in_c, f_in, f_in_c, f_in_pct, f_in_c, f_in_num_g, f_in_num_g, f_in_num_g,
               f_in_c, f_in_num_g, f_in_num_g, f_in_num_g, f_in]
    data = []
    for rr in RIESGOS:
        data.append([("" if v is None else v) for v in rr])
    for _ in range(TABLE_ROWS - len(RIESGOS)):
        data.append([""] * len(headers))
    first = TABLE_FIRST_ROW - 1
    last = first + TABLE_ROWS
    s.write(first - 1, 1, "TABLA DE RIESGOS (tblRiesgos)  —  una fila por riesgo; deje vacía la distribución "
                          "de la dimensión que el riesgo no afecta", f_sec)
    s.add_table(first, 1, last, 13, {
        "name": "tblRiesgos",
        "style": "Table Style Light 15",
        "data": data,
        "columns": [{"header": h, "format": fm, "header_format": f_hdr} for h, fm in zip(headers, col_fmt)],
    })
    s.set_row(first, 32)
    r0, r1 = first + 1, last
    s.data_validation(r0, 3, r1, 3, {"validate": "list", "source": ["SI", "NO"]})
    s.data_validation(r0, 4, r1, 4, {"validate": "decimal", "criteria": "between", "minimum": 0, "maximum": 1,
                                     "error_title": "Probabilidad no válida",
                                     "error_message": "Ingrese un valor entre 0 y 1 (ej. 0.35 o 35%)."})
    for c in (5, 9):
        s.data_validation(r0, c, r1, c, {"validate": "list", "source": DISTS,
                                         "error_title": "Distribución no válida",
                                         "error_message": "Elija una distribución de la lista o deje la celda vacía."})
    for c in (6, 7, 8, 10, 11, 12):
        s.data_validation(r0, c, r1, c, {"validate": "decimal", "criteria": "between",
                                         "minimum": -1e15, "maximum": 1e15,
                                         "error_title": "Parámetro no válido", "error_message": "Ingrese un número."})

    g0 = last + 3
    s.write(g0, 1, "GUÍA DE PARÁMETROS POR DISTRIBUCIÓN", f_sec)
    s.merge_range(g0 + 1, 1, g0 + 1, 2, "DISTRIBUCIÓN", f_hdr)
    for k, h in enumerate(["P1", "P2", "P3"]):
        s.merge_range(g0 + 1, 3 + 3 * k, g0 + 1, 5 + 3 * k, h, f_hdr)
    s.write(g0 + 1, 12, "", f_hdr)
    s.write(g0 + 1, 13, "USO", f_hdr)
    for i, g in enumerate(GUIA):
        fm = f_txt if i % 2 == 0 else f_txt_alt
        row = g0 + 2 + i
        s.merge_range(row, 1, row, 2, g[0], f_txt_b)
        for k in range(3):
            s.merge_range(row, 3 + 3 * k, row, 5 + 3 * k, g[1 + k], fm)
        s.write(row, 12, "", fm)
        s.write(row, 13, g[4], fm)
        s.set_row(row, 30)
    s.freeze_panes(TABLE_FIRST_ROW, 0)

    # ------------------------------------------------------- HOJAS DE SALIDA
    for name, color in (("RESULTADOS", VERDE), ("CURVA_S", "#185FA5"), ("TORNADO", "#993C1D"),
                        ("RANGOS", "#854F0B"), ("SIMULACION", "#5F5E5A")):
        s = ws[name]
        s.set_tab_color(color)
        titulo = {"CURVA_S": "CURVA S", "SIMULACION": "SIMULACIÓN"}.get(name, name)
        s.write("B2", "%s — Presione ▶ CORRER SIMULACIÓN en la hoja PARAMETROS" % titulo, f_placeholder)
    ws["RANGOS"].freeze_panes(4, 2)
    ws["SIMULACION"].freeze_panes(4, 2)

    wb.close()
    os.remove(bin_path)


if __name__ == "__main__":
    test = "--test" in sys.argv
    out = os.path.join(AQUI, "pruebas", "MonteCarlo_Prueba.xlsm") if test else \
        os.path.join(AQUI, "MonteCarlo_Riesgos.xlsm")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    build(out, test)
    print("OK ->", out)
