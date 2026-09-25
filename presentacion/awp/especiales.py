"""Láminas con diagramas a medida (no parametrizables como rejilla o proceso)."""
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN

from .diseno import (ALTO, ANCHO, AZUL, AZUL_CORP, AZUL_MEDIO, AZUL_PALIDO, AZUL_TINTE, BLANCO, BORDE,
                     BORDE_OSC, FONDO, GRIS, GRIS_MEDIO, GRIS_SUAVE, M, MONO, NARANJA, NARANJA_CLARO,
                     NARANJA_OSC, NARANJA_TINTE, NEGRO, TARJETA, TEXTO, UTIL, Y0, Y1, barra_nota, caja,
                     flecha, icono, icono_circulo, linea, numero_circulo, texto)


def agenda(d, etiqueta, titulo, modulos):
    """modulos = [(número, nombre, fase_o_None)]"""
    s = d.contenido(etiqueta, titulo)
    cols, gap = 4, 0.22
    filas = (len(modulos) + cols - 1) // cols
    w = (UTIL - gap * (cols - 1)) / cols
    h = (Y1 - Y0 - gap * (filas - 1)) / filas
    for i, (num, nom, fase) in enumerate(modulos):
        f, c = divmod(i, cols)
        x, y = M + c * (w + gap), Y0 + f * (h + gap)
        es_fase = fase is not None
        caja(s, x, y, w, h, relleno=NEGRO if es_fase else BLANCO, borde=None if es_fase else BORDE)
        texto(s, x + 0.25, y + 0.14, 0.9, h - 0.28, f"{num:02d}", tam=26, negrita=True, fuente=MONO,
              color=NARANJA, ancla=MSO_ANCHOR.MIDDLE)
        cuerpo = [[{"t": nom, "negrita": True, "color": BLANCO if es_fase else NEGRO}]]
        if fase:
            cuerpo.append([{"t": fase, "color": NARANJA_CLARO, "tam": 10.5}])
        texto(s, x + 1.2, y + 0.1, w - 1.35, h - 0.2, cuerpo, tam=13, ancla=MSO_ANCHOR.MIDDLE, interlineado=1.0)
    return s


def tres_procesos(d, etiqueta, titulo, procesos, nota=None):
    """Tres círculos superpuestos (AWP, IM, WFP) con descripción debajo."""
    s = d.contenido(etiqueta, titulo)
    dcir = 2.6
    solape = 0.45
    total = 3 * dcir - 2 * solape
    x0 = (ANCHO - total) / 2
    y = Y0 + 0.05
    for i, (sig, nombre, desc, col) in enumerate(procesos):
        x = x0 + i * (dcir - solape)
        caja(s, x, y, dcir, dcir, relleno=col, forma=MSO_SHAPE.OVAL, alfa=12)
        texto(s, x + 0.3, y + 0.75, dcir - 0.6, 0.55, sig, tam=26, negrita=True, color=BLANCO, fuente=MONO,
              alinear=PP_ALIGN.CENTER)
        texto(s, x + 0.55, y + 1.35, dcir - 1.1, 0.6, nombre, tam=11, color=BLANCO, alinear=PP_ALIGN.CENTER,
              interlineado=1.0)
    wcol = UTIL / 3
    for i, (sig, nombre, desc, col) in enumerate(procesos):
        x = M + i * wcol
        texto(s, x + 0.2, y + dcir + 0.3, wcol - 0.4, 1.2, desc, tam=13, color=TEXTO, alinear=PP_ALIGN.CENTER,
              interlineado=1.1)
    if nota:
        barra_nota(s, nota)
    return s


def jerarquia(d, etiqueta, titulo):
    s = d.contenido(etiqueta, titulo)

    def nodo(x, y, w, h, sigla, nombre, dato, relleno, ic, txt=BLANCO, sub=None):
        caja(s, x, y, w, h, relleno=relleno)
        icono(s, ic, x + 0.22, y + (h - 0.42) / 2, 0.42)
        texto(s, x + 0.85, y + 0.14, w - 1.0, 0.35, sigla, tam=18, negrita=True, color=txt, fuente=MONO)
        texto(s, x + 0.85, y + 0.48, w - 1.0, 0.25, nombre, tam=10.5, color=txt)
        texto(s, x + 0.85, y + 0.74, w - 1.0, 0.25, dato, tam=10.5, color=sub or txt, negrita=True)

    cx = ANCHO / 2
    w, h = 3.5, 1.08
    nodo(cx - w / 2, 1.95, w, h, "CWA", "Construction Work Area", "Área del terreno · nivel 2", NEGRO, "map_w",
         sub=NARANJA_CLARO)
    y2 = 3.55
    nodo(cx - w / 2, y2, w, h, "CWP", "Construction Work Package", "1 disciplina · < 40 000 HH · nivel 3",
         NARANJA, "helmet_w")
    xe = M + 0.15
    nodo(xe, y2, w, h, "EWP", "Engineering Work Package", "Planos, specs, lista de materiales", AZUL, "ruler_w",
         sub=AZUL_PALIDO)
    xp = ANCHO - M - 0.15 - w
    nodo(xp, y2, w, h, "PWP", "Procurement Work Package", "Materiales y equipos del CWP", AZUL_MEDIO, "truck_w")
    flecha(s, xe + w + 0.08, y2 + h / 2, cx - w / 2 - 0.1, y2 + h / 2, color=AZUL)
    flecha(s, xp - 0.08, y2 + h / 2, cx + w / 2 + 0.1, y2 + h / 2, color=AZUL_MEDIO)
    flecha(s, cx, 1.95 + h + 0.06, cx, y2 - 0.08, color=GRIS)
    y3 = 5.15
    wi, gi = 2.5, 0.25
    total = 3 * wi + 2 * gi
    x = cx - total / 2
    for i in range(3):
        caja(s, x, y3, wi, 0.95, relleno=BLANCO, borde=BORDE)
        icono(s, "clip_o", x + 0.2, y3 + 0.26, 0.42)
        texto(s, x + 0.8, y3 + 0.14, wi - 0.9, 0.35, f"IWP-0{i + 1}", tam=15, negrita=True, color=NEGRO, fuente=MONO)
        texto(s, x + 0.8, y3 + 0.52, wi - 0.9, 0.3, "1 cuadrilla · 1 semana", tam=10.5, color=GRIS)
        flecha(s, cx, y2 + h + 0.06, x + wi / 2, y3 - 0.08, color=GRIS, grosor=1.25)
        x += wi + gi
    texto(s, cx - total / 2, y3 + 1.12, total, 0.3,
          [[{"t": "Installation Work Package (IWP): ", "negrita": True, "color": NEGRO},
            {"t": "lo que recibe el capataz · nivel 5"}]], tam=11, color=GRIS, alinear=PP_ALIGN.CENTER)
    texto(s, cx + total / 2 + 0.3, y3 + 0.05, 2.7, 0.9,
          [[{"t": "Regla base", "negrita": True, "color": NARANJA}], "1 EWP = 1 PWP = 1 CWP"],
          tam=11, color=TEXTO, interlineado=1.1)
    return s


def regla_1a1(d, etiqueta, titulo):
    """Tres columnas alineadas EWP = PWP = CWP para tres disciplinas, con las excepciones."""
    s = d.contenido(etiqueta, titulo)
    disciplinas = ["Concreto", "Acero", "Tuberías"]
    cols = [("EWP", "Ingeniería", AZUL), ("PWP", "Compras", AZUL_MEDIO), ("CWP", "Construcción", NARANJA)]
    wcol, gap = 2.3, 0.75
    x0 = M
    y = Y0
    for j, (sig, area, col) in enumerate(cols):
        x = x0 + j * (wcol + gap)
        texto(s, x, y, wcol, 0.3, area.upper(), tam=10.5, negrita=True, color=col, espaciado=2,
              alinear=PP_ALIGN.CENTER)
        for i, disc in enumerate(disciplinas):
            yy = y + 0.45 + i * 1.3
            caja(s, x, yy, wcol, 1.0, relleno=col)
            texto(s, x, yy + 0.12, wcol, 0.4, f"{sig}-0{i + 1}", tam=17, negrita=True, color=BLANCO, fuente=MONO,
                  alinear=PP_ALIGN.CENTER)
            texto(s, x, yy + 0.55, wcol, 0.3, disc, tam=11.5, color=BLANCO, alinear=PP_ALIGN.CENTER)
            if j < 2:
                texto(s, x + wcol, yy, gap, 1.0, "=", tam=26, negrita=True, color=GRIS, alinear=PP_ALIGN.CENTER,
                      ancla=MSO_ANCHOR.MIDDLE)
    xl = x0 + 3 * wcol + 2 * gap + 0.45
    wl = ANCHO - M - xl
    caja(s, xl, Y0, wl, Y1 - Y0, relleno=NEGRO)
    texto(s, xl + 0.3, Y0 + 0.3, wl - 0.6, 0.3, "EXCEPCIONES ADMITIDAS", tam=10.5, negrita=True, color=NARANJA,
          espaciado=2)
    items = [("boxes_o", "Materiales a granel", "Bandejas, soportes o tubería se agrupan en un PWP común para varios CWP."),
             ("ruler_o", "Criterios de diseño", "Un EWP general puede servir a varios CWP."),
             ("link_o", "Interdisciplina", "Un CWP puede depender de varios EWP (civil, mecánica, estructuras).")]
    yy = Y0 + 0.8
    for ic, t, desc in items:
        icono(s, ic, xl + 0.3, yy + 0.05, 0.38)
        texto(s, xl + 0.85, yy, wl - 1.1, 1.2, [[{"t": t, "negrita": True, "color": BLANCO, "tam": 13}],
                                                [{"t": desc, "color": BORDE}]], tam=11.5, interlineado=1.05,
              espacio_despues=2)
        yy += 1.3
    return s


def codigo_wbs(d, etiqueta, titulo, nota):
    s = d.contenido(etiqueta, titulo)
    partes = [("WTF", "Planta", "Water Treatment Facility", AZUL),
              ("I", "Zona", "I = ISBL · O = OSBL", AZUL_CORP),
              ("12", "CWA", "Área de construcción", NARANJA_OSC),
              ("E4", "Disciplina", "E = movimiento de tierras · 4 = excavación", NARANJA),
              ("C05", "Paquete", "C = CWP (E, M, F, P = otros paquetes)", NARANJA_CLARO),
              ("14", "IWP", "Paquete de instalación, plano o spool", GRIS_MEDIO)]
    anchos = [1.55, 0.95, 1.2, 1.35, 1.55, 1.2]
    sep = 0.42
    total = sum(anchos) + sep * (len(anchos) - 1)
    x = (ANCHO - total) / 2
    y = Y0 + 0.1
    xs = []
    for i, ((cod, nom, desc, col), w) in enumerate(zip(partes, anchos)):
        caja(s, x, y, w, 1.1, relleno=col)
        texto(s, x, y, w, 1.1, cod, tam=34, negrita=True, fuente=MONO, color=BLANCO, alinear=PP_ALIGN.CENTER,
              ancla=MSO_ANCHOR.MIDDLE)
        xs.append((x, w, nom, desc, col))
        if i < len(partes) - 1:
            texto(s, x + w, y, sep, 1.1, "–", tam=30, negrita=True, color=GRIS, alinear=PP_ALIGN.CENTER,
                  ancla=MSO_ANCHOR.MIDDLE, fuente=MONO)
        x += w + sep
    # Rótulos alternados abajo
    for i, (x, w, nom, desc, col) in enumerate(xs):
        cx = x + w / 2
        yl = y + 1.1
        largo = 0.35 if i % 2 == 0 else 1.2
        linea(s, cx, yl, cx, yl + largo, color=col, grosor=1.5)
        wt = 2.6
        texto(s, cx - wt / 2, yl + largo + 0.05, wt, 0.9,
              [[{"t": nom, "negrita": True, "color": NEGRO, "tam": 13}], [{"t": desc, "color": GRIS}]], tam=11,
              alinear=PP_ALIGN.CENTER, interlineado=1.0)
    barra_nota(s, nota)
    return s


def gantt_liberacion(d, etiqueta, titulo, nota):
    """Plan de liberación: por disciplina, EWP → PWP → CWP en serie (fin a inicio), escalonados."""
    s = d.contenido(etiqueta, titulo)
    disc = ["Pilotes", "Concreto", "Acero", "Tuberías", "E & I", "Traceado", "Aislamiento"]
    meses = ["E", "F", "M", "A", "M", "J", "J", "A", "S", "O", "N", "D"]
    x0, wl = M + 1.6, UTIL - 1.6
    wm = wl / 12
    y = Y0
    for i, m in enumerate(meses):
        texto(s, x0 + i * wm, y, wm, 0.3, m, tam=10, color=GRIS, alinear=PP_ALIGN.CENTER, fuente=MONO)
    hr = 0.4
    yy = y + 0.4
    for i, dn in enumerate(disc):
        caja(s, M, yy, UTIL, hr, relleno=BLANCO if i % 2 == 0 else "F7F7F7")
        texto(s, M + 0.15, yy, 1.4, hr, dn, tam=11.5, negrita=True, color=NEGRO, ancla=MSO_ANCHOR.MIDDLE)
        ini = i * 1.0
        tramos = [("EWP", 2.0, AZUL), ("PWP", 1.5, AZUL_MEDIO), ("CWP", 2.0, NARANJA)]
        xx = ini
        for et, dur, col in tramos:
            if xx + dur > 12:
                dur = 12 - xx
            if dur <= 0:
                break
            caja(s, x0 + xx * wm + 0.02, yy + 0.07, dur * wm - 0.04, hr - 0.14, relleno=col)
            if dur >= 1:
                texto(s, x0 + xx * wm, yy + 0.07, dur * wm, hr - 0.14, et, tam=9.5, negrita=True, color=BLANCO,
                      fuente=MONO, alinear=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)
            xx += dur
        yy += hr + 0.04
    # Leyenda
    yl = yy + 0.1
    xl = M
    for et, desc, col in (("EWP", "Ingeniería: último plano IFC", AZUL), ("PWP", "Compras: último componente en obra", AZUL_MEDIO),
                          ("CWP", "Construcción del paquete", NARANJA)):
        caja(s, xl, yl + 0.06, 0.3, 0.2, relleno=col)
        texto(s, xl + 0.4, yl, 3.6, 0.32, [[{"t": et + " ", "negrita": True, "color": NEGRO}, {"t": desc}]],
              tam=11, color=GRIS, ancla=MSO_ANCHOR.MIDDLE)
        xl += 4.0
    barra_nota(s, nota)
    return s


def calendario(d, etiqueta, titulo, nota):
    s = d.contenido(etiqueta, titulo)
    cols = ["Semana pasada", "Semana 1", "Semana 2", "Semana 3"]
    filas = [("Tuberías", [("IWP-09", "hecho"), ("IWP-11", "act"), ("IWP-12", "sig"), ("IWP-14", "sig")]),
             ("Acero", [("IWP-05", "hecho"), ("IWP-07", "act"), ("IWP-08", "sig"), ("IWP-10", "sig")]),
             ("Eléctrico", [("IWP-13", "hecho"), ("IWP-15", "act"), ("IWP-19", "sig"), ("IWP-20", "sig")]),
             ("Concreto", [("IWP-21", "hecho"), ("IWP-22", "act"), ("IWP-24", "sig"), ("—", "vacio")])]
    x0 = M + 1.8
    wc = (UTIL - 1.8) / 4
    y = Y0
    for j, c in enumerate(cols):
        caja(s, x0 + j * wc + 0.05, y, wc - 0.1, 0.45, relleno=GRIS_MEDIO if j == 0 else NEGRO)
        texto(s, x0 + j * wc, y, wc, 0.45, c.upper(), tam=10.5, negrita=True, color=BLANCO, espaciado=1,
              alinear=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)
    hr = 0.62
    for i, (disc, celdas) in enumerate(filas):
        yy = y + 0.6 + i * (hr + 0.1)
        texto(s, M, yy, 1.7, hr, disc, tam=13, negrita=True, color=NEGRO, ancla=MSO_ANCHOR.MIDDLE)
        for j, (iwp, estado) in enumerate(celdas):
            if estado == "vacio":
                caja(s, x0 + j * wc + 0.05, yy, wc - 0.1, hr, borde=BORDE, guiones=True)
                texto(s, x0 + j * wc, yy, wc, hr, "Sin IWP libre: alerta", tam=10.5, color=GRIS,
                      alinear=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)
                continue
            rel = {"hecho": "E0E0E0", "act": NARANJA, "sig": NARANJA_TINTE}[estado]
            col = {"hecho": GRIS, "act": BLANCO, "sig": NARANJA_OSC}[estado]
            caja(s, x0 + j * wc + 0.05, yy, wc - 0.1, hr, relleno=rel)
            texto(s, x0 + j * wc, yy, wc, hr, iwp, tam=14, negrita=True, color=col, fuente=MONO,
                  alinear=PP_ALIGN.CENTER, ancla=MSO_ANCHOR.MIDDLE)
    barra_nota(s, nota)
    return s


def barras_tool_time(d, etiqueta, titulo):
    s = d.contenido(etiqueta, titulo)
    texto(s, M, 2.0, 3.2, 1.3, "37 %", tam=80, negrita=True, color=GRIS)
    texto(s, M, 3.35, 3.4, 0.6, [[{"t": "Proyectos tradicionales", "negrita": True, "color": NEGRO}],
                                 "3,7 h productivas por jornada de 10 h"], tam=12, color=GRIS)
    flecha(s, 3.95, 2.72, 4.95, 2.72, color=NARANJA, grosor=3)
    texto(s, 5.2, 2.0, 3.4, 1.3, "46 %", tam=80, negrita=True, color=NARANJA)
    texto(s, 5.2, 3.35, 3.4, 0.6, [[{"t": "Proyectos con AWP", "negrita": True, "color": NEGRO}],
                                  "4,6 h productivas por jornada de 10 h"], tam=12, color=GRIS)
    yb = 4.55
    texto(s, M, yb - 0.4, 6, 0.3, "JORNADA DE 10 HORAS", tam=10, negrita=True, color=GRIS, espaciado=2)
    wbar = 8.0
    for k, (etq, pct, col) in enumerate((("Tradicional", 0.37, GRIS), ("AWP", 0.46, NARANJA))):
        y = yb + k * 0.72
        texto(s, M, y, 1.3, 0.5, etq, tam=12, negrita=True, color=NEGRO, ancla=MSO_ANCHOR.MIDDLE)
        caja(s, M + 1.4, y, wbar * pct, 0.5, relleno=col)
        caja(s, M + 1.4 + wbar * pct, y, wbar * (1 - pct), 0.5, relleno="E0E0E0")
        texto(s, M + 1.55, y, 2, 0.5, f"{pct * 10:.1f} h".replace(".", ","), tam=12, negrita=True, color=BLANCO,
              ancla=MSO_ANCHOR.MIDDLE, fuente=MONO)
        texto(s, M + 1.4 + wbar * pct + 0.15, y, 3, 0.5, f"{(1 - pct) * 10:.1f} h sin herramientas".replace(".", ","),
              tam=11, color=GRIS, ancla=MSO_ANCHOR.MIDDLE)
    xc = 10.35
    caja(s, xc, 2.0, ANCHO - M - xc, 3.77, relleno=NEGRO)
    icono(s, "wrench_o", xc + 0.35, 2.35, 0.5)
    texto(s, xc + 0.35, 3.1, 1.95, 0.9, "+25 %", tam=40, negrita=True, color=NARANJA)
    texto(s, xc + 0.35, 3.95, 1.95, 0.8, "de productividad en campo (CII)", tam=13, color=BLANCO, interlineado=1.1)
    texto(s, xc + 0.35, 4.85, 1.95, 0.8, "Mídalo con estudios de tool time cada 2-3 meses", tam=11, color=BORDE,
          interlineado=1.1)
    return s


def organigrama(d, etiqueta, titulo):
    s = d.contenido(etiqueta, titulo)

    def nodo(x, y, w, h, t, desc, col, ic, oscuro=True):
        caja(s, x, y, w, h, relleno=col, borde=None if oscuro else BORDE)
        icono(s, f"{ic}_{'w' if oscuro else 'o'}", x + 0.2, y + 0.2, 0.38)
        texto(s, x + 0.7, y + 0.12, w - 0.85, h - 0.24,
              [[{"t": t, "negrita": True, "color": BLANCO if oscuro else NEGRO, "tam": 13}],
               [{"t": desc, "color": BLANCO if oscuro else GRIS}]], tam=10.5, interlineado=1.0,
              ancla=MSO_ANCHOR.MIDDLE)

    cx = ANCHO / 2
    w1 = 3.6
    nodo(cx - w1 / 2, Y0, w1, 0.85, "Propietario", "Respaldo corporativo y foco en la operación", NEGRO, "building")
    nodo(cx - w1 / 2, Y0 + 1.25, w1, 0.85, "EPC / EPCM", "Lidera el plan AWP y mantiene el POC", AZUL, "sitemap")
    flecha(s, cx, Y0 + 0.87, cx, Y0 + 1.23, color=GRIS)
    abajo = [("Ingeniería", "EWP alineados al POC", AZUL_MEDIO, "ruler"),
             ("Compras", "PWP y datos de proveedores", AZUL_MEDIO, "truck"),
             ("Construcción", "IWP y ejecución en campo", NARANJA, "helmet"),
             ("Puesta en marcha y operación", "SWP, TOP y prioridades de sistemas", NARANJA_OSC, "industry")]
    gap = 0.22
    w = (UTIL - gap * 3) / 4
    y3 = Y0 + 2.75
    ybus = Y0 + 2.45
    linea(s, M + w / 2, ybus, M + 3 * (w + gap) + w / 2, ybus, color=GRIS, grosor=1.5)
    linea(s, cx, Y0 + 2.12, cx, ybus, color=GRIS, grosor=1.5)
    for i, (t, desc, col, ic) in enumerate(abajo):
        x = M + i * (w + gap)
        flecha(s, x + w / 2, ybus, x + w / 2, y3 - 0.03, color=GRIS)
        nodo(x, y3, w, 1.0, t, desc, col, ic)
    # Champion transversal
    yc = y3 + 1.35
    caja(s, M, yc, UTIL, 0.72, relleno=NARANJA_TINTE, borde=NARANJA, guiones=True)
    icono(s, "star_o", M + 0.25, yc + 0.17, 0.38)
    texto(s, M + 0.8, yc, UTIL - 1.0, 0.72,
          [[{"t": "AWP Champion y equipo de soporte: ", "negrita": True, "color": NEGRO},
            {"t": "integran AWP con los procesos de la empresa, capacitan y impulsan la mejora continua."}]],
          tam=13, color=TEXTO, ancla=MSO_ANCHOR.MIDDLE)
    return s


def cierre(d, titulo, ideas, pregunta, siguiente):
    s = d.nueva(NEGRO)
    texto(s, M, 0.95, 10, 0.3, "EN RESUMEN", tam=12, negrita=True, color=NARANJA, espaciado=3)
    texto(s, M, 1.35, 11.5, 1.4, titulo, tam=40, negrita=True, color=BLANCO, interlineado=0.95, nombre="Título")
    w, gap, y = 3.83, 0.32, 3.2
    x = M
    for ic, t, dd in ideas:
        caja(s, x, y, w, 2.15, relleno=TARJETA, borde=BORDE_OSC)
        icono(s, ic, x + 0.35, y + 0.3, 0.5)
        texto(s, x + 0.35, y + 0.9, w - 0.6, 0.62, t, tam=15, negrita=True, color=BLANCO, ancla=MSO_ANCHOR.BOTTOM,
              interlineado=0.95)
        texto(s, x + 0.35, y + 1.6, w - 0.6, 0.35, dd, tam=12, color=BORDE)
        x += w + gap
    texto(s, M, 5.8, 6, 0.6, pregunta, tam=28, negrita=True, color=NARANJA_CLARO)
    texto(s, 6.9, 5.85, ANCHO - M - 6.9, 0.6, siguiente, tam=14, color=BORDE, alinear=PP_ALIGN.RIGHT,
          ancla=MSO_ANCHOR.MIDDLE)
    d.pie_de_pagina(s, oscuro=True, texto_pie="CIERRE")
    return s


def resumen_fases(d, etiqueta, titulo, fases, nota):
    """Cuatro columnas de fase con quién lidera y qué entrega; hilo conductor abajo."""
    s = d.contenido(etiqueta, titulo)
    gap = 0.25
    w = (UTIL - gap * 3) / 4
    h = Y1 - Y0 - 1.0
    for i, (fase, lider, entrega, col) in enumerate(fases):
        x = M + i * (w + gap)
        caja(s, x, Y0, w, 0.55, relleno=col)
        texto(s, x + 0.2, Y0, w - 0.4, 0.55, fase.upper(), tam=11, negrita=True, color=BLANCO, espaciado=1,
              ancla=MSO_ANCHOR.MIDDLE)
        caja(s, x, Y0 + 0.55, w, h - 0.55, relleno=BLANCO, borde=BORDE)
        texto(s, x + 0.2, Y0 + 0.75, w - 0.4, 0.25, "LIDERA", tam=9.5, negrita=True, color=GRIS, espaciado=1)
        texto(s, x + 0.2, Y0 + 1.0, w - 0.4, 0.62, lider, tam=14, negrita=True, color=NEGRO)
        texto(s, x + 0.2, Y0 + 1.75, w - 0.4, 0.25, "ENTREGA", tam=9.5, negrita=True, color=GRIS, espaciado=1)
        texto(s, x + 0.2, Y0 + 2.0, w - 0.4, h - 2.1, entrega, tam=12, color=TEXTO, interlineado=1.1)
        if i < 3:
            flecha(s, x + w + 0.03, Y0 + 0.27, x + w + gap - 0.03, Y0 + 0.27, color=GRIS)
    barra_nota(s, nota)
    return s
